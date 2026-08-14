"""Architecture smoke tests for GlideUNet.

Tests forward pass output shape on CPU with minimal channel counts.
"""

import unittest

import torch

from dlamp.models.architectures.glide_unet import GlideUNet


class GlideUNetTest(unittest.TestCase):
    """Shape tests for GlideUNet."""

    def _build(self) -> GlideUNet:
        # hidden_dim must be divisible by GroupNorm default n_groups (32)
        return GlideUNet(
            image_channels=1,
            hidden_dim=32,
            ch_mults=(1, 2),
            is_attn=(False, False),
            n_blocks=1,
        )

    def test_output_shape_matches_input(self) -> None:
        """GlideUNet output (B, C, H, W) matches input spatial dims."""
        model = self._build()
        model.eval()
        B, C, H, W = 1, 1, 8, 8
        x = torch.randn(B, C, H, W)
        t = torch.zeros(B, dtype=torch.long)
        cond = torch.randn(B, C, H, W)
        with torch.no_grad():
            out = model(x, t, cond)
        self.assertEqual(out.shape, (B, C, H, W))

    def test_parameter_count_positive(self) -> None:
        """GlideUNet must have at least one trainable parameter."""
        model = self._build()
        total = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
