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
from analysis.video_creator import create_animation 

log = logging.getLogger(__name__)


def run_workflow(cfg: DictConfig, exp_code_prefix: str, start_time: str, end_time: str) -> None:
    """Runs the full prediction, saving, and plotting workflow for a single experiment.

    Args:
        cfg (DictConfig): The configuration object.
        exp_code_prefix (str): The prefix for the experiment code (e.g., "FANAPI").
        start_time (str): The start time for the case in "YYYY-MM-DD HH:MM" format.
        end_time (str): The end time for the case in "YYYY-MM-DD HH:MM" format.

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

        EXP_CODE = f"{exp_code_prefix}_{cfg.inference.bdy_swap_method.name}"
        cfg.data.start_time = start_time
        cfg.data.end_time = end_time

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
        saver: ForecastSaver = ForecastSaver(
            adm, out_dir / "netcdf_forecasts", exp_code=EXP_CODE
        )
        saver.save_all_forecasts()
        log.info("All forecast steps saved to NetCDF files.")

        # Step 4: Generate and save analysis plots for specific time steps
        plotter: WeatherPlotter = WeatherPlotter(
            cfg, adm, out_dir / "plots", exp_code=EXP_CODE
        )
        # Plot initial state (F000H) and hourly forecasts
        plot_steps: List[int] = [-1] + list(range(cfg.plot.figure_columns))
        log.info("Generating analysis plots for steps: %s", plot_steps)

        generated_plots: List[Path] = []
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
                generated_plots.append(path)
            except (ValueError, IndexError) as e:
                step_plus_one: int = step + 1
                step_str: str = (
                    "F000H" if step == -1 else f"F{step_plus_one:03d}H"
                )
                log.exception("Plot for step %s failed: %s", step_str, e)

        log.info("Generating full stamps plots for steps: %s", plot_steps)

        generated_fc_stamps: List[Path] = []
        generated_gt_stamps: List[Path] = []
        for step in plot_steps:
            try:
                num_forecasts: int = results["output_upper"].shape[1]
                if step >= num_forecasts:
                    log.warning(
                        "Skipping full stamps plot for step F%03dH as it exceeds max.",
                        step + 1
                    )
                    continue
                fc_stamps_path, gt_stamps_path = plotter.create_full_stamps_plots(step)
                generated_fc_stamps.append(fc_stamps_path)
                generated_gt_stamps.append(gt_stamps_path)
            except (ValueError, IndexError) as e:
                step_plus_one: int = step + 1
                step_str: str = (
                    "F000H" if step == -1 else f"F{step_plus_one:03d}H"
                )
                log.exception("Full stamps plot for step %s failed: %s", step_str, e)

        # Step 5: Create an animation from the generated plots
        video_filename = f"{EXP_CODE}_{case_start.strftime('%Y%m%d_%H%M')}.mp4"
        video_path = out_dir / "plots" / video_filename
        fc_video_path = out_dir / "plots" / f"fc_{video_filename}"
        gt_video_path = out_dir / "plots" / f"gt_{video_filename}"
        create_animation(generated_plots, video_path, framerate=1)
        create_animation(generated_fc_stamps, fc_video_path, framerate=1)
        create_animation(generated_gt_stamps, gt_video_path, framerate=1)

        log.info("Workflow finished successfully.")

    except (IOError, ValueError, ModuleNotFoundError) as e:
        log.error("Workflow failed due to a critical error: %s", e)
        raise


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
    # Default experiment
    exp_code_prefix = "FANAPI"
    start_time = "2010-09-18 18:00"
    end_time = "2010-09-18 20:00"
    run_workflow(cfg, exp_code_prefix, start_time, end_time)



if __name__ == "__main__":
    main()
