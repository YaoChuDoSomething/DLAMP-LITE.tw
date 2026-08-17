"""Standardization and normalization utilities for atmospheric fields in FCN-RegPGW.

Provides z-score scaling (mean/standard deviation) and inverse denormalization
for multi-channel meteorological forecast grids.
"""

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class GlobalStandardizer:
    """Z-score standardizer for multi-channel atmospheric data."""

    def __init__(
        self,
        means: np.ndarray,
        stds: np.ndarray,
        epsilon: float = 1e-6,
    ) -> None:
        """Initialize standardizer with precomputed means and standard deviations.

        Args:
            means (np.ndarray): Mean statistics per variable channel.
            stds (np.ndarray): Standard deviation statistics per variable
                channel.
            epsilon (float): Small constant to avoid zero-division.
        """
        self.means = np.asarray(means, dtype=np.float32)
        self.stds = np.asarray(stds, dtype=np.float32)
        self.epsilon = epsilon

        # Ensure non-zero standard deviations
        self.stds = np.where(self.stds < self.epsilon, 1.0, self.stds)

    @classmethod
    def from_files(
        cls,
        means_path: str | Path,
        stds_path: str | Path,
        num_channels: int | None = 73,
    ) -> "GlobalStandardizer":
        """Load standardizer from .npy files.

        Args:
            means_path (Union[str, Path]): Path to global_means.npy.
            stds_path (Union[str, Path]): Path to global_stds.npy.
            num_channels (Optional[int]): Number of channels to extract from
                leading dimension. Defaults to 73.

        Returns:
            GlobalStandardizer: Initialized standardizer instance.

        Raises:
            FileNotFoundError: If statistics files do not exist.
        """
        m_path = Path(means_path)
        s_path = Path(stds_path)
        if not m_path.is_file():
            raise FileNotFoundError(f"Means file not found: {m_path}")
        if not s_path.is_file():
            raise FileNotFoundError(f"Stds file not found: {s_path}")

        logger.info("Loading standardization statistics from %s and %s", m_path, s_path)
        means = np.load(m_path)
        stds = np.load(s_path)

        # Slice to requested channels if higher-dimensional
        if means.ndim == 4:
            # (1, C, H, W) or (1, C, 1, 1)
            means = means[0, :num_channels, :, :] if num_channels else means[0]
            stds = stds[0, :num_channels, :, :] if num_channels else stds[0]
        elif means.ndim == 3 and num_channels:
            means = means[:num_channels, :, :]
            stds = stds[:num_channels, :, :]

        return cls(means=means, stds=stds)

    @classmethod
    def compute_from_samples(
        cls,
        samples: Sequence[np.ndarray],
    ) -> "GlobalStandardizer":
        """Compute mean and standard deviation statistics from a collection of arrays.

        Args:
            samples (Sequence[np.ndarray]): List of arrays with shape (C, H, W).

        Returns:
            GlobalStandardizer: Fitted standardizer instance.
        """
        stacked = np.stack(samples, axis=0)  # (N, C, H, W)
        # Compute mean across sample, H, and W axes per channel
        means = np.mean(stacked, axis=(0, 2, 3), keepdims=True)  # (1, C, 1, 1)
        stds = np.std(stacked, axis=(0, 2, 3), keepdims=True)  # (1, C, 1, 1)
        return cls(means=means, stds=stds)

    def transform(self, data: np.ndarray) -> np.ndarray:
        """Normalize atmospheric data with (x - mean) / std.

        Args:
            data (np.ndarray): Data array of shape (C, H, W) or (B, C, H, W).

        Returns:
            np.ndarray: Normalized array with identical shape.
        """
        return ((data - self.means) / self.stds).astype(np.float32)

    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """Denormalize atmospheric data with (x * std) + mean.

        Args:
            data (np.ndarray): Normalized data array.

        Returns:
            np.ndarray: Physical scale atmospheric data array.
        """
        return (data * self.stds + self.means).astype(np.float32)

    def save(
        self,
        means_path: str | Path,
        stds_path: str | Path,
    ) -> None:
        """Save mean and standard deviation arrays to disk.

        Args:
            means_path (Union[str, Path]): Target output path for means.
            stds_path (Union[str, Path]): Target output path for stds.
        """
        ensure_dir(Path(means_path).parent)
        ensure_dir(Path(stds_path).parent)
        save_numpy_atomic(means_path, self.means)
        save_numpy_atomic(stds_path, self.stds)
        logger.info("Saved standardizer statistics to %s and %s", means_path, stds_path)
