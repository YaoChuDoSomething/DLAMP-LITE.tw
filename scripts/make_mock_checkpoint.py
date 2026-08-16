#!/usr/bin/env python
"""Create a random-weight (unconverged) Pangu checkpoint for mock MVP use.

The checkpoint is structurally valid (lightning schema: ``state_dict`` +
``hyper_parameters``) so that ``PanguLightningModule.load_from_checkpoint``
and ``load_pangu_model`` accept it, but the weights are never trained.
It is a garbage-in/garbage-out placeholder used only to exercise the
checkpoint -> ONNX -> inference workflow end to end without real data.

Usage:
    python scripts/make_mock_checkpoint.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import lightning as L
import omegaconf
import torch
import yaml
from omegaconf import OmegaConf

from dlamp.const import CHECKPOINT_DIR, REPO_ROOT
from dlamp.models.builders.pangu_builder import PanguBuilder
from dlamp.utils import DataCompose

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("make_mock_checkpoint")

MODEL_CODE = "20250627"
OUT_CKPT = Path(CHECKPOINT_DIR) / "Pangu_250627_000000-epoch=000-val_loss_epoch=1.0000.ckpt"


def to_plain(obj):
    """Recursively convert OmegaConf/lightning containers to plain Python."""
    if isinstance(obj, (omegaconf.DictConfig, omegaconf.ListConfig)):
        return OmegaConf.to_container(obj, resolve=True)
    if isinstance(obj, dict):
        return {str(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    return obj


def main() -> None:
    with open(REPO_ROOT / "config" / "data" / f"rwrf_{MODEL_CODE}.yaml") as stream:
        cfg_data = yaml.safe_load(stream)
    with open(REPO_ROOT / "config" / "model" / f"pangu_rwrf_{MODEL_CODE}.yaml") as stream:
        cfg_model = yaml.safe_load(stream)
    with open(REPO_ROOT / "config" / "lightning" / f"pangu_rwrf_{MODEL_CODE}.yaml") as stream:
        cfg_lightning = yaml.safe_load(stream)

    data_list = DataCompose.from_config(cfg_data["train_data"])
    builder = PanguBuilder(
        "mock",
        data_list,
        image_shape=cfg_data["image_shape"],
        add_time_features=cfg_data["add_time_features"],
        **cfg_model,
        **cfg_lightning,
    )
    module = builder.build_model()
    log.info("pressure levels: %d, upper vars: %d, surface vars: %d",
             len(builder.pressure_levels), len(builder.upper_vars), len(builder.surface_vars))

    checkpoint = {
        "state_dict": module.state_dict(),
        "hyper_parameters": to_plain(dict(module.hparams)),
        "pytorch-lightning_version": L.__version__,
    }
    OUT_CKPT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, OUT_CKPT)
    log.info("Saved mock checkpoint: %s (%.2f MB)", OUT_CKPT, OUT_CKPT.stat().st_size / 1e6)


if __name__ == "__main__":
    main()
