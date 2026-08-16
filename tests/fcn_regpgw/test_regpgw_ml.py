"""Unit tests for RegPGW ML infrastructure and workflows.

Tests regional domain boundary extraction, sponge zones, RegPGW datasets,
neural architectures, PyTorch Lightning training module, global FCN driving
inference, coupled predictions, ONNX export, and regional plotting.
"""

from pathlib import Path
from typing import Any

import numpy as np
import torch

from fcn_regpgw.config import (
    RegPGWModelConfig,
    RegPGWTrainConfig,
)
from fcn_regpgw.data.boundary_extractor import BoundaryExtractor, SpongeLayer
from fcn_regpgw.data.regional_dataset import (
    RegPGWDataset,
    create_regpgw_dataloader,
)
from fcn_regpgw.inference.engine import BaseInferenceEngine
from fcn_regpgw.inference.regpgw_predictor import (
    RegPGWOneWayDownscaler,
    RegPGWPredictor,
    RegPGWTwoWayCoupler,
)
from fcn_regpgw.models.global_fcn import GlobalFCNDrivingModel
from fcn_regpgw.models.regpgw_lightning import RegPGWLightningModule
from fcn_regpgw.models.regpgw_net import RegPGWNet
from fcn_regpgw.visual.regional_plotter import RegionalWeatherPlotter
from fcn_regpgw.workflows.regpgw_export_runner import RegPGWExportRunner


class DummyEngine(BaseInferenceEngine):
    """Dummy engine for fast inference testing."""

    def __init__(self, out_channels: int = 73) -> None:
        self.model_path = Path("dummy")
        self.device = "cpu"
        self.out_channels = out_channels

    def predict(
        self, x: torch.Tensor | np.ndarray, **kwargs: Any
    ) -> np.ndarray:
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().numpy()
        b = x.shape[0]
        h, w = x.shape[-2], x.shape[-1]
        return np.ones((b, self.out_channels, h, w), dtype=np.float32)


def test_boundary_extractor_and_sponge_layer():
    """Test boundary extraction from global fields and sponge weights."""
    bounds = (10, 30, 20, 50)  # H_reg=20, W_reg=30
    extractor = BoundaryExtractor(bounds=bounds, boundary_width=4)

    global_field = np.zeros((73, 100, 100), dtype=np.float32)
    global_field[:, 10:30, 20:50] = 5.0

    reg_crop = extractor.crop_regional_domain(global_field)
    assert reg_crop.shape == (73, 20, 30)
    assert np.allclose(reg_crop, 5.0)

    # Paste back
    new_reg = np.ones((73, 20, 30), dtype=np.float32) * 9.0
    pasted = extractor.paste_regional_to_global(global_field, new_reg)
    assert pasted[:, 15, 25].mean() == 9.0
    assert pasted[:, 0, 0].mean() == 0.0

    # Sponge layer
    sponge = SpongeLayer(height=20, width=30, boundary_width=4)
    mask = sponge.mask
    assert mask.shape == (20, 30)
    # Edge is 1, center is 0
    assert mask[0, 0] == 1.0
    assert mask[10, 15] == 0.0

    # Blend
    reg_state = np.ones((73, 20, 30), dtype=np.float32) * 2.0
    bdry_forcing = np.ones((73, 20, 30), dtype=np.float32) * 10.0
    blended = sponge.blend_boundary(reg_state, bdry_forcing)
    assert blended[:, 0, 0].mean() == 10.0
    assert blended[:, 10, 15].mean() == 2.0


def test_regpgw_dataset_and_dataloader():
    """Test RegPGWDataset item indexing and dataloader batching."""
    seq = np.random.randn(5, 73, 16, 16).astype(np.float32)
    static = np.random.randn(6, 16, 16).astype(np.float32)

    dataset = RegPGWDataset(states=seq, static_features=static, lead_steps=1)
    assert len(dataset) == 4

    inputs, targets = dataset[0]
    # Inputs: 73 (state_t) + 73 (bdry_t1) + 6 (static) = 152
    assert inputs.shape == (152, 16, 16)
    assert targets.shape == (73, 16, 16)

    loader = create_regpgw_dataloader(dataset, batch_size=2, shuffle=False)
    b_in, b_tgt = next(iter(loader))
    assert b_in.shape == (2, 152, 16, 16)
    assert b_tgt.shape == (2, 73, 16, 16)


