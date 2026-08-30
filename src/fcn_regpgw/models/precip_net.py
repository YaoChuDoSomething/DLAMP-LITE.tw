"""Precipitation diagnostic neural models for FCN-RegPGW.

Provides diagnostic neural networks for mapping multi-level atmospheric
fields to surface total precipitation (tp) rate.
"""


from torch import Tensor, nn

from fcn_regpgw.models.afno import AFNO


class PrecipNet(nn.Module):
    """Precipitation diagnostic model mapping atmospheric state to surface rainfall."""

    def __init__(
        self,
        inp_shape: tuple[int, int] = (720, 1440),
        in_channels: int = 73,
        embed_dim: int = 256,
        depth: int = 6,
        num_blocks: int = 4,
        patch_size: tuple[int, int] = (2, 2),
    ) -> None:
        """Initialize PrecipNet.

        Args:
            inp_shape (Tuple[int, int]): Input spatial resolution (H, W).
            in_channels (int): Input atmospheric channel count.
            embed_dim (int): Embedding token dimension.
            depth (int): Number of AFNO blocks.
            num_blocks (int): Spectral block partitions.
            patch_size (Tuple[int, int]): 2D patch partition size.
        """
        super().__init__()
        self.backbone = AFNO(
            inp_shape=inp_shape,
            in_channels=in_channels,
            out_channels=1,  # Precipitation output (tp)
            embed_dim=embed_dim,
            depth=depth,
            num_blocks=num_blocks,
            patch_size=patch_size,
        )
        self.relu = nn.ReLU()

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass predicting non-negative precipitation accumulation.

        Args:
            x (Tensor): Atmospheric state tensor of shape (B, in_channels, H, W).

        Returns:
            Tensor: Precipitation tensor of shape (B, 1, H, W).
        """
        out = self.backbone(x)
        # Precipitation is strictly non-negative
        return self.relu(out)
