"""Unit tests for high-level workflow runners, dataset loaders, and plotters."""

from pathlib import Path

import numpy as np

from fcn_regpgw.config import DataConfig
from fcn_regpgw.data.dataset import (
    WeatherForecastDataset,
    create_dataloader,
)
from fcn_regpgw.inference.engine import PyTorchInferenceEngine
from fcn_regpgw.inference.fcnv2_predictor import FCNv2Predictor
from fcn_regpgw.models.afno import AFNO
from fcn_regpgw.visual.plotter import WeatherPlotter
from fcn_regpgw.workflows.data_prep_runner import DataPrepRunner
from fcn_regpgw.workflows.data_stats_runner import DataStatsRunner


def test_data_prep_runner(tmp_path: Path) -> None:
    """Verify DataPrepRunner builds static features array."""
    cfg = DataConfig(data_dir=tmp_path, lat_size=18, lon_size=36)
    runner = DataPrepRunner(cfg)
    out_file = runner.run()

    assert out_file.is_file()
    arr = np.load(out_file)
    assert arr.shape == (6, 18, 36)


def test_data_stats_runner(tmp_path: Path) -> None:
    """Verify DataStatsRunner computes and saves mean and standard deviation."""
    samples = [
        np.random.randn(73, 18, 36).astype(np.float32) for _ in range(3)
    ]
    cfg = DataConfig(data_dir=tmp_path)
    runner = DataStatsRunner(cfg)
    _ = runner.run_from_samples(samples, output_dir=tmp_path)

    assert (tmp_path / "global_means.npy").is_file()
    assert (tmp_path / "global_stds.npy").is_file()


def test_forecast_dataset_and_dataloader() -> None:
    """Verify WeatherForecastDataset creates valid PyTorch training batches."""
    samples = [
        np.random.randn(73, 16, 32).astype(np.float32) for _ in range(5)
    ]
    ds = WeatherForecastDataset(samples=samples, lead_steps=1)
    loader = create_dataloader(ds, batch_size=2, shuffle=False, num_workers=0)

    for x, y in loader:
        assert x.shape == (2, 73, 16, 32)
        assert y.shape == (2, 73, 16, 32)
        break


def test_fcnv2_predictor_workflow(tmp_path: Path) -> None:
    """Verify FCNv2Predictor multi-step autoregressive rollout."""
    model = AFNO(
        inp_shape=(16, 32),
        in_channels=73,
        out_channels=73,
        patch_size=(2, 2),
        embed_dim=32,
        depth=1,
        num_blocks=1,
    )
    engine = PyTorchInferenceEngine(model=model, device="cpu")
    predictor = FCNv2Predictor(engine=engine, apply_lat_flip=True)

    ic = np.random.randn(73, 16, 32).astype(np.float32)
    saved = predictor.run_forecast(
        initial_condition=ic,
        forecast_hours=12,
        step_hours=6,
        output_dir=tmp_path,
    )

    assert len(saved) == 3  # 000h, 006h, 012h
    for p in saved:
        assert p.is_file()


def test_weather_plotter(tmp_path: Path) -> None:
    """Verify WeatherPlotter generates output PNG figure."""
    plotter = WeatherPlotter(lat_size=18, lon_size=36)
    dummy_data = np.random.randn(73, 18, 36).astype(np.float32)

    out_png = tmp_path / "wind_850.png"
    plotter.plot_wind_speed_850(
        weather_data=dummy_data,
        lead_hour=6,
        output_file=out_png,
    )
    assert out_png.is_file()
    assert out_png.stat().st_size > 0
