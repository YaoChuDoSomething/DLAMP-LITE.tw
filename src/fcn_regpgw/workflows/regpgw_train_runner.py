"""High-level orchestration runner for training RegPGW regional models.

Manages data loading, model compilation, PyTorch Lightning trainer execution,
and model checkpoint serialization.
"""

from pathlib import Path

import lightning.pytorch as pl
import numpy as np
from lightning.pytorch.callbacks import (
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
)

from fcn_regpgw.config import RegPGWDataConfig, RegPGWModelConfig, RegPGWTrainConfig
from fcn_regpgw.data.regional_dataset import RegPGWDataset, create_regpgw_dataloader
from fcn_regpgw.models.regpgw_lightning import RegPGWLightningModule
from fcn_regpgw.models.regpgw_net import RegPGWNet
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class RegPGWTrainRunner:
    """Orchestrates end-to-end training of RegPGW models.

    Attributes:
        data_cfg (RegPGWDataConfig): Data configuration.
        model_cfg (RegPGWModelConfig): Model architecture configuration.
        train_cfg (RegPGWTrainConfig): Training hyperparameters configuration.
    """

    def __init__(
        self,
        data_cfg: RegPGWDataConfig | None = None,
        model_cfg: RegPGWModelConfig | None = None,
        train_cfg: RegPGWTrainConfig | None = None,
    ) -> None:
        """Initialize RegPGWTrainRunner.

        Args:
            data_cfg (Optional[RegPGWDataConfig]): Data config.
            model_cfg (Optional[RegPGWModelConfig]): Model config.
            train_cfg (Optional[RegPGWTrainConfig]): Train config.
        """
        self.data_cfg = data_cfg or RegPGWDataConfig()
        self.model_cfg = model_cfg or RegPGWModelConfig()
        self.train_cfg = train_cfg or RegPGWTrainConfig()

    def run(
        self,
        train_states: np.ndarray,
        val_states: np.ndarray,
        static_features: np.ndarray | None = None,
    ) -> Path:
        """Run the complete RegPGW training loop.

        Args:
            train_states (np.ndarray): Training sequences (T_train, 73, H, W).
            val_states (np.ndarray): Validation sequences (T_val, 73, H, W).
            static_features (Optional[np.ndarray]): Static geographical features (6, H, W).

        Returns:
            Path: Path to the best saved model checkpoint (.ckpt).
        """
        logger.info("Setting up RegPGW training datasets and dataloaders")
        train_ds = RegPGWDataset(
            states=train_states,
            static_features=static_features,
            lead_steps=1,
        )
        val_ds = RegPGWDataset(
            states=val_states,
            static_features=static_features,
            lead_steps=1,
        )

        train_loader = create_regpgw_dataloader(
            train_ds,
            batch_size=self.train_cfg.batch_size,
            shuffle=True,
            num_workers=self.train_cfg.num_workers,
        )
        val_loader = create_regpgw_dataloader(
            val_ds,
            batch_size=self.train_cfg.batch_size,
            shuffle=False,
            num_workers=self.train_cfg.num_workers,
        )

        logger.info("Instantiating RegPGW model architecture")
        model = RegPGWNet(
            in_channels=self.model_cfg.in_channels,
            out_channels=self.model_cfg.out_channels,
            hidden_dim=self.model_cfg.hidden_dim,
            num_blocks=self.model_cfg.num_blocks,
            dropout=self.model_cfg.dropout,
            use_residual=self.model_cfg.use_residual_connection,
        )

        lightning_module = RegPGWLightningModule(
            model=model,
            train_cfg=self.train_cfg,
            in_channels=self.model_cfg.in_channels,
            out_channels=self.model_cfg.out_channels,
            boundary_width=self.data_cfg.boundary_width,
        )

        checkpoint_dir = self.train_cfg.checkpoint_dir
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_cb = ModelCheckpoint(
            dirpath=str(checkpoint_dir),
            filename="regpgw-best-{epoch:02d}-{val/loss:.4f}",
            monitor="val/loss",
            mode="min",
            save_top_k=1,
            save_last=True,
        )
        lr_monitor = LearningRateMonitor(logging_interval="epoch")
        early_stop = EarlyStopping(
            monitor="val/loss",
            patience=15,
            mode="min",
        )

        trainer = pl.Trainer(
            max_epochs=self.train_cfg.max_epochs,
            callbacks=[checkpoint_cb, lr_monitor, early_stop],
            default_root_dir=str(self.train_cfg.log_dir),
            val_check_interval=self.train_cfg.val_check_interval,
            enable_checkpointing=True,
        )

        logger.info("Starting PyTorch Lightning model training...")
        trainer.fit(
            model=lightning_module,
            train_dataloaders=train_loader,
            val_dataloaders=val_loader,
        )

        best_path = Path(checkpoint_cb.best_model_path)
        logger.info("Training complete. Best checkpoint saved to %s", best_path)
        return best_path
