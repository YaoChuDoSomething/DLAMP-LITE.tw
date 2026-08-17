"""PyTorch Lightning module for training FCN-RegPGW atmospheric neural models.

Encapsulates training, validation step logic, loss function computation,
and optimizer/scheduler configuration.
"""

from typing import Any

import lightning as L
import torch
import torch.nn.functional as F
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR


class FCNRegPGWLightningModule(L.LightningModule):
    """PyTorch Lightning wrapper module for AFNO, ModAFNO, and PrecipNet training."""

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 5e-4,
        weight_decay: float = 1e-5,
        max_epochs: int = 50,
        loss_type: str = "mse",
    ) -> None:
        """Initialize LightningModule.

        Args:
            model (nn.Module): Neural network architecture instance.
            learning_rate (float): Initial AdamW learning rate.
            weight_decay (float): L2 regularization factor.
            max_epochs (int): Total training epochs for scheduler.
            loss_type (str): Loss objective type ('mse', 'l1', 'huber').
        """
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        self.model = model
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.max_epochs = max_epochs
        self.loss_type = loss_type

        if loss_type == "l1":
            self.criterion: nn.Module = nn.L1Loss()
        elif loss_type == "huber":
            self.criterion = nn.HuberLoss()
        else:
            self.criterion = nn.MSELoss()

    def forward(
        self, x: torch.Tensor, t: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Forward pass dispatching to the underlying model.

        Args:
            x (torch.Tensor): Input tensor.
            t (Optional[torch.Tensor]): Optional modulation timestep.

        Returns:
            torch.Tensor: Model prediction tensor.
        """
        if t is not None:
            return self.model(x, t)  # type: ignore[no-any-return, operator]
        return self.model(x)  # type: ignore[no-any-return, operator]

    def training_step(
        self, batch: tuple[Any, ...], batch_idx: int
    ) -> torch.Tensor:
        """Execute a single training step.

        Args:
            batch (Tuple[Any, ...]): Batch tensors from DataLoader.
            batch_idx (int): Batch index.

        Returns:
            torch.Tensor: Scalar training loss.
        """
        if len(batch) == 3:
            # ModAFNO dataset: (x, t, y)
            x, t, y = batch
            pred = self(x, t)
        else:
            # Standard forecast dataset: (x, y)
            x, y = batch
            pred = self(x)

        loss = self.criterion(pred, y)
        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            sync_dist=True,
        )
        return loss

    def validation_step(
        self, batch: tuple[Any, ...], batch_idx: int
    ) -> torch.Tensor:
        """Execute a single validation step and log metrics.

        Args:
            batch (Tuple[Any, ...]): Validation batch tensors.
            batch_idx (int): Batch index.

        Returns:
            torch.Tensor: Scalar validation loss.
        """
        if len(batch) == 3:
            x, t, y = batch
            pred = self(x, t)
        else:
            x, y = batch
            pred = self(x)

        loss = self.criterion(pred, y)
        rmse = torch.sqrt(F.mse_loss(pred, y))

        self.log(
            "val_loss",
            loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            sync_dist=True,
        )
        self.log(
            "val_rmse",
            rmse,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            sync_dist=True,
        )
        return loss

    def configure_optimizers(self) -> dict[str, Any]:
        """Configure AdamW optimizer and CosineAnnealingLR scheduler.

        Returns:
            Dict[str, Any]: Optimizer and lr_scheduler dictionary.
        """
        optimizer = AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )
        scheduler = CosineAnnealingLR(
            optimizer,
            T_max=self.max_epochs,
            eta_min=1e-7,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "epoch",
            },
        }
