"""Smoke tests for EarthSpecificBlock and EarthAttention3D.

Uses the correct constructor signatures from the actual implementation.
These are CPU-only shape-preservation tests; no GPU required.

Note: Use small shapes (input_shape=(2,4,4), window_size=(2,2,2)) so
tests run quickly on CPU.
"""

import unittest
from math import prod
from typing import ClassVar

import torch

from dlamp.models.architectures.earth_3d_specifics import (
    EarthAttention3D,
    EarthSpecificBlock,
    EarthSpecificLayer,
)
from dlamp.models.model_utils import window_partition_3d


class EarthAttention3DTest(unittest.TestCase):
    """Shape and bias tests for EarthAttention3D."""

    input_shape: ClassVar[tuple[int, ...]] = (2, 4, 4)
    dim: ClassVar[int] = 4
    heads: ClassVar[int] = 2
    dropout_rate: ClassVar[float] = 0.0
    window_size: ClassVar[tuple[int, ...]] = (2, 2, 2)

    def _build(self) -> EarthAttention3D:
        return EarthAttention3D(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
        )

    def test_earth_specific_bias_coverage(self) -> None:
        """position_index should cover all distinct window-relative positions."""
        attn = self._build()
        total_movement = attn.win_Z**2 * attn.win_H**2 * (2 * attn.win_W - 1)
        self.assertEqual(
            len({x.item() for x in attn.position_index}),
            total_movement,
        )

    def test_output_shape_preserved(self) -> None:
        """EarthAttention3D preserves input window tensor shape."""
        attn = self._build()
        t = torch.randn([1] + list(self.input_shape) + [self.dim])
        win = window_partition_3d(t, self.window_size, combine_img_dim=True)
        out = attn(win)
        self.assertEqual(out.shape, win.shape)


class EarthSpecificBlockTest(unittest.TestCase):
    """Shape tests for EarthSpecificBlock."""

    input_shape: ClassVar[tuple[int, ...]] = (2, 4, 4)
    dim: ClassVar[int] = 4
    heads: ClassVar[int] = 2
    drop_path_ratio: ClassVar[float] = 0.0
    dropout_rate: ClassVar[float] = 0.0
    window_size: ClassVar[tuple[int, ...]] = (2, 2, 2)

    def test_output_shape_no_skip(self) -> None:
        """EarthSpecificBlock (reduce_dim=False) preserves shape."""
        block = EarthSpecificBlock(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            drop_path_ratio=self.drop_path_ratio,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
            is_rolling=False,
            reduce_dim=False,
        )
        seq_len = prod(self.input_shape)
        x = torch.randn(1, seq_len, self.dim)
        out = block(x)
        self.assertEqual(out.shape, x.shape)


class EarthSpecificLayerTest(unittest.TestCase):
    """Shape tests for EarthSpecificLayer."""

    input_shape: ClassVar[tuple[int, ...]] = (2, 4, 4)
    dim: ClassVar[int] = 4
    heads: ClassVar[int] = 2
    depth: ClassVar[int] = 2
    dropout_rate: ClassVar[float] = 0.0
    window_size: ClassVar[tuple[int, ...]] = (2, 2, 2)

    def test_output_shape(self) -> None:
        """EarthSpecificLayer preserves tensor shape across depth."""
        layer = EarthSpecificLayer(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            depth=self.depth,
            drop_path_ratio_list=[0.0] * self.depth,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
            skip_concat=False,
        )
        seq_len = prod(self.input_shape)
        x = torch.randn(1, seq_len, self.dim)
        out = layer(x)
        self.assertEqual(out.shape, x.shape)


if __name__ == "__main__":
    unittest.main()
