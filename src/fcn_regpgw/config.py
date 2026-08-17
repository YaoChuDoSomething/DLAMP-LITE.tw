"""Configuration data structures for FCN-RegPGW modeling.

Provides immutable dataclasses for configuring global FourCastNet driving
inference, RegPGW regional data preparation, training, inference, coupling,
and visualization.
"""

import os
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from fcn_regpgw.const import (
    DEFAULT_BOUNDARY_WIDTH,
    DEFAULT_GLOBAL_LAT_SIZE,
    DEFAULT_GLOBAL_LON_SIZE,
    DEFAULT_REGIONAL_BOUNDS,
    DEFAULT_REGIONAL_LAT_SIZE,
    DEFAULT_REGIONAL_LON_SIZE,
    NUM_REGPGW_INPUT_CHANNELS,
    NUM_REGPGW_OUTPUT_CHANNELS,
)


@dataclass(frozen=True)
class RegPGWDataConfig:
    """Configuration for RegPGW regional dataset and boundary preparation.

    Attributes:
        data_dir (Path): Directory containing raw meteorological data.
        output_dir (Path): Directory where processed regional tensors are saved.
        stats_dir (Path): Directory for storing regional z-score statistics.
        land_sea_mask_path (Optional[Path]): Path to LSM mask file.
        orography_path (Optional[Path]): Path to topography/orography mask file.
        regional_bounds (Tuple[int, int, int, int]): Slice bounds
            (lat_min, lat_max, lon_min, lon_max) on the global grid.
        boundary_width (int): Number of lateral grid cells for sponge boundary.
        regional_lat_size (int): Latitude grid points of regional domain.
        regional_lon_size (int): Longitude grid points of regional domain.
        global_lat_size (int): Latitude grid points of driving global model.
        global_lon_size (int): Longitude grid points of driving global model.
        lat_size (int): Alias for global_lat_size.
        lon_size (int): Alias for global_lon_size.
        sponge_decay (float): Exponential decay factor for lateral sponge zone.
    """

    data_dir: Path = Path("/wk2/yaochu/CASE_DATA/Pool/")
    output_dir: Path = Path("data/regpgw_processed")
    stats_dir: Path = Path("assets/regpgw_standardization")
    land_sea_mask_path: Path | None = None
    orography_path: Path | None = None
    regional_bounds: tuple[int, int, int, int] = DEFAULT_REGIONAL_BOUNDS
    boundary_width: int = DEFAULT_BOUNDARY_WIDTH
    regional_lat_size: int = DEFAULT_REGIONAL_LAT_SIZE
    regional_lon_size: int = DEFAULT_REGIONAL_LON_SIZE
    global_lat_size: int = DEFAULT_GLOBAL_LAT_SIZE
    global_lon_size: int = DEFAULT_GLOBAL_LON_SIZE
    lat_size: int = DEFAULT_GLOBAL_LAT_SIZE
    lon_size: int = DEFAULT_GLOBAL_LON_SIZE
    sponge_decay: float = 0.5


# Backward-compatible alias
DataConfig = RegPGWDataConfig


@dataclass(frozen=True)
class RegPGWModelConfig:
    """Configuration for RegPGW regional neural network architecture."""

    in_channels: int = NUM_REGPGW_INPUT_CHANNELS
    out_channels: int = NUM_REGPGW_OUTPUT_CHANNELS
    hidden_dim: int = 128
    num_blocks: int = 8
    patch_size: tuple[int, int] = (2, 2)
    embed_dim: int = 256
    num_blocks_fourier: int = 8
    dropout: float = 0.05
    use_boundary_conditioning: bool = True
    use_residual_connection: bool = True
    backbone_type: str = "conv"


# Backward-compatible alias
ModelConfig = RegPGWModelConfig


@dataclass(frozen=True)
class RegPGWTrainConfig:
    """Configuration for RegPGW model training workflow."""

    batch_size: int = 4
    num_workers: int = 4
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 100
    warmup_epochs: int = 5
    interior_loss_weight: float = 1.0
    boundary_loss_weight: float = 2.0
    physics_loss_weight: float = 0.1
    checkpoint_dir: Path = Path("checkpoints/regpgw")
    log_dir: Path = Path("outputs/lightning_logs")
    val_check_interval: float = 1.0
    precision: str = "16-mixed"


# Backward-compatible alias
TrainConfig = RegPGWTrainConfig


@dataclass(frozen=True)
class GlobalFCNInferenceConfig:
    """Configuration for pre-trained global FourCastNet driving inference."""

    model_path: Path = Path("weight/fcnv2_sm.onnx")
    device: str = "cuda"
    forecast_hours: int = 240
    step_hours: int = 6
    engine_type: str = "onnx"


@dataclass(frozen=True)
class RegPGWInferenceConfig:
    """Configuration for RegPGW regional inference & coupled execution."""

    model_path: Path = Path("weight/RegPGW+LS+Res.onnx")
    device: str = "cuda"
    coupling_mode: str = "two_way"
    step_hours: int = 1
    save_dir: Path = Path("outputs/regpgw_forecast")
    feedback_weight: float = 0.8


# Backward-compatible alias
InferenceConfig = RegPGWInferenceConfig


@dataclass(frozen=True)
class PlotConfig:
    """Configuration for regional and global visualization."""

    output_dir: Path = Path("outputs/plots")
    dpi: int = 200
    export_video: bool = True
    fps: int = 2
    video_path: Path = Path("outputs/regpgw_forecast.mp4")
    plot_channels: Sequence[int] = field(default_factory=lambda: [18, 31, 47])


@dataclass(frozen=True)
class AppConfig:
    """Root configuration aggregating all sub-configurations."""

    data: RegPGWDataConfig = field(default_factory=RegPGWDataConfig)
    model: RegPGWModelConfig = field(default_factory=RegPGWModelConfig)
    train: RegPGWTrainConfig = field(default_factory=RegPGWTrainConfig)
    global_fcn: GlobalFCNInferenceConfig = field(
        default_factory=GlobalFCNInferenceConfig
    )
    inference: RegPGWInferenceConfig = field(
        default_factory=RegPGWInferenceConfig
    )
    plot: PlotConfig = field(default_factory=PlotConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Build AppConfig with overrides from environment variables.

        Returns:
            AppConfig: Configured application instance.
        """
        data_dir_env = os.environ.get("FCN_DATA_DIR")
        data_dir = Path(data_dir_env) if data_dir_env else Path("data")

        device_env = os.environ.get("FCN_DEVICE", "cuda")
        global_model_env = os.environ.get(
            "FCN_GLOBAL_MODEL", "weight/fcnv2_sm.onnx"
        )
        regpgw_model_env = os.environ.get(
            "REGPGW_MODEL", "weight/RegPGW+LS+Res.onnx"
        )

        return cls(
            data=RegPGWDataConfig(data_dir=data_dir),
            model=RegPGWModelConfig(),
            train=RegPGWTrainConfig(),
            global_fcn=GlobalFCNInferenceConfig(
                model_path=Path(global_model_env),
                device=device_env,
            ),
            inference=RegPGWInferenceConfig(
                model_path=Path(regpgw_model_env),
                device=device_env,
            ),
            plot=PlotConfig(),
        )
