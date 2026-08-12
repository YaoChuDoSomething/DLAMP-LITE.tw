"""Simple PyTorch MLP model architecture for CPU execution.

Usage:
    model = SimpleMLP(in_features=10, hidden_dim=32, out_features=1)
"""

import torch
from torch import nn


class SimpleMLP(nn.Module):
    """Simple multi-layer perceptron.

    Attributes:
        net (nn.Sequential): Sequential neural network layers.
    """

    def __init__(
        self, in_features: int = 10, hidden_dim: int = 32, out_features: int = 1
    ) -> None:
        """Initializes SimpleMLP model.

        Args:
            in_features (int): Number of input features.
            hidden_dim (int): Number of hidden units.
            out_features (int): Number of output features.
        """
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_features),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of SimpleMLP.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, in_features).

        Returns:
            torch.Tensor: Output tensor of shape (batch_size, out_features).
        """
        return self.net(x)  # type: ignore[no-any-return]
