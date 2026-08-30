"""Adaptive Fourier Neural Operator (AFNO) architecture for atmospheric dynamics.

Implements the 2D spatial frequency token mixer with patch embeddings,
block-diagonal complex spectral filtering, and feedforward networks.
"""


import torch
import torch.nn.functional as F
from torch import Tensor, nn

from fcn_regpgw.models.fft import imag, irfft2, real, rfft2, view_as_complex


class AFNOMlp(nn.Module):
    """Feed-forward multi-layer perceptron with dropout for AFNO blocks."""

    def __init__(
        self,
        in_features: int,
        latent_features: int,
        out_features: int,
        activation_fn: nn.Module | None = None,
        drop_rate: float = 0.0,
    ) -> None:
        """Initialize AFNOMlp.

        Args:
            in_features (int): Input channel dimension.
            latent_features (int): Hidden intermediate dimension.
            out_features (int): Output feature dimension.
            activation_fn (nn.Module | None): Activation layer. Defaults to GELU.
            drop_rate (float): Dropout probability.
        """
        super().__init__()
        self.fc1 = nn.Linear(in_features, latent_features)
        self.act = activation_fn if activation_fn is not None else nn.GELU()
        self.fc2 = nn.Linear(latent_features, out_features)
        self.drop = nn.Dropout(drop_rate)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass.

        Args:
            x (Tensor): Input tensor of shape (B, H, W, C).

        Returns:
            Tensor: Output tensor of shape (B, H, W, out_features).
        """
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x


class PatchEmbed(nn.Module):
    """2D Image to Patch Embedding via 2D Convolution."""

    def __init__(
        self,
        img_size: tuple[int, int] = (720, 1440),
        patch_size: tuple[int, int] = (2, 2),
        in_channels: int = 73,
        embed_dim: int = 512,
    ) -> None:
        """Initialize PatchEmbed.

        Args:
            img_size (Tuple[int, int]): Input spatial dimensions (H, W).
            patch_size (Tuple[int, int]): Patch kernel and stride (pH, pW).
            in_channels (int): Number of input physical channels.
            embed_dim (int): Projected latent token dimension.
        """
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.h_patches = img_size[0] // patch_size[0]
        self.w_patches = img_size[1] // patch_size[1]
        self.num_patches = self.h_patches * self.w_patches

        self.proj = nn.Conv2d(
            in_channels,
            embed_dim,
            kernel_size=patch_size,
            stride=patch_size,
        )

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass projecting image tensor to patch tokens.

        Args:
            x (Tensor): Tensor of shape (B, in_channels, H, W).

        Returns:
            Tensor: Patch tokens of shape (B, H_patches, W_patches, embed_dim).
        """
        # (B, C, H, W) -> (B, embed_dim, H_p, W_p) -> (B, H_p, W_p, embed_dim)
        return self.proj(x).permute(0, 2, 3, 1)


