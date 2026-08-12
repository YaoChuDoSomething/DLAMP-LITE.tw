"""DLAMP Training Entrypoint script using Hydra and PyTorch Lightning.

Usage:
    python -m dlamp.train
"""

import hydra
import lightning as L
from omegaconf import DictConfig

from dlamp.datamodule import SyntheticDataModule
from dlamp.lightning_module import DLAMPModule


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig) -> None:
    """Main training function configured via Hydra.

    Args:
        cfg (DictConfig): Hydra configuration object.
    """
    model = DLAMPModule(
        in_features=cfg.model.in_features,
        hidden_dim=cfg.model.hidden_dim,
        out_features=cfg.model.out_features,
        lr=cfg.model.lr,
    )
    datamodule = SyntheticDataModule(
        batch_size=cfg.data.batch_size,
        num_samples=cfg.data.num_samples,
        in_features=cfg.model.in_features,
        out_features=cfg.model.out_features,
    )
    trainer = L.Trainer(
        max_epochs=cfg.trainer.max_epochs,
        accelerator=cfg.trainer.accelerator,
        devices=cfg.trainer.devices,
    )
    trainer.fit(model, datamodule=datamodule)


if __name__ == "__main__":
    main()
