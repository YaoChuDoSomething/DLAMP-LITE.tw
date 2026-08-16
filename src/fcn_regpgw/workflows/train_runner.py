"""Model training workflow runner for FCN-RegPGW architectures.

Orchestrates model instantiation, PyTorch Lightning trainer configuration,
dataset loader binding, and execution of the training loop.
"""


import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint
from torch import nn
from torch.utils.data import DataLoader

from fcn_regpgw.config import ModelConfig, TrainConfig
from fcn_regpgw.models.afno import AFNO
from fcn_regpgw.models.lightning_module import FCNRegPGWLightningModule
from fcn_regpgw.models.modafno import ModAFNO
from fcn_regpgw.models.precip_net import PrecipNet
from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class TrainRunner:
    """Workflow runner for training FCN-RegPGW neural network models."""

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        train_config: TrainConfig | None = None,
    ) -> None:
        """Initialize TrainRunner.

        Args:
            model_config (Optional[ModelConfig]): Architecture parameters.
            train_config (Optional[TrainConfig]): Training loop parameters.
        """
        self.model_cfg = model_config or ModelConfig()
        self.train_cfg = train_config or TrainConfig()

    def build_model(self) -> nn.Module:
        """Instantiate the neural network model based on configuration.

        Returns:
            nn.Module: Instantiated PyTorch neural network.

        Raises:
            ValueError: If unknown model name is configured.
        """
        name = self.model_cfg.model_name.lower()
        logger.info("Building model architecture: %s", self.model_cfg.model_name)

        if "modafno" in name:
            return ModAFNO(
                in_channels=self.model_cfg.in_channels,
                out_channels=self.model_cfg.out_channels,
                patch_size=self.model_cfg.patch_size,
                embed_dim=self.model_cfg.embed_dim,
                mod_dim=self.model_cfg.mod_dim,
                depth=self.model_cfg.depth,
                num_blocks=self.model_cfg.num_blocks,
                mlp_ratio=self.model_cfg.mlp_ratio,
                drop_rate=self.model_cfg.drop_rate,
                embed_method=self.model_cfg.embed_method,
                embed_dim_t=self.model_cfg.embed_dim_t,
            )
        elif "precip" in name:
            return PrecipNet(
                in_channels=self.model_cfg.in_channels,
                embed_dim=self.model_cfg.embed_dim,
                depth=self.model_cfg.depth,
                num_blocks=self.model_cfg.num_blocks,
                patch_size=self.model_cfg.patch_size,
            )
        elif "afno" in name:
            return AFNO(
                in_channels=self.model_cfg.in_channels,
                out_channels=self.model_cfg.out_channels,
                patch_size=self.model_cfg.patch_size,
                embed_dim=self.model_cfg.embed_dim,
                depth=self.model_cfg.depth,
                num_blocks=self.model_cfg.num_blocks,
                mlp_ratio=self.model_cfg.mlp_ratio,
                drop_rate=self.model_cfg.drop_rate,
            )
        else:
            raise ValueError(f"Unknown model name: {self.model_cfg.model_name}")

    def run(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader | None = None,
        custom_model: nn.Module | None = None,
    ) -> L.Trainer:
        """Execute the PyTorch Lightning model training loop.

        Args:
            train_loader (DataLoader): Training dataset DataLoader.
            val_loader (Optional[DataLoader]): Validation dataset DataLoader.
            custom_model (Optional[nn.Module]): Pre-instantiated model override.

        Returns:
            L.Trainer: Finished Lightning Trainer instance.
        """
        ckpt_dir = ensure_dir(self.train_cfg.checkpoint_dir)
        monitor_metric = "val_loss" if val_loader is not None else "train_loss"
        checkpoint_callback = ModelCheckpoint(
            dirpath=ckpt_dir,
            filename="{epoch:02d}-{val_loss:.4f}",
            save_top_k=3,
            monitor=monitor_metric,
            mode="min",
        )

        model = custom_model or self.build_model()
        lightning_module = FCNRegPGWLightningModule(
            model=model,
            learning_rate=self.train_cfg.learning_rate,
            weight_decay=self.train_cfg.weight_decay,
            max_epochs=self.train_cfg.max_epochs,
        )

        trainer = L.Trainer(
            max_epochs=self.train_cfg.max_epochs,
            check_val_every_n_epoch=self.train_cfg.val_interval,
            callbacks=[checkpoint_callback],
            default_root_dir=str(ckpt_dir),
            log_every_n_steps=10,
        )

        logger.info("Starting PyTorch Lightning training workflow...")
        trainer.fit(
            lightning_module,
            train_dataloaders=train_loader,
            val_dataloaders=val_loader,
        )
        logger.info("Training workflow complete.")
        return trainer
