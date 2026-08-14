# FILE: analysis/prediction.py
"""Module for running the weather model inference.

This module provides the PredictionRunner class, which encapsulates the
logic for setting up and executing a model inference session based on a
Hydra configuration.
"""

import importlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import hydra
import numpy as np
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.inference import InferenceBase
from dlamp.utils import DataCompose, DataGenerator

logger = logging.getLogger(__name__)


class PredictionRunner:
    """Handles the setup and execution of the model inference process.

    This class reads the configuration, initializes the appropriate
    inference engine (either from a checkpoint or ONNX), runs the
    prediction, and returns the results in memory.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        eval_cases (List[datetime]): A list of timestamps for evaluation.
        infer_machine (InferenceBase): The instantiated inference engine.
    """

    def __init__(self, cfg: DictConfig):
        """Initializes the PredictionRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object that defines
                the model, data, and inference settings.
        """
        self.cfg = cfg
        self.eval_cases = [datetime.strptime(cfg.data.start_time, cfg.data.format).replace(tzinfo=UTC)]
        self.infer_machine: InferenceBase = self._setup_inference_machine()

    def _setup_inference_machine(self) -> InferenceBase:
        """Sets up the inference engine based on the configuration.

        Dynamically imports and instantiates the correct inference class
        (e.g., 'BatchInferenceCkpt' or 'BatchInferenceOnnx').

        Raises:
            ValueError: If the 'infer_type' in the config is not supported.

        Returns:
            InferenceBase: An initialized instance of the inference engine.
        """
        infer_type: str = self.cfg.inference.infer_type
        INFERENCE_CLASSES = {
            "ckpt": ("inference.batch_inference_ckpt", "BatchInferenceCkpt"),
            "onnx": ("inference.batch_inference_onnx", "BatchInferenceOnnx"),
        }

        if infer_type not in INFERENCE_CLASSES:
            raise ValueError(f"Unsupported inference type: {infer_type}")

        module_name, class_name = INFERENCE_CLASSES[infer_type]

        try:
            module = importlib.import_module(module_name)
            infer_class: type[InferenceBase] = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error("Failed to load inference class: %s", e)
            raise

        return infer_class(self.cfg, self.eval_cases)

    def run(self) -> dict[str, Any]:
        """Executes the full inference workflow.

        This method runs the model prediction and then generates the
        corresponding latitude and longitude grids. It returns all results
        as a dictionary, avoiding file I/O for intermediate data.

        Returns:
            Dict[str, Any]: A dictionary containing the prediction results,
                including:
                - 'output_upper' (np.ndarray): Upper-air variables.
                - 'output_surface' (np.ndarray): Surface variables.
                - 'lat' (np.ndarray): Latitude grid.
                - 'lon' (np.ndarray): Longitude grid.
                - 'start_time' (datetime): The forecast start time.
        """
        logger.info("Starting model inference...")
        self.infer_machine.infer(bdy_swap_method=self.cfg.inference.bdy_swap_method)
        logger.info("Inference complete.")

        # Prepare latitude and longitude grids
        data_gnrt: DataGenerator = self.infer_machine.data_manager.data_gnrt
        dc_lat: DataCompose
        dc_lon: DataCompose
        dc_mask: DataCompose
        dc_lat, dc_lon, dc_mask = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"], "MASK": ["NoRule"]})
        start_time: datetime = datetime.strptime(self.cfg.data.start_time, self.cfg.data.format).replace(
            tzinfo=UTC
        )
        lat: np.ndarray = data_gnrt.yield_data(start_time, dc_lat)
        lon: np.ndarray = data_gnrt.yield_data(start_time, dc_lon)
        mask: np.ndarray = data_gnrt.yield_data(start_time, dc_mask)

        return {
            "output_upper": self.infer_machine.output_upper,
            "output_surface": self.infer_machine.output_surface,
            "lat": lat,
            "lon": lon,
            "mask": mask,
            "start_time": start_time,
        }


@hydra.main(
    version_base=None,
    config_path=str(REPO_ROOT / "config"),
    config_name="predict",
)
def main(cfg: DictConfig) -> None:
    """Runs the full prediction, saving, and plotting workflow.

    This is the ``dlamp-predict`` console-script entry point.  It
    performs model inference (``PredictionRunner``), writes WRF-compatible
    NetCDF forecasts, and generates analysis plots.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/predict.yaml``.

    Raises:
        IOError: If there's an error creating output directories or files.
        ValueError: If the configuration is invalid.
        ModuleNotFoundError: If a specified module for inference is not found.
    """
    from dlamp.analysis.data_manager import AnalysisDataManager
    from dlamp.analysis.forecast_saver import ForecastSaver
    from dlamp.analysis.plotter import WeatherPlotter
    from dlamp.runtime_config import RuntimeConfig
    from dlamp.standardizer import get_standardizer

    try:
        OmegaConf.set_struct(cfg, True)
        out_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
        logger.info("Start workflow -> %s", out_dir)
        print("cfg = ", cfg)

        # Build runtime config eagerly (validates model code paths)
        runtime_config = RuntimeConfig.from_env()
        # Construct standardizer to load stats + data_list once
        get_standardizer(runtime_config)
        logger.info("Runtime config and standardizer initialized.")

        # Step 1: Execute the model inference
        predictor: PredictionRunner = PredictionRunner(cfg)
        results = predictor.run()
        logger.info("Model inference complete.")

        # Step 2: Initialize the data manager with prediction results
        adm: AnalysisDataManager = AnalysisDataManager(cfg, results)

        # Step 3: Save all forecast time steps to WRF-compatible NetCDF files
        saver: ForecastSaver = ForecastSaver(adm, out_dir / "netcdf_forecasts")
        saver.save_all_forecasts()
        logger.info("All forecast steps saved to NetCDF files.")

        # Step 4: Generate and save analysis plots for specific time steps
        plotter: WeatherPlotter = WeatherPlotter(cfg, adm, out_dir / "plots")
        # Plot initial state (F000H) and hourly forecasts
        plot_steps: list[int] = [-1] + list(range(cfg.plot.figure_columns))
        logger.info("Generating analysis plots for steps: %s", plot_steps)

        for step in plot_steps:
            try:
                # Ensure step is within the valid forecast range
                num_forecasts: int = results["output_upper"].shape[1]
                if step >= num_forecasts:
                    logger.warning(
                        "Skipping plot for step F%03dH as it exceeds max.",
                        step + 1,
                    )
                    continue

                plotter.create_analysis_figure(step)
            except (ValueError, IndexError):
                step_plus_one: int = step + 1
                step_str: str = "F000H" if step == -1 else f"F{step_plus_one:03d}H"
                logger.exception("Plot for step %s failed", step_str)

        logger.info("Workflow finished successfully.")

    except (OSError, ValueError, ModuleNotFoundError) as e:
        logger.error("Workflow failed due to a critical error: %s", e)
        raise


if __name__ == "__main__":
    main()
