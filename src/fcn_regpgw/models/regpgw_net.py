"""RegPGW regional neural network architecture.

Implements the boundary-conditioned regional prognostic model with land-sea
mask, orography conditioning, and residual connection learning
(RegPGW + LS + Res).
"""

import torch
from torch import nn

from fcn_regpgw.const import (
    NUM_REGPGW_INPUT_CHANNELS,
    NUM_REGPGW_OUTPUT_CHANNELS,
)
from fcn_regpgw.models.fft import irfft2, rfft2


class RegPGWConvBlock(nn.Module):
    """Residual convolutional block with layer normalization and GELU."""

    def __init__(self, channels: int, dropout: float = 0.05) -> None:
        """Initialize RegPGWConvBlock.

        Args:
            channels (int): Feature channel dimension.
            dropout (float): Dropout probability.
        """
        super().__init__()
        self.norm1 = nn.GroupNorm(8, channels)
        self.conv1 = nn.Conv2d(
            channels, channels, kernel_size=3, padding=1, padding_mode="replicate"
        )
        self.act = nn.GELU()
        self.norm2 = nn.GroupNorm(8, channels)
        self.conv2 = nn.Conv2d(
            channels, channels, kernel_size=3, padding=1, padding_mode="replicate"
        )
        self.drop = nn.Dropout2d(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of residual block.

        Args:
            x (torch.Tensor): Input tensor of shape (B, C, H, W).

        Returns:
            torch.Tensor: Output tensor of shape (B, C, H, W).
        """
        residual = x
        out = self.norm1(x)
        out = self.conv1(out)
        out = self.act(out)
        out = self.norm2(out)
        out = self.conv2(out)
        out = self.drop(out)
        return residual + out


class RegPGWSpectralBlock(nn.Module):
    """Spectral frequency block for regional spatial pattern modeling."""

    def __init__(self, channels: int) -> None:
        """Initialize RegPGWSpectralBlock.

        Args:
            channels (int): Channel dimension.
        """
        super().__init__()
        self.channels = channels
        # Complex weights for spectral mixing
        self.weights_real = nn.Parameter(
            torch.randn(channels, channels, 1, 1) * 0.02
        )
        self.weights_imag = nn.Parameter(
            torch.randn(channels, channels, 1, 1) * 0.02
        )
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply 2D Fourier spectral filter.

        Args:
            x (torch.Tensor): Input tensor of shape (B, C, H, W).

        Returns:
            torch.Tensor: Spectral filtered tensor of shape (B, C, H, W).
        """
        _, _, h, w = x.shape
        # Permute to (B, H, W, C) for FFT
        x_perm = x.permute(0, 2, 3, 1)
        x_fft = rfft2(x_perm, dim=(1, 2), norm="ortho")
        x_real = x_fft.real.permute(0, 3, 1, 2)  # (B, C, H, W_half)
        x_imag = x_fft.imag.permute(0, 3, 1, 2)

        # Complex matrix multiplication
        out_real = torch.conv2d(x_real, self.weights_real) - torch.conv2d(
            x_imag, self.weights_imag
        )
        out_imag = torch.conv2d(x_real, self.weights_imag) + torch.conv2d(
            x_imag, self.weights_real
        )

        # Inverse FFT
        out_complex = torch.complex(
            out_real.permute(0, 2, 3, 1), out_imag.permute(0, 2, 3, 1)
        )
        out = irfft2(out_complex, s=(h, w), dim=(1, 2), norm="ortho")
        out = out.permute(0, 3, 1, 2)
        return self.act(out) + x


class RegPGWNet(nn.Module):
    """RegPGW regional neural prognostic model.

    Takes input state (73 channels), boundary condition (73 channels), and
    static mask channels (6 channels: LSM, Topo, sin/cos lat, sin/cos lon).
    Predicts the next regional state with residual learning.

    Attributes:
        in_channels (int): Total input channels (152).
        out_channels (int): Output channels (73).
        hidden_dim (int): Feature channel dimension.
        num_blocks (int): Number of residual/spectral processing blocks.
        use_residual (bool): Whether to predict residual over state_t.
    """

    def __init__(
        self,
        in_channels: int = NUM_REGPGW_INPUT_CHANNELS,
        out_channels: int = NUM_REGPGW_OUTPUT_CHANNELS,
        hidden_dim: int = 128,
        num_blocks: int = 6,
        dropout: float = 0.05,
        use_residual: bool = True,
        backbone_type: str = "conv",
    ) -> None:
        """Initialize RegPGWNet.

        Args:
            in_channels (int): Input channel dimension.
            out_channels (int): Output channel dimension.
            hidden_dim (int): Feature channels.
            num_blocks (int): Number of backbone blocks.
            dropout (float): Dropout probability.
            use_residual (bool): Whether to use residual state learning.
            backbone_type (str): 'conv' for residual conv blocks or 'spectral'.
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.hidden_dim = hidden_dim
        self.use_residual = use_residual
        self.backbone_type = backbone_type

        # Input feature projection
        self.in_proj = nn.Sequential(
            nn.Conv2d(
                in_channels,
                hidden_dim,
                kernel_size=3,
                padding=1,
                padding_mode="replicate",
            ),
            nn.GELU(),
            nn.GroupNorm(8, hidden_dim),
        )

        # Deep backbone
        blocks = []
        for i in range(num_blocks):
            if backbone_type == "spectral" and i % 2 == 1:
                blocks.append(RegPGWSpectralBlock(hidden_dim))
            else:
                blocks.append(RegPGWConvBlock(hidden_dim, dropout=dropout))
        self.backbone = nn.Sequential(*blocks)

        # Output projection predicting state tendency / delta
        self.out_proj = nn.Sequential(
            nn.GroupNorm(8, hidden_dim),
            nn.GELU(),
            nn.Conv2d(
                hidden_dim,
                out_channels,
                kernel_size=3,
                padding=1,
                padding_mode="replicate",
            ),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of RegPGWNet.

        Args:
            x (torch.Tensor): Input tensor of shape (B, 152, H, W).
                Channels [0:73] must contain the current regional state state_t.

        Returns:
            torch.Tensor: Predicted regional state tensor of shape (B, 73, H, W).
        """
        state_t = x[:, : self.out_channels, :, :]

        feats = self.in_proj(x)
        feats = self.backbone(feats)
        delta = self.out_proj(feats)

        if self.use_residual:
            return state_t + delta
        return delta