class AFNO2DLayer(nn.Module):
    """2D Adaptive Fourier Neural Operator Layer."""

    def __init__(
        self,
        hidden_size: int,
        num_blocks: int = 8,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
        hidden_size_factor: int = 1,
    ) -> None:
        """Initialize AFNO2DLayer.

        Args:
            hidden_size (int): Hidden token feature dimension.
            num_blocks (int): Number of block-diagonal partitions.
            sparsity_threshold (float): Frequency domain soft-thresholding parameter.
            hard_thresholding_fraction (float): Fraction of modes preserved.
            hidden_size_factor (int): Hidden expansion factor for complex weights.
        """
        super().__init__()
        if hidden_size % num_blocks != 0:
            raise ValueError(
                f"hidden_size ({hidden_size}) must be divisible by "
                f"num_blocks ({num_blocks})"
            )

        self.hidden_size = hidden_size
        self.num_blocks = num_blocks
        self.block_size = hidden_size // num_blocks
        self.hidden_size_factor = hidden_size_factor
        self.sparsity_threshold = sparsity_threshold
        self.hard_thresholding_fraction = hard_thresholding_fraction

        scale = 1.0 / (hidden_size * hidden_size_factor)
        self.w1 = nn.Parameter(
            scale
            * torch.randn(
                2,
                num_blocks,
                self.block_size,
                self.block_size * hidden_size_factor,
            )
        )
        self.b1 = nn.Parameter(
            scale
            * torch.randn(
                2,
                num_blocks,
                self.block_size * hidden_size_factor,
            )
        )
        self.w2 = nn.Parameter(
            scale
            * torch.randn(
                2,
                num_blocks,
                self.block_size * hidden_size_factor,
                self.block_size,
            )
        )
        self.b2 = nn.Parameter(
            scale * torch.randn(2, num_blocks, self.block_size)
        )

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass through spectral transform and block-diagonal filtering.

        Args:
            x (Tensor): Input tensor of shape (B, H, W, C).

        Returns:
            Tensor: Filtered output tensor of shape (B, H, W, C).
        """
        b, h, w, c = x.shape
        x_fft = rfft2(x, dim=(1, 2), norm="ortho")
        x_real, x_imag = real(x_fft), imag(x_fft)

        x_real = x_real.reshape(
            b, h, w // 2 + 1, self.num_blocks, self.block_size
        )
        x_imag = x_imag.reshape(
            b, h, w // 2 + 1, self.num_blocks, self.block_size
        )

        o1_shape = (
            b,
            h,
            w // 2 + 1,
            self.num_blocks,
            self.block_size * self.hidden_size_factor,
        )
        o1_real = torch.zeros(o1_shape, device=x.device)
        o1_imag = torch.zeros(o1_shape, device=x.device)
        o2 = torch.zeros(x_real.shape + (2,), device=x.device)

        total_modes = min(h, w) // 2 + 1
        kept_modes = max(
            1, int(total_modes * self.hard_thresholding_fraction)
        )

        o1_real[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
        ] = F.relu(
            torch.einsum(
                "nyxbi,bio->nyxbo",
                x_real[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w1[0],
            )
            - torch.einsum(
                "nyxbi,bio->nyxbo",
                x_imag[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w1[1],
            )
            + self.b1[0]
        )

        o1_imag[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
        ] = F.relu(
            torch.einsum(
                "nyxbi,bio->nyxbo",
                x_imag[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w1[0],
            )
            + torch.einsum(
                "nyxbi,bio->nyxbo",
                x_real[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w1[1],
            )
            + self.b1[1]
        )

        o2[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
            ...,
            0,
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w2[0],
            )
            - torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w2[1],
            )
            + self.b2[0]
        )

        o2[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
            ...,
            1,
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w2[0],
            )
            + torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :,
                    total_modes - kept_modes : total_modes + kept_modes,
                    :kept_modes,
                ],
                self.w2[1],
            )
            + self.b2[1]
        )

        x_out = F.softshrink(o2, lambd=self.sparsity_threshold)
        x_complex = view_as_complex(x_out)
        x_complex = x_complex.reshape(b, h, w // 2 + 1, c)
        return irfft2(x_complex, s=(h, w), dim=(1, 2), norm="ortho")


class AFNOBlock(nn.Module):
    """Transformer-style block combining AFNO2DLayer and AFNOMlp with LayerNorms."""

    def __init__(
        self,
        dim: int,
        mlp_ratio: float = 2.0,
        drop_rate: float = 0.0,
        num_blocks: int = 8,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ) -> None:
        """Initialize AFNOBlock.

        Args:
            dim (int): Feature channel dimension.
            mlp_ratio (float): Hidden expansion factor for feedforward network.
            drop_rate (float): Dropout probability.
            num_blocks (int): Number of block partitions in spectral layer.
            sparsity_threshold (float): Spectral sparsity threshold.
            hard_thresholding_fraction (float): High frequency preservation fraction.
        """
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.filter = AFNO2DLayer(
            hidden_size=dim,
            num_blocks=num_blocks,
            sparsity_threshold=sparsity_threshold,
            hard_thresholding_fraction=hard_thresholding_fraction,
        )
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = AFNOMlp(
            in_features=dim,
            latent_features=int(dim * mlp_ratio),
            out_features=dim,
            drop_rate=drop_rate,
        )

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass with residual connections.

        Args:
            x (Tensor): Input tensor of shape (B, H, W, C).

        Returns:
            Tensor: Output tensor of shape (B, H, W, C).
        """
        x = x + self.filter(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x


class AFNO(nn.Module):
    """Complete Adaptive Fourier Neural Operator backbone model."""

    def __init__(
        self,
        inp_shape: tuple[int, int] = (720, 1440),
        in_channels: int = 73,
        out_channels: int = 73,
        patch_size: tuple[int, int] = (2, 2),
        embed_dim: int = 512,
        depth: int = 8,
        num_blocks: int = 8,
        mlp_ratio: float = 2.0,
        drop_rate: float = 0.0,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ) -> None:
        """Initialize AFNO model.

        Args:
            inp_shape (Tuple[int, int]): Input spatial resolution (H, W).
            in_channels (int): Number of input channels.
            out_channels (int): Number of output channels.
            patch_size (Tuple[int, int]): 2D Patch partition size.
            embed_dim (int): Channel embedding dimension.
            depth (int): Number of stacked AFNO blocks.
            num_blocks (int): Number of spectral block partitions.
            mlp_ratio (float): Hidden expansion ratio.
            drop_rate (float): Dropout probability.
            sparsity_threshold (float): Sparsity threshold for spectral mixer.
            hard_thresholding_fraction (float): Frequency preservation ratio.
        """
        super().__init__()
        self.inp_shape = inp_shape
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.patch_size = patch_size
        self.embed_dim = embed_dim

        self.patch_embed = PatchEmbed(
            img_size=inp_shape,
            patch_size=patch_size,
            in_channels=in_channels,
            embed_dim=embed_dim,
        )

        self.blocks = nn.ModuleList(
            [
                AFNOBlock(
                    dim=embed_dim,
                    mlp_ratio=mlp_ratio,
                    drop_rate=drop_rate,
                    num_blocks=num_blocks,
                    sparsity_threshold=sparsity_threshold,
                    hard_thresholding_fraction=hard_thresholding_fraction,
                )
                for _ in range(depth)
            ]
        )

        self.head = nn.Linear(
            embed_dim,
            out_channels * patch_size[0] * patch_size[1],
            bias=False,
        )

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass forecasting atmospheric state.

        Args:
            x (Tensor): Input tensor of shape (B, in_channels, H, W).

        Returns:
            Tensor: Output forecast tensor of shape (B, out_channels, H, W).
        """
        b, _, h, w = x.shape
        x_tokens = self.patch_embed(x)

        for block in self.blocks:
            x_tokens = block(x_tokens)

        out_tokens = self.head(x_tokens)
        h_p, w_p = self.patch_embed.h_patches, self.patch_embed.w_patches
        p0, p1 = self.patch_size

        out = out_tokens.view(b, h_p, w_p, self.out_channels, p0, p1)
        out = out.permute(0, 3, 1, 4, 2, 5).contiguous()
        return out.view(b, self.out_channels, h, w)
