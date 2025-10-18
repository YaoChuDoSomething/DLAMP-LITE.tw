# predict.py
"""Main script for prediction, analysis, and visualization workflow.

This script orchestrates the entire process:
1.  Loads configuration using Hydra.
2.  Runs the model inference using PredictionRunner.
3.  Initializes data management, saving, and plotting components.
4.  Saves the detailed forecast output to NetCDF files.
5.  Generates and saves a 12-panel analysis plot for key forecast steps.

Usage:
    To run the prediction workflow, execute this script directly:
    $ python predict.py
"""

import logging
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

import hydra
from omegaconf import DictConfig, OmegaConf

from analysis.data_manager import AnalysisDataManager
from analysis.forecast_saver import ForecastSaver
from analysis.plotter import WeatherPlotter
from analysis.prediction import PredictionRunner

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig) -> None:
    """Runs the full prediction, saving, and plotting workflow.

    Args:
        cfg (DictConfig): The configuration object loaded by Hydra.

    Raises:
        IOError: If there's an error creating output directories or files.
        ValueError: If the configuration is invalid.
        ModuleNotFoundError: If a specified module for inference is not found.
    """
    try:
        OmegaConf.set_struct(cfg, True)
        out_dir: Path = Path(
            hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
        )
        log.info("Start workflow -> %s", out_dir)

        EXP_CODE = f"FANAPI_{cfg.inference.bdy_swap_method.name}"
        cfg.data.start_time = "2010-09-18 18:00"
        cfg.data.end_time = "2010-09-18 20:00"

        #EXP_CODE = f"MY2020_{cfg.inference.bdy_swap_method.name}"
        #cfg.data.start_time = "2020-05-21 12:00"
        #cfg.data.end_time = "2020-05-22 12:00"

        #EXP_CODE = f"MUIFA_{cfg.inference.bdy_swap_method.name}"
        #cfg.data.start_time = "2022-09-11 00:00"
        #cfg.data.end_time = "2022-09-11 03:00"

        case_end = datetime.strptime(cfg.data.end_time, cfg.data.format)
        case_start = datetime.strptime(cfg.data.start_time, cfg.data.format)
        case_duration = (case_end - case_start)
        cfg.data.use_Kth_hour_pred = 0
        cfg.plot.figure_columns = int(case_duration.total_seconds() // 3600) + 1

        eval_cases = [case_start]
        eval_cases.sort()
        log.info(f"cfg = {cfg}")

        # Step 1: Execute the model inference
        predictor: PredictionRunner = PredictionRunner(cfg)
        results = predictor.run()
        log.info("Model inference complete.")

        # Step 2: Initialize the data manager with prediction results
        adm: AnalysisDataManager = AnalysisDataManager(cfg, results)

        # Step 3: Save all forecast time steps to WRF-compatible NetCDF files
        saver: ForecastSaver = ForecastSaver(adm, out_dir / "netcdf_forecasts")
        saver.save_all_forecasts()
        log.info("All forecast steps saved to NetCDF files.")

        # Step 4: Generate and save analysis plots for specific time steps
        plotter: WeatherPlotter = WeatherPlotter(cfg, adm, out_dir / "plots")
        # Plot initial state (F000H) and hourly forecasts
        plot_steps: List[int] = [-1] + list(range(cfg.plot.figure_columns))
        log.info("Generating analysis plots for steps: %s", plot_steps)

        for step in plot_steps:
            try:
                # Ensure step is within the valid forecast range
                num_forecasts: int = results["output_upper"].shape[1]
                if step >= num_forecasts:
                    log.warning(
                        "Skipping plot for step F%03dH as it exceeds max.",
                        step + 1
                    )
                    continue

                path: Path = plotter.create_analysis_figure(step)
            except (ValueError, IndexError) as e:
                step_plus_one: int = step + 1
                step_str: str = (
                    "F000H" if step == -1 else f"F{step_plus_one:03d}H"
                )
                log.exception("Plot for step %s failed: %s", step_str, e)

        log.info("Workflow finished successfully.")

    except (IOError, ValueError, ModuleNotFoundError) as e:
        log.error("Workflow failed due to a critical error: %s", e)
        raise


if __name__ == "__main__":
    main()
