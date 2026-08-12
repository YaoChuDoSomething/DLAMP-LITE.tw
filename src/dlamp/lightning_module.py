"""PyTorch Lightning Module wrapper for DLAMP CPU training.

Usage:
    module = DLAMPModule(in_features=10, hidden_dim=32, out_features=1, lr=1e-3)
"""

from typing import Any

import lightning as L
import torch
from torch import nn
from torch.optim import Adam

from dlamp.model import SimpleMLP


class DLAMPModule(L.LightningModule):
    """Lightning Module for DLAMP model training on CPU.

    Attributes:
        model (SimpleMLP): Core PyTorch model.
        loss_fn (nn.Module): MSE loss function.
        lr (float): Learning rate.
    """

    def __init__(
        self,
        in_features: int = 10,
        hidden_dim: int = 32,
        out_features: int = 1,
        lr: float = 1e-3,
    ) -> None:
        """Initializes DLAMP Lightning Module.

        Args:
            in_features (int): Number of input features.
            hidden_dim (int): Number of hidden units.
            out_features (int): Number of output features.
            lr (float): Learning rate for Adam optimizer.
        """
        super().__init__()
        self.save_hyperparameters()
        self.model = SimpleMLP(
            in_features=in_features,
            hidden_dim=hidden_dim,
            out_features=out_features,
        )
        self.loss_fn = nn.MSELoss()
        self.lr = lr

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Model output.
        """
        out: torch.Tensor = self.model(x)
        return out

    def training_step(
        self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        """Runs single training step.

        Args:
            batch (tuple[torch.Tensor, torch.Tensor]): Tuple of (x, y).
            batch_idx (int): Batch index.

        Returns:
            torch.Tensor: Computed loss tensor.
        """
        x, y = batch
        preds = self(x)
        loss: torch.Tensor = self.loss_fn(preds, y)
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self) -> Any:
        """Configures optimizer.

        Returns:
            Any: PyTorch optimizer instance.
        """
        return Adam(self.parameters(), lr=self.lr)
