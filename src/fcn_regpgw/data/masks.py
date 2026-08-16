"""Static geographical masks and orography processors for FCN-RegPGW.

Handles loading, generation, and standardization of Land-Sea Masks (LSM)
and topography/orography features.
"""

from pathlib import Path

import numpy as np
import xarray as xr

from fcn_regpgw.const import (
    DEFAULT_LAT_SIZE,
    DEFAULT_LON_SIZE,
)
from fcn_regpgw.data.transforms import generate_sincos_grid
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class StaticMaskProcessor:
    """Processor for static surface features: LSM, Orography, and Sin/Cos coordinates."""

    def __init__(
        self,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
        lsm_path: str | Path | None = None,
        orography_path: str | Path | None = None,
    ) -> None:
        """Initialize StaticMaskProcessor.

        Args:
            lat_size (int): Latitude grid points.
            lon_size (int): Longitude grid points.
            lsm_path (Optional[Union[str, Path]]): Path to NetCDF LSM dataset.
            orography_path (Optional[Union[str, Path]]): Path to NetCDF
                Orography dataset.
        """
        self.lat_size = lat_size
        self.lon_size = lon_size
        self.lsm_path = Path(lsm_path) if lsm_path else None
        self.orography_path = Path(orography_path) if orography_path else None

    def load_land_sea_mask(self) -> np.ndarray:
        """Load land-sea mask array of shape (1, lat_size, lon_size).

        If file does not exist, generates a synthetic mask as fallback.

        Returns:
            np.ndarray: LSM array with values in [0, 1].
        """
        if self.lsm_path and self.lsm_path.is_file():
            logger.info("Loading Land-Sea Mask from %s", self.lsm_path)
            ds = xr.open_dataset(self.lsm_path)
            # Standard key lookup (LSM or lsm)
            var_name = "LSM" if "LSM" in ds else "lsm"
            mask = ds[var_name].values.astype(np.float32)
            if mask.ndim == 2:
                mask = mask[np.newaxis, ...]
            # Handle potential 1441 vs 1440 periodic boundary
            if mask.shape[-1] > self.lon_size:
                mask = mask[:, :, : self.lon_size]
            return mask[:, : self.lat_size, : self.lon_size]

        logger.warning(
            "LSM file not specified or missing. Using synthetic land-sea mask."
        )
        # Synthetic mask (zeros for ocean, ones for central landmass)
        synthetic = np.zeros(
            (1, self.lat_size, self.lon_size), dtype=np.float32
        )
        synthetic[:, 200:500, 400:1000] = 1.0
        return synthetic

    def load_orography(self) -> np.ndarray:
        """Load orography (topography) array of shape (1, lat_size, lon_size).

        Standardizes the orography feature by subtracting mean and dividing by
        standard deviation. If file does not exist, generates synthetic orography.

        Returns:
            np.ndarray: Standardized orography array.
        """
        if self.orography_path and self.orography_path.is_file():
            logger.info("Loading Orography from %s", self.orography_path)
            ds = xr.open_dataset(self.orography_path)
            var_name = (
                "Z"
                if "Z" in ds
                else "z"
                if "z" in ds
                else next(iter(ds.data_vars.keys()))
            )
            oro = ds[var_name].values.astype(np.float32)
            if oro.ndim == 2:
                oro = oro[np.newaxis, ...]
            if oro.shape[-1] > self.lon_size:
                oro = oro[:, :, : self.lon_size]
            oro = oro[:, : self.lat_size, : self.lon_size]
            std_val = float(oro.std())
            if std_val > 1e-6:
                oro = (oro - float(oro.mean())) / std_val
            return oro

        logger.warning(
            "Orography file not specified or missing. Using synthetic orography."
        )
        synthetic = np.zeros(
            (1, self.lat_size, self.lon_size), dtype=np.float32
        )
        return synthetic

    def build_static_features(self) -> np.ndarray:
        """Build full 6-channel static tensor [sin_lat, cos_lat, sin_lon, cos_lon, oro, lsm].

        Returns:
            np.ndarray: Static feature tensor of shape (6, lat_size, lon_size).
        """
        sincos = generate_sincos_grid(self.lat_size, self.lon_size)
        oro = self.load_orography()
        lsm = self.load_land_sea_mask()
        static_data = np.concatenate([sincos, oro, lsm], axis=0).astype(
            np.float32
        )
        return static_data
