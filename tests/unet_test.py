"""Architecture tests for Unet model."""

import torch
from omegaconf import OmegaConf

from dlamp.models.unet import UnetModel
from dlamp.models.glide_unet import GlideUnetModel
from dlamp.models.earth_3d_specifics import Earth3DSpecificsModel


def test_unet_forward_pass() -> None:
    """Test forward pass of Unet model."""
    model = UnetModel(input_shape=(3, 256, 256))
    x = torch.randn(1, 3, 256, 256)
    out = model(x)
    assert out.shape == (1, 3, 256, 256)


def test_glide_unet_forward_pass() -> None:
    """Test forward pass of GlideUnet model."""
    model = GlideUnetModel(input_shape=(3, 256, 256))
    x = torch.randn(1, 3, 256, 256)
    out = model(x)
    assert out.shape == (1, 3, 256, 256)


def test_earth_3d_specifics_forward_pass() -> None:
    """Test forward pass of Earth3DSpecifics model."""
    model = Earth3DSpecificsModel()
    x = torch.randn(1, 3, 256, 256)
    out = model(x)
    assert out.shape == (1, 3, 256, 256)
