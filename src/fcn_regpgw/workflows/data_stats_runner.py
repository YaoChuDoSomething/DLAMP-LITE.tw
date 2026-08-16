"""Standardization statistics calculation workflow runner for FCN-RegPGW.

Computes multi-channel mean and standard deviation statistics across training
samples and exports them to persistent .npy files.
"""

from collections.abc import Sequence
from pathlib import Path

import numpy as np

from fcn_regpgw.config import DataConfig
from fcn_regpgw.data.standardizer import GlobalStandardizer
from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class DataStatsRunner:
    """Workflow runner for calculating atmospheric field z-score statistics."""

    def __init__(self, config: DataConfig | None = None) -> None:
        """Initialize DataStatsRunner.

        Args:
            config (Optional[DataConfig]): Data configuration settings.
        """
        self.config = config or DataConfig()

    def run_from_samples(
        self,
        samples: Sequence[np.ndarray],
        output_dir: str | Path | None = None,
    ) -> GlobalStandardizer:
        """Compute statistics from a collection of sample arrays and save to disk.

        Args:
            samples (Sequence[np.ndarray]): List of arrays with shape (C, H, W).
            output_dir (Optional[Union[str, Path]]): Destination folder for
                global_means.npy and global_stds.npy.

        Returns:
            GlobalStandardizer: Fitted standardizer instance.
        """
        out_dir = ensure_dir(output_dir or self.config.data_dir)
        logger.info(
            "Computing normalization statistics from %d samples...", len(samples)
        )

        standardizer = GlobalStandardizer.compute_from_samples(samples)
        means_path = out_dir / "global_means.npy"
        stds_path = out_dir / "global_stds.npy"

        standardizer.save(means_path, stds_path)
        logger.info(
            "Saved global means to %s and global stds to %s",
            means_path,
            stds_path,
        )
        return standardizer

    def run_from_directory(
        self,
        input_dir: str | Path,
        output_dir: str | Path | None = None,
        max_files: int | None = None,
    ) -> GlobalStandardizer:
        """Scan directory for .npy weather states and compute z-score statistics.

        Args:
            input_dir (Union[str, Path]): Directory with training weather states.
            output_dir (Optional[Union[str, Path]]): Destination directory.
            max_files (Optional[int]): Optional limit on sample count.

        Returns:
            GlobalStandardizer: Fitted standardizer instance.

        Raises:
            FileNotFoundError: If no .npy files are found in input_dir.
        """
        dir_path = Path(input_dir)
        files = sorted(dir_path.glob("*.npy"))
        if not files:
            raise FileNotFoundError(f"No .npy sample files found in {dir_path}")

        if max_files:
            files = files[:max_files]

        logger.info("Loading %d state files from %s...", len(files), dir_path)
        samples: list[np.ndarray] = [np.load(f) for f in files]
        return self.run_from_samples(samples, output_dir=output_dir)
