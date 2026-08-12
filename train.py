import logging
from pathlib import Path

import hydra
from lightning.pytorch import seed_everything
from omegaconf import DictConfig, OmegaConf

from dlamp.managers import DataManager
from dlamp.models import get_builder
from dlamp.runtime_config import RuntimeConfig, get_standardizer
from dlamp.utils import DataCompose

log = logging.getLogger(__name__)


_HYDRA_CONFIG_DIR = str(Path(__file__).resolve().parent / "config")


@hydra.main(version_base=None, config_path=_HYDRA_CONFIG_DIR, config_name="train_pangu")
def main(cfg: DictConfig) -> None:
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