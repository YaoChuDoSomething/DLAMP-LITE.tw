"""Data preparation workflow runner for FCN-RegPGW static features and masks.

Generates and serializes static land-sea masks, standardized orography fields,
and degree-to-radian trigonometric coordinate grids.
"""

from pathlib import Path

from fcn_regpgw.config import DataConfig
from fcn_regpgw.data.masks import StaticMaskProcessor
from fcn_regpgw.utils.file_util import ensure_dir, save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class DataPrepRunner:
    """Workflow runner for atmospheric static feature preparation."""

    def __init__(self, config: DataConfig | None = None) -> None:
        """Initialize DataPrepRunner.

        Args:
            config (Optional[DataConfig]): Data configuration settings.
        """
        self.config = config or DataConfig()
        self.processor = StaticMaskProcessor(
            lat_size=self.config.lat_size,
            lon_size=self.config.lon_size,
            lsm_path=self.config.land_sea_mask_path,
            orography_path=self.config.orography_path,
        )

    def run(self, output_path: str | Path | None = None) -> Path:
        """Execute data preparation workflow and save static feature array.

        Args:
            output_path (Optional[Union[str, Path]]): Destination path for
                saved 6-channel static features array.

        Returns:
            Path: Path to saved static features file.
        """
        logger.info("Executing DataPrepRunner static features generation...")
        static_data = self.processor.build_static_features()

        dest_file = (
            Path(output_path)
            if output_path
            else self.config.data_dir / "static_features.npy"
        )
        ensure_dir(dest_file.parent)
        save_numpy_atomic(dest_file, static_data)
        logger.info(
            "Static features array of shape %s saved to %s",
            static_data.shape,
            dest_file,
        )
        return dest_file
