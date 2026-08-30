"""Modulation and positional embedding modules for Fourier Neural Operators.

Provides continuous sinusoidal positional embeddings, one-hot timestep
embeddings, and modulated MLP projection networks.
"""

from typing import Literal

import torch
from torch import Tensor, nn


class PositionalEmbedding(nn.Module):
    """Sinusoidal positional embedding network for continuous temporal values."""

    def __init__(self, num_channels: int) -> None:
        """Initialize PositionalEmbedding.

        Args:
            num_channels (int): Number of embedding channels.
        """
        super().__init__()
        self.num_channels = num_channels
        freqs = torch.pi * torch.arange(
            start=1,
            end=self.num_channels // 2 + 1,
            dtype=torch.float32,
        )
        self.register_buffer("freqs", freqs)

    def forward(self, x: Tensor) -> Tensor:
        """Compute sinusoidal embedding for input tensor.

        Args:
            x (Tensor): Scalar or 1D tensor of timesteps.

        Returns:
            Tensor: Embedding tensor of shape (batch_size, num_channels).
        """
        freqs: Tensor = self.freqs  # type: ignore[assignment]
        outer = x.view(-1).outer(freqs.to(x.dtype))
        sin_cos = torch.cat([outer.cos(), outer.sin()], dim=1)
        return sin_cos[:, : self.num_channels]


class OneHotEmbedding(nn.Module):
    """One-hot linear interpolation embedding network for discrete timesteps."""

    def __init__(self, num_channels: int) -> None:
        """Initialize OneHotEmbedding.

        Args:
            num_channels (int): Number of discrete bin channels.
        """
        super().__init__()
        self.num_channels = num_channels
        indices = torch.arange(num_channels, dtype=torch.float32).view(1, -1)
        self.register_buffer("indices", indices)

    def forward(self, t: Tensor) -> Tensor:
        """Compute one-hot triangular kernel embedding for normalized time in [0, 1].

        Args:
            t (Tensor): Normalized timestep tensor in [0, 1].

        Returns:
            Tensor: Embedding tensor of shape (batch_size, num_channels).
        """
        indices: Tensor = self.indices  # type: ignore[assignment]
        scaled = t.view(-1, 1) * (self.num_channels - 1)
        return torch.clamp(1.0 - torch.abs(scaled - indices), min=0.0)


class ModEmbedNet(nn.Module):
    """Timestep modulation embedding network with multi-layer perceptron projection."""

    def __init__(
        self,
        max_time: float = 1.0,
        dim: int = 64,
        depth: int = 1,
        activation_fn: type[nn.Module] = nn.GELU,
        method: Literal["sinusoidal", "onehot"] = "sinusoidal",
    ) -> None:
        """Initialize ModEmbedNet.

        Args:
            max_time (float): Normalization scale factor for maximum input time.
            dim (int): Dimensionality of the time embedding.
            depth (int): Number of dense projection layers.
            activation_fn (Type[nn.Module]): Nonlinear activation module class.
            method (Literal["sinusoidal", "onehot"]): Embedding calculation mode.

        Raises:
            ValueError: If an unsupported embedding method is provided.
        """
        super().__init__()
        self.max_time = max_time
        self.method = method
        self.dim = dim

        if method == "onehot":
            self.embedder: nn.Module = OneHotEmbedding(dim)
        elif method == "sinusoidal":
            self.embedder = PositionalEmbedding(dim)
        else:
            raise ValueError(
                f"Embedding method '{method}' not supported. Use 'sinusoidal' or 'onehot'."
            )

        layers = []
        for _ in range(depth):
            layers.extend([nn.Linear(dim, dim), activation_fn()])
        self.mlp = nn.Sequential(*layers)

    def forward(self, t: Tensor) -> Tensor:
        """Project timestep into modulation embedding vector.

        Args:
            t (Tensor): Timestep tensor.

        Returns:
            Tensor: Modulation vector of shape (batch_size, dim).
        """
        t_norm = t / self.max_time
        emb = self.embedder(t_norm)
        return self.mlp(emb)
