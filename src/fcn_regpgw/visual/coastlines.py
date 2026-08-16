"""Coastline data loader and geographic boundary normalization for FCN-RegPGW.

Provides robust coastline coordinate transformation for [0, 360] longitude
atmospheric plotting grids.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class CoastlineProvider:
    """Provider for transformed global and regional coastline coordinates."""

    def __init__(self, csv_path: str | Path | None = None) -> None:
        """Initialize CoastlineProvider.

        Args:
            csv_path (Optional[Union[str, Path]]): Path to coastline CSV file.
        """
        self.csv_path = Path(csv_path) if csv_path else None
        self._lon: np.ndarray | None = None
        self._lat: np.ndarray | None = None

    def get_coordinates(self) -> tuple[np.ndarray, np.ndarray]:
        """Load and return normalized coastline lon/lat coordinate arrays.

        Normalizes negative longitudes into the [0, 360] domain and inserts NaNs
        to prevent artificial connecting lines across map boundaries.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (lon_coords, lat_coords).
        """
        if self._lon is not None and self._lat is not None:
            return self._lon, self._lat

        if self.csv_path and self.csv_path.is_file():
            logger.info("Loading coastline coordinates from %s", self.csv_path)
            try:
                df = pd.read_csv(self.csv_path)
                lon_col = (
                    "lon_map"
                    if "lon_map" in df.columns
                    else "lon"
                    if "lon" in df.columns
                    else df.columns[0]
                )
                lat_col = (
                    "lat_map"
                    if "lat_map" in df.columns
                    else "lat"
                    if "lat" in df.columns
                    else df.columns[1]
                )

                lon = df[lon_col].to_numpy().copy()
                lat = df[lat_col].to_numpy().copy()

                # Adjust negative longitudes to 0-360 range
                lon[lon < 0] = lon[lon < 0] + 360.0
                # Insert NaN breaks near prime meridian to prevent horizontal wrapping
                lon[(df[lon_col] < 0) & (df[lon_col] >= -10)] = np.nan

                self._lon = lon
                self._lat = lat
                return lon, lat
            except (ValueError, KeyError, OSError) as exc:
                logger.warning(
                    "Failed to parse coastline CSV (%s). Using fallback.", exc
                )

        # Fallback synthetic outline
        logger.info("Using default fallback coastline coordinates.")
        t = np.linspace(0, 2 * np.pi, 200)
        self._lon = (180.0 + 100.0 * np.cos(t)).astype(np.float32)
        self._lat = (30.0 * np.sin(t)).astype(np.float32)
        return self._lon, self._lat
