"""Tests for src/dlamp modules."""

import torch
from omegaconf import OmegaConf

from dlamp.datamodule import SyntheticDataModule, SyntheticDataset
from dlamp.lightning_module import DLAMPModule
from dlamp.model import SimpleMLP


def test_simple_mlp_forward() -> None:
    """Tests forward pass of SimpleMLP."""
    model = SimpleMLP(in_features=10, hidden_dim=32, out_features=1)
    x = torch.randn(4, 10)
    out = model(x)
    assert out.shape == (4, 1)


def test_dlamp_module() -> None:
    """Tests DLAMP Lightning Module loss computation."""
    module = DLAMPModule(in_features=10, hidden_dim=32, out_features=1)
    x = torch.randn(4, 10)
    y = torch.randn(4, 1)
    loss = module.training_step((x, y), 0)
    assert loss is not None
    assert loss.dim() == 0


def test_synthetic_dataset() -> None:
    """Tests SyntheticDataset length and item shapes."""
    dataset = SyntheticDataset(num_samples=20, in_features=10, out_features=1)
    assert len(dataset) == 20
    x, y = dataset[0]
    assert x.shape == (10,)
    assert y.shape == (1,)


def test_synthetic_datamodule() -> None:
    """Tests SyntheticDataModule dataloader batch shapes."""
    dm = SyntheticDataModule(
        batch_size=8, num_samples=24, in_features=10, out_features=1
    )
    loader = dm.train_dataloader()
    batch_x, batch_y = next(iter(loader))
    assert batch_x.shape == (8, 10)
    assert batch_y.shape == (8, 1)


def test_config_loading() -> None:
    """Tests YAML configuration structure loading."""
    yaml_content = """
    model:
      in_features: 10
      hidden_dim: 32
      out_features: 1
      lr: 0.001
    data:
      batch_size: 32
      num_samples: 100
    trainer:
      max_epochs: 2
      accelerator: "cpu"
      devices: 1
    """
    cfg = OmegaConf.create(yaml_content)
    assert cfg.model.in_features == 10
    assert cfg.trainer.accelerator == "cpu"
