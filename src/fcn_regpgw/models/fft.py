"""Fourier Transform neural layers and helpers for Fourier Neural Operators.

Provides real-to-complex and complex-to-real 2D Fast Fourier Transforms
compatible with PyTorch and ONNX export.
"""


import torch
import torch.fft
from torch import Tensor


def rfft2(
    x: Tensor,
    s: tuple[int, int] | None = None,
    dim: tuple[int, int] = (-2, -1),
    norm: str | None = None,
) -> Tensor:
    """Compute 2-dimensional Real Fast Fourier Transform.

    Args:
        x (Tensor): Real-valued input tensor of shape (..., H, W).
        s (Optional[Tuple[int, int]]): Signal size in transformed dimensions.
        dim (Tuple[int, int]): Dimensions along which to compute FFT.
        norm (Optional[str]): Normalization mode ('forward', 'backward', 'ortho').

    Returns:
        Tensor: Complex-valued frequency domain tensor.
    """
    return torch.fft.rfft2(x, s=s, dim=dim, norm=norm)


def irfft2(
    x: Tensor,
    s: tuple[int, int] | None = None,
    dim: tuple[int, int] = (-2, -1),
    norm: str | None = None,
) -> Tensor:
    """Compute 2-dimensional Inverse Real Fast Fourier Transform.

    Args:
        x (Tensor): Complex-valued frequency domain tensor.
        s (Optional[Tuple[int, int]]): Target real spatial shape (H, W).
        dim (Tuple[int, int]): Dimensions along which to compute inverse FFT.
        norm (Optional[str]): Normalization mode ('forward', 'backward', 'ortho').

    Returns:
        Tensor: Real-valued reconstructed spatial tensor.
    """
    return torch.fft.irfft2(x, s=s, dim=dim, norm=norm)


def real(x: Tensor) -> Tensor:
    """Extract real component of a complex tensor.

    Args:
        x (Tensor): Complex tensor.

    Returns:
        Tensor: Real part tensor.
    """
    return torch.real(x)


def imag(x: Tensor) -> Tensor:
    """Extract imaginary component of a complex tensor.

    Args:
        x (Tensor): Complex tensor.

    Returns:
        Tensor: Imaginary part tensor.
    """
    return torch.imag(x)


def view_as_complex(x: Tensor) -> Tensor:
    """View real tensor with last dimension 2 as complex tensor.

    Args:
        x (Tensor): Real tensor where x.shape[-1] == 2.

    Returns:
        Tensor: Complex tensor with last dimension removed.
    """
    return torch.view_as_complex(x)
