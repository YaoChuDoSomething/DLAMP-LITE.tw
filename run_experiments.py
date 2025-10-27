# run_experiments.py
"""Script to run multiple prediction workflow experiments sequentially."""

import logging
from typing import Dict, Any

import hydra
from omegaconf import DictConfig

from predict import run_workflow

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="config", config_name="predict")
def main(cfg: DictConfig) -> None:
    """Runs a series of prediction workflow experiments.

    Args:
        cfg (DictConfig): The base configuration object loaded by Hydra.
    """
    experiments: Dict[str, Dict[str, Any]] = {
        "FANAPI": {
            "start_time": "2010-09-18 18:00",
            "end_time": "2010-09-20 00:00",
        },
        "MY2020": {
            "start_time": "2020-05-21 12:00",
            "end_time": "2020-05-22 12:00",
        },
        "MUIFA": {
            "start_time": "2022-09-11 00:00",
            "end_time": "2022-09-12 00:00",
        },
    }

    for exp_name, exp_config in experiments.items():
        log.info("=" * 80)
        log.info("Starting experiment: %s", exp_name)
        log.info("=" * 80)
        
        # Create a mutable copy of the config for each run
        run_cfg = cfg.copy()
        
        run_workflow(
            cfg=run_cfg,
            exp_code_prefix=exp_name,
            start_time=exp_config["start_time"],
            end_time=exp_config["end_time"],
        )
        
        log.info("=" * 80)
        log.info("Finished experiment: %s", exp_name)
        log.info("=" * 80)

if __name__ == "__main__":
    main()
