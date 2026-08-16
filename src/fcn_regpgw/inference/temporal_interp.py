"""ModAFNO temporal interpolation predictor (fcinterp).

Interpolates coarse 6-hourly atmospheric forecast pairs to high-resolution
hourly trajectories with solar zenith modulation and static feature fusion.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

from fcn_regpgw.const import (
    DEFAULT_LAT_SIZE,
    DEFAULT_LON_SIZE,
    PRESSURE_LEVELS,
    SLICE_Q,
    SLICE_R,
    SLICE_T,
)
from fcn_regpgw.data.masks import StaticMaskProcessor
from fcn_regpgw.data.standardizer import GlobalStandardizer
from fcn_regpgw.data.transforms import (
    calculate_cos_zenith_series,
    q_to_rh,
    rh_to_q,
)
from fcn_regpgw.inference.engine import BaseInferenceEngine
from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class ModAFNOInterpolator:
    """Continuous temporal interpolation predictor using ModAFNO neural backbone."""

    def __init__(
        self,
        engine: BaseInferenceEngine,
        standardizer: GlobalStandardizer | None = None,
        static_mask_processor: StaticMaskProcessor | None = None,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
    ) -> None:
        """Initialize ModAFNOInterpolator.

        Args:
            engine (BaseInferenceEngine): ModAFNO inference engine.
            standardizer (Optional[GlobalStandardizer]): Normalization standardizer.
            static_mask_processor (Optional[StaticMaskProcessor]): Static mask builder.
            lat_size (int): Latitude grid size.
            lon_size (int): Longitude grid size.
        """
        self.engine = engine
        self.standardizer = standardizer
        self.processor = static_mask_processor or StaticMaskProcessor(
            lat_size=lat_size, lon_size=lon_size
        )
        self.static_data = self.processor.build_static_features()
        self.lat_size = lat_size
        self.lon_size = lon_size

    def prepare_state(self, raw_data: np.ndarray) -> np.ndarray:
        """Prepare raw state: convert RH to q, trim boundary, and standardize.

        Args:
            raw_data (np.ndarray): Raw state array of shape (73, H, W).

        Returns:
            np.ndarray: Normalized state array with specific humidity.
        """
        x_data = raw_data.copy()
        if x_data.shape[1] > self.lat_size:
            x_data = x_data[:, : self.lat_size, :]
        if x_data.shape[2] > self.lon_size:
            x_data = x_data[:, :, : self.lon_size]

        # Convert RH -> q in channels 60:73
        rh = x_data[SLICE_R, :, :]
        t_k = x_data[SLICE_T, :, :]
        x_data[SLICE_Q, :, :] = rh_to_q(rh, t_k, pressure_levels=PRESSURE_LEVELS)

        # Apply z-score standardization
        if self.standardizer:
            x_data = self.standardizer.transform(x_data)

        return x_data

    def postprocess_state(self, pred_norm: np.ndarray) -> np.ndarray:
        """Postprocess prediction: inverse transform and convert q back to RH.

        Args:
            pred_norm (np.ndarray): Normalized prediction array of shape (73, H, W).

        Returns:
            np.ndarray: Physical scale state array with relative humidity.
        """
        out_state = pred_norm.copy()
        if self.standardizer:
            out_state = self.standardizer.inverse_transform(out_state)

        # Invert q -> RH in channels 60:73
        q = out_state[SLICE_Q, :, :]
        t_k = out_state[SLICE_T, :, :]
        out_state[SLICE_R, :, :] = q_to_rh(q, t_k, pressure_levels=PRESSURE_LEVELS)

        return out_state

    def run_interpolation(
        self,
        input_folder: str | Path,
        output_folder: str | Path,
        initial_time_str: str = "2025072400",
        num_6h_intervals: int = 10,
    ) -> list[Path]:
        """Interpolate coarse 6-hourly forecasts into hourly trajectory steps.

        Args:
            input_folder (Union[str, Path]): Directory containing 6h forecasts.
            output_folder (Union[str, Path]): Target output directory.
            initial_time_str (str): Initial condition timestamp string (YYYYMMDDHH).
            num_6h_intervals (int): Number of 6-hour interval pairs to process.

        Returns:
            List[Path]: List of generated hourly forecast file paths.

        Raises:
            FileNotFoundError: If required 6h boundary forecast files are missing.
        """
        in_dir = Path(input_folder)
        out_dir = ensure_dir(output_folder)
        saved_files: list[Path] = []

        base_dt = datetime.strptime(initial_time_str, "%Y%m%d%H").replace(
            tzinfo=UTC
        )

        logger.info(
            "Starting ModAFNO 6h->1h temporal interpolation for %d intervals",
            num_6h_intervals,
        )

        for i in range(num_6h_intervals):
            t0_hours = i * 6
            t1_hours = (i + 1) * 6

            file_0 = in_dir / f"output_weather_{t0_hours:03d}h.npy"
            file_1 = in_dir / f"output_weather_{t1_hours:03d}h.npy"

            # Fallback check for unpadded names if reading legacy files
            if not file_0.is_file():
                file_0 = in_dir / f"output_weather_{t0_hours}h.npy"
            if not file_1.is_file():
                file_1 = in_dir / f"output_weather_{t1_hours}h.npy"

            if not file_0.is_file() or not file_1.is_file():
                logger.warning(
                    "Interval boundary files missing (%s, %s). Skipping interval %d.",
                    file_0,
                    file_1,
                    i,
                )
                continue

            data1 = np.load(file_0)
            data2 = np.load(file_1)

            x1_norm = self.prepare_state(data1)
            x2_norm = self.prepare_state(data2)
            inter_data = np.concatenate([x1_norm, x2_norm], axis=0)  # 146 channels

            dt0 = base_dt + timedelta(hours=t0_hours)
            dt1 = base_dt + timedelta(hours=t1_hours)

            for intro_i in range(6):
                target_lead = t0_hours + intro_i
                dt_target = base_dt + timedelta(hours=target_lead)

                # Compute 3-channel solar zenith: [t0, t1, t_target]
                solar_data = calculate_cos_zenith_series(
                    [dt0, dt1, dt_target],
                    lat_size=self.lat_size,
                    lon_size=self.lon_size,
                )

                # Composite 155 channels: (146 + 3 + 6 = 155)
                composite_data = np.concatenate(
                    [inter_data, solar_data, self.static_data],
                    axis=0,
                ).astype(np.float32)

                t_norm = float(intro_i) / 6.0
                pred = self.engine.predict(composite_data, t=t_norm)
                if pred.ndim == 4 and pred.shape[0] == 1:
                    pred = pred[0]

                out_state = self.postprocess_state(pred)
                out_path = out_dir / f"output_weather_{target_lead:03d}h.npy"
                save_numpy_atomic(out_path, out_state)
                saved_files.append(out_path)
                logger.info(
                    "Saved interpolated hour %03dh to %s",
                    target_lead,
                    out_path,
                )

        return saved_files
