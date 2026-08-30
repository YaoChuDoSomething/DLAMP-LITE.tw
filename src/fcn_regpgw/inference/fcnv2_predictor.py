"""Autoregressive global forecast predictor using FCNv2 models.

Executes sequential multi-step forecast rollouts with coordinate alignment
and persistent step serialization.
"""

from pathlib import Path

import numpy as np

from fcn_regpgw.data.standardizer import GlobalStandardizer
from fcn_regpgw.data.transforms import flip_latitude
from fcn_regpgw.inference.engine import BaseInferenceEngine
from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class FCNv2Predictor:
    """Autoregressive multi-step global atmospheric predictor."""

    def __init__(
        self,
        engine: BaseInferenceEngine,
        standardizer: GlobalStandardizer | None = None,
        apply_lat_flip: bool = True,
    ) -> None:
        """Initialize FCNv2Predictor.

        Args:
            engine (BaseInferenceEngine): Configured inference engine.
            standardizer (Optional[GlobalStandardizer]): Standardizer for
                normalization.
            apply_lat_flip (bool): Whether to flip latitude for model
                orientation.
        """
        self.engine = engine
        self.standardizer = standardizer
        self.apply_lat_flip = apply_lat_flip

    def run_forecast(
        self,
        initial_condition: np.ndarray,
        forecast_hours: int = 240,
        step_hours: int = 6,
        output_dir: str | Path | None = None,
    ) -> list[Path]:
        """Execute autoregressive rollout forecasting up to target lead time.

        Args:
            initial_condition (np.ndarray): Initial state array (73, H, W).
            forecast_hours (int): Total forecast lead time in hours.
            step_hours (int): Forecast step duration in hours (default 6).
            output_dir (Optional[Union[str, Path]]): Destination directory to
                save step arrays.

        Returns:
            List[Path]: List of saved file paths for each forecast step.
        """
        save_dir = ensure_dir(output_dir) if output_dir else None
        saved_files: list[Path] = []

        current_state = initial_condition.copy()
        if self.apply_lat_flip:
            current_state = flip_latitude(current_state, lat_axis=-2)

        # Save initial condition (000h)
        if save_dir:
            out_0h = (
                flip_latitude(current_state, lat_axis=-2)
                if self.apply_lat_flip
                else current_state
            )
            p_0 = save_dir / "output_weather_000h.npy"
            save_numpy_atomic(p_0, out_0h)
            saved_files.append(p_0)

        num_steps = forecast_hours // step_hours
        logger.info(
            "Starting FCNv2 autoregressive forecast: %d steps (%d hours)",
            num_steps,
            forecast_hours,
        )

        for step in range(1, num_steps + 1):
            lead_time = step * step_hours

            # Normalize if standardizer provided
            if self.standardizer:
                in_data = self.standardizer.transform(current_state)
            else:
                in_data = current_state

            # Forward pass
            out_pred = self.engine.predict(in_data)
            if out_pred.ndim == 4 and out_pred.shape[0] == 1:
                out_pred = out_pred[0]

            # Denormalize
            if self.standardizer:
                out_state = self.standardizer.inverse_transform(out_pred)
            else:
                out_state = out_pred

            # Save state
            if save_dir:
                to_save = (
                    flip_latitude(out_state, lat_axis=-2)
                    if self.apply_lat_flip
                    else out_state
                )
                file_path = save_dir / f"output_weather_{lead_time:03d}h.npy"
                save_numpy_atomic(file_path, to_save)
                saved_files.append(file_path)
                logger.info("Saved forecast step %03dh to %s", lead_time, file_path)

            current_state = out_state

        return saved_files
