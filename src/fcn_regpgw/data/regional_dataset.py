"""Regional datasets and DataLoaders for RegPGW model training.

Defines PyTorch Dataset classes for boundary-conditioned regional atmospheric
prognostic modeling, loading paired regional state sequences, driving boundary
forcing fields, and static geographical masks.
"""


import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from fcn_regpgw.const import (
    NUM_STATIC_CHANNELS,
)


class RegPGWDataset(Dataset):
    """PyTorch Dataset for boundary-conditioned RegPGW training.

    Yields training pairs:
        inputs: (152, H_reg, W_reg) -> [0..73: state_t, 73..146: bdry_t1, 146..152: static]
        targets: (73, H_reg, W_reg) -> [0..73: state_t1]

    Attributes:
        states (List[np.ndarray]): List of regional state arrays of shape (T, 73, H, W).
        boundaries (List[np.ndarray]): List of driving boundary forcing arrays (T, 73, H, W).
        static_features (np.ndarray): 6-channel static features of shape (6, H, W).
        lead_steps (int): Step interval (default: 1 step).
    """

    def __init__(
        self,
        states: list[np.ndarray] | np.ndarray,
        boundaries: list[np.ndarray] | np.ndarray | None = None,
        static_features: np.ndarray | None = None,
        lead_steps: int = 1,
    ) -> None:
        """Initialize RegPGWDataset.

        Args:
            states (Union[List[np.ndarray], np.ndarray]): Sequences of regional states.
            boundaries (Optional[Union[List[np.ndarray], np.ndarray]]): Sequences
                of driving boundary fields from global model or reanalysis.
                If None, uses states directly.
            static_features (Optional[np.ndarray]): Static channel array of
                shape (6, H, W). If None, initializes zero channels.
            lead_steps (int): Prediction lead time step delta.
        """
        if isinstance(states, np.ndarray):
            self.states = [states]
        else:
            self.states = list(states)

        if boundaries is None:
            self.boundaries = self.states
        elif isinstance(boundaries, np.ndarray):
            self.boundaries = [boundaries]
        else:
            self.boundaries = list(boundaries)

        self.lead_steps = lead_steps

        # Index mapping: (sequence_idx, time_idx)
        self.indices: list[tuple[int, int]] = []
        for seq_idx, seq in enumerate(self.states):
            total_time = seq.shape[0]
            for t in range(total_time - self.lead_steps):
                self.indices.append((seq_idx, t))

        # Setup static features
        _, _, h, w = self.states[0].shape
        if static_features is not None:
            self.static_features = static_features.astype(np.float32)
        else:
            self.static_features = np.zeros(
                (NUM_STATIC_CHANNELS, h, w), dtype=np.float32
            )

    def __len__(self) -> int:
        """Get dataset size.

        Returns:
            int: Total number of valid transition pairs.
        """
        return len(self.indices)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Fetch a single input-target sample pair.

        Args:
            idx (int): Sample index.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: (inputs, targets) tensors.
        """
        seq_idx, t = self.indices[idx]
        t_next = t + self.lead_steps

        # Current regional state: (73, H, W)
        state_t = self.states[seq_idx][t].astype(np.float32)
        # Driving boundary forcing at next step: (73, H, W)
        bdry_t1 = self.boundaries[seq_idx][t_next].astype(np.float32)
        # Target regional state at next step: (73, H, W)
        target_t1 = self.states[seq_idx][t_next].astype(np.float32)

        # Concatenate into input tensor: 73 + 73 + 6 = 152 channels
        inputs = np.concatenate(
            [state_t, bdry_t1, self.static_features], axis=0
        )

        return (
            torch.from_numpy(inputs),
            torch.from_numpy(target_t1),
        )


def create_regpgw_dataloader(
    dataset: RegPGWDataset,
    batch_size: int = 4,
    shuffle: bool = True,
    num_workers: int = 2,
    pin_memory: bool = True,
) -> DataLoader:
    """Factory for building standard PyTorch DataLoader for RegPGW.

    Args:
        dataset (RegPGWDataset): RegPGWDataset instance.
        batch_size (int): Mini-batch size.
        shuffle (bool): Whether to randomize sample order.
        num_workers (int): Number of DataLoader subprocesses.
        pin_memory (bool): Whether to pin memory for fast GPU transfer.

    Returns:
        DataLoader: Configured PyTorch DataLoader instance.
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
    )
