"""Entrypoint for DLAMP one-way downscaling inference workflow.

Performs forward-only auto-regression — no ground-truth boundary values
are re-injected during the prediction loop.  This is equivalent to
``predict.py`` but explicitly documents the "no-feedback" contract.

Usage::

    python predict_dscale.py
    python predict_dscale.py data.start_time="2024-07-01 00:00"
    python predict_dscale.py inference=pangu_rwrf_ckpt
    python predict_dscale.py --cfg job   # dry-run

Environment variables::

    DLAMP_EXP_CODE      Model version code (e.g. "20250729")
    DLAMP_DATA_SOURCE   Source tag (default "OP_ERA5")
    DLAMP_DATA_PATH     Root path to raw NetCDF data

Raises:
    ValueError: If the configuration is invalid or inference type is
        unsupported.
    ModuleNotFoundError: If the specified inference engine module cannot
        be imported.
    IOError: If output directories or files cannot be created.
"""

import logging
from pathlib import Path
from typing import List

import hydra
from omegaconf import DictConfig, OmegaConf

from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.forecast_saver import ForecastSaver
from dlamp.analysis.plotter import WeatherPlotter
from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import get_standardizer
from dlamp.workflows import PredictDscaleRunner

log = logging.getLogger(__name__)

_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")


@hydra.main(
    version_base=None,
    config_path=_HYDRA_CONFIG_DIR,
    config_name="predict_dscale",
)
def main(cfg: DictConfig) -> None:
    """Runs the one-way downscaling inference, saving, and plotting workflow.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/predict_dscale.yaml``.  The key difference from
            ``predict.yaml`` is that ``inference.bdy_swap_method`` is
            ``null`` by default.

    Raises:
        ValueError: If the configuration is invalid.
        ModuleNotFoundError: If the inference engine module is missing.
        IOError: If output files cannot be written.
    """
    try:
        OmegaConf.set_struct(cfg, True)
        out_dir = Path(
            hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
        )
        log.info("predict_dscale workflow → %s", out_dir)

        runtime_config = RuntimeConfig.from_env()
        get_standardizer(runtime_config)
        log.info("Runtime config and standardizer initialized.")

        # Step 1: One-way downscaling inference (no boundary feedback)
        runner = PredictDscaleRunner(cfg)
        results = runner.run()
        log.info("One-way downscaling inference complete.")

        # Step 2: Package results for saving / plotting
        adm = AnalysisDataManager(cfg, results)

        # Step 3: Save forecast NetCDF files
        saver = ForecastSaver(adm, out_dir / "netcdf_forecasts")
        saver.save_all_forecasts()
        log.info("All forecast steps saved to NetCDF.")

        # Step 4: Generate analysis plots
        plotter = WeatherPlotter(cfg, adm, out_dir / "plots")
        plot_steps: List[int] = [-1] + list(range(cfg.plot.figure_columns))
        log.info("Generating plots for steps: %s", plot_steps)

        for step in plot_steps:
            num_forecasts: int = results["output_upper"].shape[1]
            if step >= num_forecasts:
                log.warning(
                    "Skipping plot for step F%03dH — exceeds max.", step + 1
                )
                continue
            try:
                plotter.create_analysis_figure(step)
            except (ValueError, IndexError) as exc:
                step_str = "F000H" if step == -1 else f"F{step + 1:03d}H"
                log.exception("Plot for step %s failed: %s", step_str, exc)

        log.info("predict_dscale workflow finished successfully.")

    except (IOError, ValueError, ModuleNotFoundError) as exc:
        log.error("predict_dscale workflow failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
