"""Synthetic Dataset and DataModule for DLAMP CPU training.

Usage:
    datamodule = SyntheticDataModule(batch_size=32)
"""

import lightning as L
import torch
from torch.utils.data import DataLoader, Dataset


class SyntheticDataset(Dataset[tuple[torch.Tensor, torch.Tensor]]):
    """Synthetic dataset generating random tensors.

    Attributes:
        num_samples (int): Total samples.
        in_features (int): Feature dimension.
        out_features (int): Output dimension.
        x (torch.Tensor): Input features.
        y (torch.Tensor): Targets.
    """

    def __init__(
        self,
        num_samples: int = 100,
        in_features: int = 10,
        out_features: int = 1,
    ) -> None:
        """Initializes SyntheticDataset.

        Args:
            num_samples (int): Number of synthetic samples.
            in_features (int): Input feature size.
            out_features (int): Output feature size.
        """
        super().__init__()
        self.num_samples = num_samples
        self.in_features = in_features
        self.out_features = out_features
        torch.manual_seed(42)
        self.x = torch.randn(num_samples, in_features)
        self.y = torch.randn(num_samples, out_features)

    def __len__(self) -> int:
        """Returns length of dataset.

        Returns:
            int: Total number of samples.
        """
        return self.num_samples

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Gets dataset item by index.

        Args:
            idx (int): Sample index.

        Returns:
            tuple[torch.Tensor, torch.Tensor]: Pair of (x, y).
        """
        return self.x[idx], self.y[idx]


class SyntheticDataModule(L.LightningDataModule):
    """Lightning DataModule for SyntheticDataset.

    Attributes:
        batch_size (int): DataLoader batch size.
        num_samples (int): Number of samples.
        in_features (int): Input feature size.
        out_features (int): Output feature size.
    """

    def __init__(
        self,
        batch_size: int = 32,
        num_samples: int = 100,
        in_features: int = 10,
        out_features: int = 1,
    ) -> None:
        """Initializes SyntheticDataModule.

        Args:
            batch_size (int): Batch size.
            num_samples (int): Total synthetic samples.
            in_features (int): Input feature dimension.
            out_features (int): Output feature dimension.
        """
        super().__init__()
        self.batch_size = batch_size
        self.num_samples = num_samples
        self.in_features = in_features
        self.out_features = out_features

    def train_dataloader(self) -> DataLoader[tuple[torch.Tensor, torch.Tensor]]:
        """Creates training DataLoader.

        Returns:
            DataLoader[tuple[torch.Tensor, torch.Tensor]]: DataLoader instance.
        """
        dataset = SyntheticDataset(
            num_samples=self.num_samples,
            in_features=self.in_features,
            out_features=self.out_features,
        )
        return DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