def test_regpgw_net_and_lightning_module():
    """Test RegPGWNet forward pass and Lightning Module training step."""
    model = RegPGWNet(
        in_channels=152,
        out_channels=73,
        hidden_dim=32,
        num_blocks=2,
        use_residual=True,
    )
    x = torch.randn(2, 152, 16, 16)
    out = model(x)
    assert out.shape == (2, 73, 16, 16)

    lightning_module = RegPGWLightningModule(
        model=model,
        train_cfg=RegPGWTrainConfig(batch_size=2, learning_rate=1e-3),
        boundary_width=3,
    )

    targets = torch.randn(2, 73, 16, 16)
    loss = lightning_module.training_step((x, targets), batch_idx=0)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0.0

    val_loss = lightning_module.validation_step((x, targets), batch_idx=0)
    assert isinstance(val_loss, torch.Tensor)


def test_global_fcn_and_regpgw_coupling(tmp_path: Path):
    """Test Global FCN driving rollout, 1-way downscaling, and 2-way coupling."""
    bounds = (10, 30, 20, 50)
    global_engine = DummyEngine(out_channels=73)
    global_model = GlobalFCNDrivingModel(
        regional_bounds=bounds, engine=global_engine
    )

    init_global = np.ones((73, 100, 100), dtype=np.float32)
    glob_traj, bdry_traj = global_model.run_global_rollout(
        initial_state=init_global, total_hours=12, step_hours=6
    )
    assert glob_traj.shape == (3, 73, 100, 100)
    assert bdry_traj.shape == (3, 73, 20, 30)

    # RegPGW Predictor
    reg_engine = DummyEngine(out_channels=73)
    reg_predictor = RegPGWPredictor(
        engine=reg_engine,
        height=20,
        width=30,
        boundary_width=3,
    )
    reg_step = reg_predictor.predict_step(
        regional_state_t=np.zeros((73, 20, 30), dtype=np.float32),
        boundary_forcing_t1=np.ones((73, 20, 30), dtype=np.float32),
    )
    assert reg_step.shape == (73, 20, 30)

    # One-way downscaling
    downscaler = RegPGWOneWayDownscaler(
        global_model=global_model,
        regpgw_predictor=reg_predictor,
        save_dir=tmp_path / "oneway",
    )
    oneway_traj = downscaler.run(
        initial_global_state=init_global, total_hours=12, step_hours=6
    )
    assert oneway_traj.shape == (3, 73, 20, 30)

    # Two-way coupling
    coupler = RegPGWTwoWayCoupler(
        global_model=global_model,
        regpgw_predictor=reg_predictor,
        extractor=BoundaryExtractor(bounds=bounds),
        save_dir=tmp_path / "twoway",
    )
    c_glob, c_reg = coupler.run(
        initial_global_state=init_global, total_hours=12, step_hours=6
    )
    assert c_glob.shape == (3, 73, 100, 100)
    assert c_reg.shape == (3, 73, 20, 30)


def test_regional_weather_plotter(tmp_path: Path):
    """Test regional 850 hPa wind and comparison plotting."""
    plotter = RegionalWeatherPlotter(output_dir=tmp_path / "plots", dpi=100)
    state = np.random.randn(73, 24, 24).astype(np.float32) * 5.0

    p1 = plotter.plot_850hpa_wind_speed(regional_state=state, lead_hour=6)
    assert p1.exists()

    p2 = plotter.plot_comparison(
        global_subgrid=state, regpgw_grid=state * 1.1, lead_hour=6
    )
    assert p2.exists()


def test_regpgw_export_runner(tmp_path: Path):
    """Test ONNX model export for RegPGW architecture."""
    model = RegPGWNet(
        in_channels=152,
        out_channels=73,
        hidden_dim=16,
        num_blocks=2,
    )
    export_path = tmp_path / "RegPGW+LS+Res.onnx"
    runner = RegPGWExportRunner(
        output_path=export_path,
        model_cfg=RegPGWModelConfig(in_channels=152, out_channels=73),
    )
    out_onnx = runner.export(
        model_or_ckpt=model, spatial_shape=(16, 16), opset_version=17
    )
    assert out_onnx.exists()
    assert out_onnx.stat().st_size > 0
