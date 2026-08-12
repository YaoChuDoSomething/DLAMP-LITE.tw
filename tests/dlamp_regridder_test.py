"""Tests for DLAMP Regridder module."""


import torch
from dlamp.regridder import DLAMPRegenerator


def test_regridder_interpolates_image() -> None:
    """Test DLAMP Regenerator interpolates image coordinates."""
    regenerator = DLAMPRegenerator()
    # Mock input tensor
    x = torch.randn(1, 3, 128, 128)
    # Test that regridding produces valid output
    y = regenerator.regrid(x)
    assert y is not None
    assert y.shape == (1, 3, 128, 128)
