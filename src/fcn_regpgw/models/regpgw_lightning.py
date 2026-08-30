"""PyTorch Lightning Module for training RegPGW regional models.

Provides loss computation with interior and boundary weighting, validation
RMSE metrics across pressure levels, and learning rate scheduling.
"""

from typing import Any

import lightning.pytorch as pl
import torch
from torch import nn
from torch.optim.lr_scheduler import CosineAnnealingLR

from fcn_regpgw.config import RegPGWTrainConfig
from fcn_regpgw.const import (
    DEFAULT_BOUNDARY_WIDTH,
    NUM_REGPGW_INPUT_CHANNELS,
    NUM_REGPGW_OUTPUT_CHANNELS,
)
from fcn_regpgw.data.boundary_extractor import SpongeLayer
from fcn_regpgw.models.regpgw_net import RegPGWNet


class RegPGWLightningModule(pl.LightningModule):
    """Lightning Module for training RegPGW boundary-conditioned models.

    Attributes:
        model (nn.Module): Neural network instance (e.g., RegPGWNet).
        train_cfg (RegPGWTrainConfig): Training configuration.
        boundary_width (int): Sponge boundary width.
    """

    def __init__(
        self,
        model: nn.Module | None = None,
        train_cfg: RegPGWTrainConfig | None = None,
        in_channels: int = NUM_REGPGW_INPUT_CHANNELS,
        out_channels: int = NUM_REGPGW_OUTPUT_CHANNELS,
        boundary_width: int = DEFAULT_BOUNDARY_WIDTH,
    ) -> None:
        """Initialize RegPGWLightningModule.

        Args:
            model (Optional[nn.Module]): RegPGW neural network.
            train_cfg (Optional[RegPGWTrainConfig]): Training config.
            in_channels (int): Input channel count.
            out_channels (int): Output channel count.
            boundary_width (int): Sponge boundary width.
        """
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        self.train_cfg = train_cfg or RegPGWTrainConfig()
        self.boundary_width = boundary_width

        if model is not None:
            self.model = model
        else:
            self.model = RegPGWNet(
                in_channels=in_channels,
                out_channels=out_channels,
            )

        self.mse_loss = nn.MSELoss(reduction="none")
        self.l1_loss = nn.L1Loss(reduction="none")
        self._sponge_layer: SpongeLayer | None = None

    def _get_sponge_mask(self, h: int, w: int, device: torch.device) -> torch.Tensor:
        """Fetch or initialize 2D sponge weighting mask.

        Args:
            h (int): Height.
            w (int): Width.
            device (torch.device): Target device.

        Returns:
            torch.Tensor: Sponge mask of shape (1, 1, H, W).
        """
        if self._sponge_layer is None or self._sponge_layer.height != h or self._sponge_layer.width != w:
            self._sponge_layer = SpongeLayer(
                height=h,
                width=w,
                boundary_width=self.boundary_width,
            )
        mask_np = self._sponge_layer.mask
        return torch.from_numpy(mask_np).to(device=device, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through RegPGW model.

        Args:
            x (torch.Tensor): Input tensor (B, 152, H, W).

        Returns:
            torch.Tensor: Predicted tensor (B, 73, H, W).
        """
        return self.model(x)

    def compute_weighted_loss(
        self, pred: torch.Tensor, target: torch.Tensor
    ) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        """Compute interior and boundary weighted loss.

        Args:
            pred (torch.Tensor): Predicted tensor (B, C, H, W).
            target (torch.Tensor): Target ground truth tensor (B, C, H, W).

        Returns:
            Tuple[torch.Tensor, Dict[str, torch.Tensor]]: (total_loss, metrics_dict).
        """
        _, _, h, w = pred.shape
        sponge_mask = self._get_sponge_mask(h, w, pred.device)  # (1, 1, H, W)
        interior_mask = 1.0 - sponge_mask

        pixel_mse = self.mse_loss(pred, target)

        loss_interior = (pixel_mse * interior_mask).sum() / (
            interior_mask.sum() * pred.shape[0] * pred.shape[1] + 1e-6
        )
        loss_boundary = (pixel_mse * sponge_mask).sum() / (
            sponge_mask.sum() * pred.shape[0] * pred.shape[1] + 1e-6
        )

        total_loss = (
            self.train_cfg.interior_loss_weight * loss_interior
            + self.train_cfg.boundary_loss_weight * loss_boundary
        )

        metrics = {
            "loss_interior": loss_interior.detach(),
            "loss_boundary": loss_boundary.detach(),
            "loss_total": total_loss.detach(),
        }
        return total_loss, metrics

    def training_step(
        self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        """Execute single training optimization step.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor]): (inputs, targets) batch.
            batch_idx (int): Batch index.

        Returns:
            torch.Tensor: Scalar loss for backpropagation.
        """
        inputs, targets = batch
        preds = self.forward(inputs)
        loss, metrics = self.compute_weighted_loss(preds, targets)

        self.log("train/loss", loss, prog_bar=True, on_step=True, on_epoch=True)
        self.log("train/loss_interior", metrics["loss_interior"], on_step=False, on_epoch=True)
        self.log("train/loss_boundary", metrics["loss_boundary"], on_step=False, on_epoch=True)
        return loss

    def validation_step(
        self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        """Execute validation step and log metrics.

        Args:
            batch (Tuple[torch.Tensor, torch.Tensor]): (inputs, targets) batch.
            batch_idx (int): Batch index.

        Returns:
            torch.Tensor: Validation loss.
        """
        inputs, targets = batch
        preds = self.forward(inputs)
        loss, _ = self.compute_weighted_loss(preds, targets)

        # RMSE
        rmse = torch.sqrt(torch.mean((preds - targets) ** 2))
        self.log("val/loss", loss, prog_bar=True, on_epoch=True)
        self.log("val/rmse", rmse, prog_bar=True, on_epoch=True)
        return loss

    def configure_optimizers(self) -> dict[str, Any]:
        """Configure AdamW optimizer and CosineAnnealing learning rate scheduler.

        Returns:
            Dict[str, Any]: Optimizer and LR scheduler dictionary.
        """
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.train_cfg.learning_rate,
            weight_decay=self.train_cfg.weight_decay,
        )
        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=self.train_cfg.max_epochs,
            eta_min=1e-6,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "epoch",
            },
        }
