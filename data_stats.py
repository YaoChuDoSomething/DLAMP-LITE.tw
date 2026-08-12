"""Entrypoint for the DLAMP z-score standardization-statistics workflow.

Computes per-variable mean and standard deviation from a random sample
of raw NetCDF data and writes the results to the standardization JSON
file referenced by ``RuntimeConfig``.  If a variable already has stats
the computation is skipped so the script is safe to re-run.

Usage::

    python data_stats.py
    python data_stats.py stats.start_time="2021-01-01 00:00" \\
                         stats.end_time="2022-12-31 00:00"
    python data_stats.py --cfg job   # dry-run

Environment variables::

    DLAMP_EXP_CODE      Model version; selects which JSON file to write
    DLAMP_DATA_SOURCE   Source tag (default "OP_ERA5")
    DLAMP_DATA_PATH     Root path to raw NetCDF data

Raises:
    RuntimeConfigError: If env-var model code mismatches an existing JSON.
"""

import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import get_standardizer
from dlamp.workflows import DataStatsRunner

log = logging.getLogger(__name__)

_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")


@hydra.main(
    version_base=None,
    config_path=_HYDRA_CONFIG_DIR,
    config_name="data_stats",
)
def main(cfg: DictConfig) -> None:
    """Runs the z-score standardization-statistics computation workflow.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/data_stats.yaml``.  Must contain a ``stats`` group
            with ``start_time``, ``end_time``, ``sample_size``, and
            ``num_criteria`` keys.

    Raises:
        ValueError: If the datetime strings in the config are malformed.
    """
    OmegaConf.set_struct(cfg, True)
    out_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    log.info("data_stats workflow → %s", out_dir)

    runtime_config = RuntimeConfig.from_env()
    get_standardizer(runtime_config)
    log.info("Runtime config and standardizer initialized.")

    runner = DataStatsRunner(cfg, runtime_config)
    summary = runner.run()

    log.info(
        "data_stats complete: json=%s (window %s → %s)",
        summary["standardization_path"],
        summary["start_time"],
        summary["end_time"],
    )


if __name__ == "__main__":
    main()
