"""PyTorch Dataset and DataLoader wrappers for FCN-RegPGW training and evaluation.

Provides structured PyTorch Dataset classes for atmospheric forecast pairs and
temporal interpolation sequences.
"""

from collections.abc import Sequence

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from fcn_regpgw.data.masks import StaticMaskProcessor
from fcn_regpgw.data.standardizer import GlobalStandardizer


class WeatherForecastDataset(Dataset):
    """PyTorch Dataset for atmospheric auto-regressive forecast training (x_t -> x_{t+dt})."""

    def __init__(
        self,
        samples: Sequence[np.ndarray],
        standardizer: GlobalStandardizer | None = None,
        lead_steps: int = 1,
    ) -> None:
        """Initialize forecast dataset.

        Args:
            samples (Sequence[np.ndarray]): Sequence of state arrays (C, H, W).
            standardizer (Optional[GlobalStandardizer]): Standardizer for
                normalization.
            lead_steps (int): Step delta between input and target.
        """
        self.samples = samples
        self.standardizer = standardizer
        self.lead_steps = lead_steps

    def __len__(self) -> int:
        """Return dataset size."""
        return max(0, len(self.samples) - self.lead_steps)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Fetch input and target pair (x_t, x_{t+dt}).

        Args:
            idx (int): Sample index.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Normalized input and target
                tensors.
        """
        x_in = self.samples[idx].copy()
        x_tgt = self.samples[idx + self.lead_steps].copy()

        if self.standardizer:
            x_in = self.standardizer.transform(x_in)
            x_tgt = self.standardizer.transform(x_tgt)

        return (
            torch.from_numpy(x_in).float(),
            torch.from_numpy(x_tgt).float(),
        )


class TemporalInterpDataset(Dataset):
    """PyTorch Dataset for ModAFNO temporal interpolation between 6-hour bounds."""

    def __init__(
        self,
        anchor_pairs: Sequence[tuple[np.ndarray, np.ndarray]],
        intermediate_targets: Sequence[np.ndarray],
        timesteps: Sequence[float],
        static_mask_processor: StaticMaskProcessor | None = None,
        standardizer: GlobalStandardizer | None = None,
    ) -> None:
        """Initialize temporal interpolation dataset.

        Args:
            anchor_pairs (Sequence[Tuple[np.ndarray, np.ndarray]]): Pairs of
                (x_0h, x_6h) state arrays.
            intermediate_targets (Sequence[np.ndarray]): Ground truth target
                arrays at interpolated hours.
            timesteps (Sequence[float]): Normalized fractional time offsets in
                [0, 1].
            static_mask_processor (Optional[StaticMaskProcessor]): Processor
                for static channels.
            standardizer (Optional[GlobalStandardizer]): Standardizer for
                normalization.
        """
        self.anchor_pairs = anchor_pairs
        self.intermediate_targets = intermediate_targets
        self.timesteps = timesteps
        self.standardizer = standardizer

        processor = static_mask_processor or StaticMaskProcessor()
        self.static_features = processor.build_static_features()

    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.anchor_pairs)

    def __getitem__(
        self, idx: int
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Fetch composite input tensor, normalized time, and target tensor.

        Args:
            idx (int): Sample index.

        Returns:
            Tuple[torch.Tensor, torch.Tensor, torch.Tensor]: (x_input, t_norm,
                y_target).
        """
        x1, x2 = self.anchor_pairs[idx]
        target = self.intermediate_targets[idx]
        t_val = self.timesteps[idx]

        if self.standardizer:
            x1_norm = self.standardizer.transform(x1)
            x2_norm = self.standardizer.transform(x2)
            tgt_norm = self.standardizer.transform(target)
        else:
            x1_norm, x2_norm, tgt_norm = x1, x2, target

        # 155 channels: 73 (x1) + 73 (x2) + 3 (solar placeholder/actual) + 6 (static)
        solar_dummy = np.zeros(
            (3, x1.shape[1], x1.shape[2]), dtype=np.float32
        )
        composite_input = np.concatenate(
            [x1_norm, x2_norm, solar_dummy, self.static_features],
            axis=0,
        ).astype(np.float32)

        return (
            torch.from_numpy(composite_input).float(),
            torch.tensor([t_val], dtype=torch.float32),
            torch.from_numpy(tgt_norm).float(),
        )


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 4,
    shuffle: bool = True,
    num_workers: int = 2,
) -> DataLoader:
    """Create a configured PyTorch DataLoader.

    Args:
        dataset (Dataset): Target dataset.
        batch_size (int): Batch size.
        shuffle (bool): Whether to shuffle data.
        num_workers (int): Parallel worker process count.

    Returns:
        DataLoader: Configured DataLoader instance.
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
