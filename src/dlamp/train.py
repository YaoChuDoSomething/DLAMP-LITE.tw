"""Model training entrypoint.

Exposes the Hydra-wrapped ``main`` used by the ``dlamp-train`` console
script.  The configuration root is anchored to the repository root via
``dlamp.const.REPO_ROOT`` so it is independent of the calling working
directory.
"""

import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.managers import DataManager
from dlamp.models import get_builder
from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import get_standardizer
from dlamp.utils import DataCompose

log = logging.getLogger(__name__)


@hydra.main(
    version_base=None,
    config_path=str(REPO_ROOT / "config"),
    config_name="train_pangu",
)
def main(cfg: DictConfig) -> None:
    """Runs the model training workflow for Pangu (or diffusion) models.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/train_pangu.yaml`` (override with ``--config-name``).

    Raises:
        RuntimeConfigError: If ``DLAMP_EXP_CODE`` has no matching
            standardization or data config files.
    """
    hydra_oup_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    log.info(f"Working directory: {Path.cwd()}")
    log.info(f"Output directory: {hydra_oup_dir}")

    # lightning ddp strategy doesn't need manual seed
    # https://github.com/Lightning-AI/pytorch-lightning/issues/12986
    # seed_everything(1000)

    # Build runtime config eagerly (validates model code paths)
    runtime_config = RuntimeConfig.from_env()
    # Construct standardizer to load stats + data_list once
    get_standardizer(runtime_config)
    log.info("Runtime config and standardizer initialized.")

    # prevent access to non-existing keys
    OmegaConf.set_struct(cfg, True)

    # prepare data
    data_list = DataCompose.from_config(cfg.data.train_data)
    data_manager = DataManager(data_list, **cfg.data, **cfg.lightning)
    data_manager.setup("test")

    # model
    model_builder = get_builder(cfg.model.model_name)(
        hydra_oup_dir,
        data_list,
        image_shape=data_manager.image_shape,
        add_time_features=cfg.data.add_time_features,
        **cfg.model,
        **cfg.lightning,
    )
    model = model_builder.build_model(data_manager.test_dataloader())

    # trainer
    wandb_logger = model_builder.wandb_logger()
    wandb_logger.watch(model, log="all")
    trainer = model_builder.build_trainer(wandb_logger)

    # start training
    trainer.fit(
        model,
        data_manager,
        ckpt_path=getattr(cfg.lightning, "resume_from_checkpoint", None),
    )


if __name__ == "__main__":
    main()
