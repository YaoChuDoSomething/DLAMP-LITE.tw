"""Precipitation diagnostic inference predictor.

Maps sequential multi-step atmospheric forecasts to surface precipitation
rate fields using diagnostic neural backbones.
"""

from pathlib import Path

import numpy as np

from fcn_regpgw.data.standardizer import GlobalStandardizer
from fcn_regpgw.inference.engine import BaseInferenceEngine
from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class PrecipPredictor:
    """Diagnostic precipitation predictor for atmospheric forecast sequences."""

    def __init__(
        self,
        engine: BaseInferenceEngine,
        standardizer: GlobalStandardizer | None = None,
    ) -> None:
        """Initialize PrecipPredictor.

        Args:
            engine (BaseInferenceEngine): Precip model engine.
            standardizer (Optional[GlobalStandardizer]): Atmospheric variable
                standardizer.
        """
        self.engine = engine
        self.standardizer = standardizer

    def run_prediction(
        self,
        weather_data_dir: str | Path,
        output_dir: str | Path,
        forecast_hours: int = 240,
        step_hours: int = 6,
    ) -> list[Path]:
        """Execute precipitation inference on sequence of weather states.

        Args:
            weather_data_dir (Union[str, Path]): Folder with output_weather_*.npy.
            output_dir (Union[str, Path]): Destination directory for precipitation.
            forecast_hours (int): Total forecast hours.
            step_hours (int): Step delta in hours.

        Returns:
            List[Path]: Paths to saved precipitation files.
        """
        in_dir = Path(weather_data_dir)
        out_dir = ensure_dir(output_dir)
        saved_files: list[Path] = []

        num_steps = forecast_hours // step_hours
        logger.info(
            "Starting precipitation diagnostic inference for %d steps",
            num_steps,
        )

        for step in range(num_steps + 1):
            lead_time = step * step_hours
            src_file = in_dir / f"output_weather_{lead_time:03d}h.npy"
            if not src_file.is_file():
                logger.warning(
                    "Weather state %s not found. Skipping precip step.",
                    src_file,
                )
                continue

            state = np.load(src_file)
            if self.standardizer:
                in_data = self.standardizer.transform(state)
            else:
                in_data = state

            pred = self.engine.predict(in_data)
            if pred.ndim == 4 and pred.shape[0] == 1:
                pred = pred[0]

            out_file = out_dir / f"output_precip_{lead_time:03d}h.npy"
            save_numpy_atomic(out_file, pred)
            saved_files.append(out_file)
            logger.info(
                "Saved precipitation step %03dh to %s", lead_time, out_file
            )

        return saved_files
