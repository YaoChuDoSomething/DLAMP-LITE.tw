"""Architecture tests for Earth 3D Specifics model."""

import torch
from omegaconf import OmegaConf

from dlamp.models.earth_3d_specifics import Earth3DSpecificsModel


def test_earth_3d_specifics_forward_pass() -> None:
    """Test forward pass of Earth3DSpecifics model."""
    model = Earth3DSpecificsModel()
    x = torch.randn(1, 3, 256, 256)
    out = model(x)
    assert out.shape == (1, 3, 256, 256)


def test_earth_3d_specifics_processing() -> None:
    """Test Earth3DSpecifics model processing."""
    model = Earth3DSpecificsModel()
    x = torch.randn(1, 3, 256, 256)
    processed = model.process(x)
    assert processed is not None
