"""Entrypoint for the DLAMP data-preparation (constant-mask generation) workflow.

Generates land-sea and topography mask ``.npy`` artefacts required by
the training and inference pipelines.  The mask-generation method is
selected by ``cfg.data_prep.method`` (default: ``extract_from_nc``).

Usage::

    python data_prep.py
    python data_prep.py data_prep.method=gen_tw_cn_terrain
    python data_prep.py --cfg job   # dry-run, prints resolved config

Environment variables (via ``RuntimeConfig``)::

    DLAMP_EXP_CODE      Model version, e.g. "20250729" (default "20250627")
    DLAMP_DATA_SOURCE   Source tag, default "OP_ERA5"
    DLAMP_DATA_PATH     Root path to raw NetCDF data

Raises:
    ValueError: If ``data_prep.method`` is not a supported mask source.
    FileNotFoundError: If the required source file cannot be located.
"""

import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import get_standardizer
from dlamp.workflows import DataPrepRunner

log = logging.getLogger(__name__)

_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")


@hydra.main(
    version_base=None,
    config_path=_HYDRA_CONFIG_DIR,
    config_name="data_prep",
)
def main(cfg: DictConfig) -> None:
    """Runs the data-preparation (constant-mask generation) workflow.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/data_prep.yaml``.  Must contain:
            - ``data_prep.method`` (str): One of ``extract_from_nc``,
              ``gen_tw_cn_terrain``, or ``gen_tw_only_terrain``.

    Raises:
        ValueError: If ``data_prep.method`` is not supported.
        FileNotFoundError: If the required source file is missing.
    """
    OmegaConf.set_struct(cfg, True)
    out_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    log.info("data_prep workflow → %s", out_dir)

    runtime_config = RuntimeConfig.from_env()
    get_standardizer(runtime_config)
    log.info("Runtime config and standardizer initialized.")

    runner = DataPrepRunner(cfg)
    summary = runner.run()

    log.info(
        "data_prep complete: method=%s, artifacts=%s",
        summary["method"],
        summary["artifacts"],
    )


if __name__ == "__main__":
    main()
