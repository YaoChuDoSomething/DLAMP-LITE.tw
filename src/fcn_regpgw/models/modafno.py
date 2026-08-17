"""Modulated Adaptive Fourier Neural Operator (ModAFNO) architecture.

Enables continuous temporal interpolation and condition-modulated atmospheric
forecasting via dynamic scale and shift parameter generation.
"""

from typing import Literal

import torch
import torch.nn.functional as F
from torch import Tensor, nn

from fcn_regpgw.models.afno import AFNOMlp, PatchEmbed
from fcn_regpgw.models.embeddings import ModEmbedNet
from fcn_regpgw.models.fft import imag, irfft2, real, rfft2, view_as_complex


class ScaleShiftMlp(nn.Module):
    """Multi-Layer Perceptron computing scale and shift modulation parameters."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_features: int | None = None,
        hidden_layers: int = 0,
        activation_fn: type[nn.Module] = nn.GELU,
    ) -> None:
        """Initialize ScaleShiftMlp.

        Args:
            in_features (int): Input modulation vector dimension.
            out_features (int): Output affine parameter dimension.
            hidden_features (Optional[int]): Intermediate hidden layer size.
            hidden_layers (int): Number of intermediate projection layers.
            activation_fn (Type[nn.Module]): Nonlinear activation class.
        """
        super().__init__()
        h_dim = hidden_features or (2 * out_features)
        layers: list[nn.Module] = []

        if hidden_layers > 0:
            layers.extend([nn.Linear(in_features, h_dim), activation_fn()])
            for _ in range(hidden_layers - 1):
                layers.extend([nn.Linear(h_dim, h_dim), activation_fn()])
            layers.append(nn.Linear(h_dim, out_features))
        else:
            layers.append(nn.Linear(in_features, out_features))

        self.mlp = nn.Sequential(*layers)

    def forward(self, t: Tensor) -> Tensor:
        """Forward pass generating affine parameters.

        Args:
            t (Tensor): Modulation feature vector of shape (B, in_features).

        Returns:
            Tensor: Parameter tensor of shape (B, out_features).
        """
        return self.mlp(t)


class ModAFNO2DLayer(nn.Module):
    """Modulated Adaptive Fourier 2D Layer."""

    def __init__(
        self,
        hidden_size: int,
        mod_dim: int,
        num_blocks: int = 1,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
        hidden_size_factor: int = 1,
    ) -> None:
        """Initialize ModAFNO2DLayer.

        Args:
            hidden_size (int): Hidden feature channel dimension.
            mod_dim (int): Modulation embedding vector dimension.
            num_blocks (int): Spectral block partition count.
            sparsity_threshold (float): Soft threshold parameter.
            hard_thresholding_fraction (float): Modes preservation ratio.
            hidden_size_factor (int): Hidden expansion factor.
        """
        super().__init__()
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

        # Scale and shift generator for complex spectral weights (real & imag)
        self.scale_shift = ScaleShiftMlp(
            in_features=mod_dim,
            out_features=2 * hidden_size * hidden_size_factor,
        )

    def forward(self, x: Tensor, t_emb: Tensor) -> Tensor:
        """Forward pass with time-modulated spectral filtering.

        Args:
            x (Tensor): Input tensor of shape (B, H, W, C).
            t_emb (Tensor): Modulation embedding tensor of shape (B, mod_dim).

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

        o1_re = (
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

        o1_im = (
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

        # Scale-shift modulation
        scale_shift_params = self.scale_shift(t_emb)  # (B, 2*C_o1)
        scale_p = scale_shift_params[:, : c * self.hidden_size_factor]
        shift_p = scale_shift_params[:, c * self.hidden_size_factor :]

        scale_view = scale_p.view(
            b,
            1,
            1,
            self.num_blocks,
            self.block_size * self.hidden_size_factor,
        )
        shift_view = shift_p.view(
            b,
            1,
            1,
            self.num_blocks,
            self.block_size * self.hidden_size_factor,
        )

        o1_re = o1_re * (scale_view + 1.0) + shift_view
        o1_im = o1_im * (scale_view + 1.0) + shift_view

        o1_real[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
        ] = F.relu(o1_re)
        o1_imag[
            :,
            total_modes - kept_modes : total_modes + kept_modes,
            :kept_modes,
        ] = F.relu(o1_im)

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


class ModAFNOBlock(nn.Module):
    """Transformer-style block with modulated spectral mixer and modulated MLP."""

    def __init__(
        self,
        dim: int,
        mod_dim: int,
        mlp_ratio: float = 2.0,
        drop_rate: float = 0.0,
        num_blocks: int = 1,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ) -> None:
        """Initialize ModAFNOBlock.

        Args:
            dim (int): Hidden token dimension.
            mod_dim (int): Modulation feature vector dimension.
            mlp_ratio (float): Hidden expansion ratio in feedforward layer.
            drop_rate (float): Dropout probability.
            num_blocks (int): Spectral block partition count.
            sparsity_threshold (float): Sparsity threshold for spectral filter.
            hard_thresholding_fraction (float): Mode preservation ratio.
        """
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.filter = ModAFNO2DLayer(
            hidden_size=dim,
            mod_dim=mod_dim,
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

    def forward(self, x: Tensor, t_emb: Tensor) -> Tensor:
        """Forward pass.

        Args:
            x (Tensor): Input tensor of shape (B, H, W, C).
            t_emb (Tensor): Modulation tensor of shape (B, mod_dim).

        Returns:
            Tensor: Output tensor of shape (B, H, W, C).
        """
        x = x + self.filter(self.norm1(x), t_emb)
        x = x + self.mlp(self.norm2(x))
        return x


class ModAFNO(nn.Module):
    """Complete Modulated Adaptive Fourier Neural Operator model."""

    def __init__(
        self,
        inp_shape: tuple[int, int] = (720, 1440),
        in_channels: int = 155,
        out_channels: int = 73,
        embed_dim: int = 512,
        mod_dim: int = 64,
        patch_size: tuple[int, int] = (2, 2),
        depth: int = 12,
        num_blocks: int = 1,
        mlp_ratio: float = 2.0,
        drop_rate: float = 0.0,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
        embed_method: Literal["sinusoidal", "onehot"] = "sinusoidal",
        embed_dim_t: int = 64,
        **kwargs: object,
    ) -> None:
        """Initialize ModAFNO model.

        Args:
            inp_shape (Tuple[int, int]): Input spatial grid shape (H, W).
            in_channels (int): Input channel count (73+73+3+6=155).
            out_channels (int): Output atmospheric variable count (73).
            embed_dim (int): Latent token embedding dimension.
            mod_dim (int): Modulation feature vector dimension.
            patch_size (Tuple[int, int]): 2D spatial patch partition size.
            depth (int): Number of modulated Fourier blocks.
            num_blocks (int): Number of spectral block partitions.
            mlp_ratio (float): Hidden expansion ratio.
            drop_rate (float): Dropout probability.
            sparsity_threshold (float): Frequency sparsity threshold.
            hard_thresholding_fraction (float): Mode preservation ratio.
            embed_method (Literal["sinusoidal", "onehot"]): Timestep embedding method.
            embed_dim_t (int): Dimensionality of time embedding.
            **kwargs: Extra unused compatibility arguments.
        """
        super().__init__()
        self.inp_shape = inp_shape
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.patch_size = patch_size
        self.embed_dim = embed_dim

        self.mod_embed = ModEmbedNet(
            max_time=1.0,
            dim=embed_dim_t,
            depth=1,
            method=embed_method,
        )

        self.patch_embed = PatchEmbed(
            img_size=inp_shape,
            patch_size=patch_size,
            in_channels=in_channels,
            embed_dim=embed_dim,
        )

        self.blocks = nn.ModuleList(
            [
                ModAFNOBlock(
                    dim=embed_dim,
                    mod_dim=embed_dim_t,
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

    def forward(self, x: Tensor, t: Tensor) -> Tensor:
        """Forward pass for continuous time-modulated prediction.

        Args:
            x (Tensor): Input tensor of shape (B, in_channels, H, W).
            t (Tensor): Normalized time offset tensor in [0, 1] of shape (B,) or (B, 1).

        Returns:
            Tensor: Output forecast tensor of shape (B, out_channels, H, W).
        """
        b, _, h, w = x.shape
        t_emb = self.mod_embed(t)
        x_tokens = self.patch_embed(x)

        for block in self.blocks:
            x_tokens = block(x_tokens, t_emb)

        out_tokens = self.head(x_tokens)
        h_p, w_p = self.patch_embed.h_patches, self.patch_embed.w_patches
        p0, p1 = self.patch_size

        out = out_tokens.view(b, h_p, w_p, self.out_channels, p0, p1)
        out = out.permute(0, 3, 1, 4, 2, 5).contiguous()
        return out.view(b, self.out_channels, h, w)
