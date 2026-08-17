"""Unit tests for neural network architectures and Lightning training module."""

import torch

from fcn_regpgw.models.afno import AFNO
from fcn_regpgw.models.embeddings import (
    ModEmbedNet,
    OneHotEmbedding,
    PositionalEmbedding,
)
from fcn_regpgw.models.lightning_module import FCNRegPGWLightningModule
from fcn_regpgw.models.modafno import ModAFNO
from fcn_regpgw.models.precip_net import PrecipNet


def test_positional_and_onehot_embeddings() -> None:
    """Verify temporal embedding shape and forward pass."""
    pos_emb = PositionalEmbedding(num_channels=32)
    t = torch.tensor([0.0, 0.5, 1.0])
    out_pos = pos_emb(t)
    assert out_pos.shape == (3, 32)

    onehot_emb = OneHotEmbedding(num_channels=16)
    out_onehot = onehot_emb(t)
    assert out_onehot.shape == (3, 16)


def test_mod_embed_net() -> None:
    """Verify ModEmbedNet forward pass."""
    net_sin = ModEmbedNet(dim=32, depth=2, method="sinusoidal")
    t = torch.tensor([0.25, 0.75])
    out_sin = net_sin(t)
    assert out_sin.shape == (2, 32)

    net_onehot = ModEmbedNet(dim=32, depth=1, method="onehot")
    out_oh = net_onehot(t)
    assert out_oh.shape == (2, 32)


def test_afno_forward_shape() -> None:
    """Verify AFNO forward pass produces matching output spatial shape."""
    model = AFNO(
        inp_shape=(32, 64),
        in_channels=10,
        out_channels=5,
        patch_size=(2, 2),
        embed_dim=64,
        depth=2,
        num_blocks=2,
    )
    x = torch.randn(2, 10, 32, 64)
    out = model(x)
    assert out.shape == (2, 5, 32, 64)


def test_modafno_forward_shape() -> None:
    """Verify ModAFNO forward pass with modulation timestep."""
    model = ModAFNO(
        inp_shape=(32, 64),
        in_channels=20,
        out_channels=10,
        patch_size=(2, 2),
        embed_dim=64,
        mod_dim=32,
        depth=2,
        num_blocks=1,
    )
    x = torch.randn(2, 20, 32, 64)
    t = torch.tensor([0.1, 0.5])
    out = model(x, t)
    assert out.shape == (2, 10, 32, 64)


def test_precip_net_forward_shape() -> None:
    """Verify PrecipNet diagnostic prediction output shape."""
    model = PrecipNet(
        inp_shape=(32, 64),
        in_channels=10,
        embed_dim=32,
        depth=2,
        num_blocks=2,
    )
    x = torch.randn(2, 10, 32, 64)
    out = model(x)
    assert out.shape == (2, 1, 32, 64)
    assert torch.all(out >= 0.0)


def test_lightning_module_training_step() -> None:
    """Verify LightningModule forward and loss calculation."""
    base_model = AFNO(
        inp_shape=(16, 32),
        in_channels=4,
        out_channels=4,
        patch_size=(2, 2),
        embed_dim=32,
        depth=1,
        num_blocks=1,
    )
    module = FCNRegPGWLightningModule(model=base_model)

    x = torch.randn(2, 4, 16, 32)
    y = torch.randn(2, 4, 16, 32)
    loss = module.training_step((x, y), batch_idx=0)
    assert loss.ndim == 0
    assert not torch.isnan(loss)
