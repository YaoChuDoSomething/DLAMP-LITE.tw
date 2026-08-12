"""Architecture tests for GlideUnet model."""

import torch
from dlamp.models.glide_unet import GlideUnetModel


def test_glide_unet_forward_pass() -> None:
    """Test forward pass of GlideUnet model."""
    model = GlideUnetModel(input_shape=(3, 256, 256))
    x = torch.randn(1, 3, 256, 256)
    out = model(x)
    assert out.shape == (1, 3, 256, 256)


def test_glide_unet_loss_computation() -> None:
    """Test loss computation for GlideUnet model."""
    model = GlideUnetModel(input_shape=(3, 256, 256))
    x = torch.randn(1, 3, 256, 256)
    y = torch.randn(1, 3, 256, 256)
    loss = model(x, y)
    assert loss is not None
    assert isinstance(loss, torch.Tensor)
    assert loss.dim() == 0
