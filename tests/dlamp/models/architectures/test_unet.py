"""Architecture smoke tests for UNet.

Tests forward pass output shape on CPU with minimal channel counts.
"""

import unittest

import torch

from dlamp.models.architectures.unet import UNet


class UNetTest(unittest.TestCase):
    """Shape tests for UNet."""

    def _build(self) -> UNet:
        # n_channels must be divisible by GroupNorm n_groups (default 32)
        return UNet(
            image_channels=1,
            n_channels=32,
            ch_mults=(1, 2),
            is_attn=(False, False),
            n_blocks=1,
        )

    def test_output_shape_matches_input(self) -> None:
        """UNet output (B, C, H, W) matches input spatial dims."""
        model = self._build()
        model.eval()
        B, C, H, W = 1, 1, 8, 8
        x = torch.randn(B, C, H, W)
        t = torch.zeros(B, dtype=torch.long)
        with torch.no_grad():
            out = model(x, t)
        self.assertEqual(out.shape, (B, C, H, W))

    def test_parameter_count_positive(self) -> None:
        """UNet must have at least one trainable parameter."""
        model = self._build()
        total = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
