"""Regional PGW one-way downscaling and two-way boundary coupling predictors.

Implements one-way regional atmospheric downscaling and two-way coupled domain
feedback mechanisms between global FCNv2 and regional RegPGW models.
"""

from pathlib import Path

import numpy as np

from fcn_regpgw.data.standardizer import GlobalStandardizer
from fcn_regpgw.inference.engine import BaseInferenceEngine
from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class PGWOneWayPredictor:
    """One-way regional downscaling predictor driven by global FCNv2 outputs."""

    def __init__(
        self,
        pgw_engine: BaseInferenceEngine,
        standardizer: GlobalStandardizer | None = None,
    ) -> None:
        """Initialize PGWOneWayPredictor.

        Args:
            pgw_engine (BaseInferenceEngine): Engine for RegPGW model.
            standardizer (Optional[GlobalStandardizer]): Normalization
                standardizer.
        """
        self.pgw_engine = pgw_engine
        self.standardizer = standardizer

    def run_downscaling(
        self,
        fcnv2_output_dir: str | Path,
        output_dir: str | Path,
        forecast_hours: int = 480,
        step_hours: int = 6,
    ) -> list[Path]:
        """Execute one-way regional downscaling for all forecast steps.

        Args:
            fcnv2_output_dir (Union[str, Path]): Directory with global FCNv2
                NPY files.
            output_dir (Union[str, Path]): Directory to save PGW regional
                forecasts.
            forecast_hours (int): Total forecast hours.
            step_hours (int): Step delta in hours.

        Returns:
            List[Path]: Paths to generated regional forecast files.
        """
        in_dir = Path(fcnv2_output_dir)
        out_dir = ensure_dir(output_dir)
        saved_files: list[Path] = []

        num_steps = forecast_hours // step_hours
        logger.info(
            "Starting RegPGW one-way downscaling: %d steps (%d hours)",
            num_steps,
            forecast_hours,
        )

        for step in range(num_steps + 1):
            lead_time = step * step_hours
            src_file = in_dir / f"output_weather_{lead_time:03d}h.npy"
            if not src_file.is_file():
                logger.warning("Driving file not found: %s. Skipping.", src_file)
                continue

            global_data = np.load(src_file)
            if self.standardizer:
                in_data = self.standardizer.transform(global_data)
            else:
                in_data = global_data

            pgw_pred = self.pgw_engine.predict(in_data)
            if pgw_pred.ndim == 4 and pgw_pred.shape[0] == 1:
                pgw_pred = pgw_pred[0]

            if self.standardizer:
                out_state = self.standardizer.inverse_transform(pgw_pred)
            else:
                out_state = pgw_pred

            dest_file = out_dir / f"output_weather_{lead_time:03d}h.npy"
            save_numpy_atomic(dest_file, out_state)
            saved_files.append(dest_file)
            logger.info("Saved PGW forecast step %03dh to %s", lead_time, dest_file)

        return saved_files


class PGWTwoWayPredictor:
    """Two-way coupled predictor with regional feedback re-injection into global model."""

    def __init__(
        self,
        fcnv2_engine: BaseInferenceEngine,
        pgw_engine: BaseInferenceEngine,
        standardizer: GlobalStandardizer | None = None,
        domain_bounds: tuple[int, int, int, int] = (200, 500, 400, 800),
    ) -> None:
        """Initialize PGWTwoWayPredictor.

        Args:
            fcnv2_engine (BaseInferenceEngine): Global model engine.
            pgw_engine (BaseInferenceEngine): Regional PGW model engine.
            standardizer (Optional[GlobalStandardizer]): Normalization standardizer.
            domain_bounds (Tuple[int, int, int, int]): Regional bounding box
                slice indices (lat_min, lat_max, lon_min, lon_max).
        """
        self.fcnv2_engine = fcnv2_engine
        self.pgw_engine = pgw_engine
        self.standardizer = standardizer
        self.lat_min, self.lat_max, self.lon_min, self.lon_max = domain_bounds

    def run_coupled_forecast(
        self,
        initial_condition: np.ndarray,
        forecast_hours: int = 240,
        step_hours: int = 6,
        output_dir: str | Path = "outputs/two_way",
    ) -> tuple[list[Path], list[Path]]:
        """Run step-by-step two-way coupled forecast with domain re-injection.

        Args:
            initial_condition (np.ndarray): Initial state array (73, H, W).
            forecast_hours (int): Total forecast lead time in hours.
            step_hours (int): Forecast step duration in hours.
            output_dir (Union[str, Path]): Base output directory.

        Returns:
            Tuple[List[Path], List[Path]]: (global_saved_files, regional_saved_files).
        """
        base_dir = ensure_dir(output_dir)
        global_dir = ensure_dir(base_dir / "FCNV2_forecast")
        pgw_dir = ensure_dir(base_dir / "PGW_forecast")

        global_files: list[Path] = []
        pgw_files: list[Path] = []

        current_global = initial_condition.copy()

        # Save initial condition
        p_g0 = global_dir / "output_weather_000h.npy"
        save_numpy_atomic(p_g0, current_global)
        global_files.append(p_g0)

        num_steps = forecast_hours // step_hours
        logger.info(
            "Starting FCNv2-RegPGW two-way coupled forecast: %d steps (%d hours)",
            num_steps,
            forecast_hours,
        )

        for step in range(1, num_steps + 1):
            lead_time = step * step_hours

            # Step 1: Global FCNv2 prediction
            in_g = (
                self.standardizer.transform(current_global)
                if self.standardizer
                else current_global
            )
            pred_g = self.fcnv2_engine.predict(in_g)
            if pred_g.ndim == 4 and pred_g.shape[0] == 1:
                pred_g = pred_g[0]
            state_g = (
                self.standardizer.inverse_transform(pred_g)
                if self.standardizer
                else pred_g
            )

            # Step 2: Regional PGW prediction driven by current step
            in_p = (
                self.standardizer.transform(state_g)
                if self.standardizer
                else state_g
            )
            pred_p = self.pgw_engine.predict(in_p)
            if pred_p.ndim == 4 and pred_p.shape[0] == 1:
                pred_p = pred_p[0]
            state_p = (
                self.standardizer.inverse_transform(pred_p)
                if self.standardizer
                else pred_p
            )

            # Step 3: Re-inject regional high-resolution domain into global state
            # If state_p is regional size, paste it; if global, blend the bounding domain
            if (
                state_p.shape[-2] == (self.lat_max - self.lat_min)
                and state_p.shape[-1] == (self.lon_max - self.lon_min)
            ):
                state_g[
                    :,
                    self.lat_min : self.lat_max,
                    self.lon_min : self.lon_max,
                ] = state_p
            else:
                # Same resolution: blend inner domain
                state_g[
                    :,
                    self.lat_min : self.lat_max,
                    self.lon_min : self.lon_max,
                ] = state_p[
                    :,
                    self.lat_min : self.lat_max,
                    self.lon_min : self.lon_max,
                ]

            # Save global & regional forecasts
            f_g = global_dir / f"output_weather_{lead_time:03d}h.npy"
            f_p = pgw_dir / f"output_weather_{lead_time:03d}h.npy"

            save_numpy_atomic(f_g, state_g)
            save_numpy_atomic(f_p, state_p)

            global_files.append(f_g)
            pgw_files.append(f_p)

            logger.info(
                "Saved coupled step %03dh (global: %s, pgw: %s)",
                lead_time,
                f_g,
                f_p,
            )
            current_global = state_g

        return global_files, pgw_files
