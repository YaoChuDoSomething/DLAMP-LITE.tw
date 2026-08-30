"""Meteorological field plotting and visualization utilities for FCN-RegPGW.

Provides high-resolution contour plotting for 850 hPa wind speed,
geopotential height, temperature, and precipitation fields with coastline overlays.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fcn_regpgw.const import (
    DEFAULT_LAT_SIZE,
    DEFAULT_LON_SIZE,
    INDEX_U850,
    INDEX_V850,
    WIND_SPEED_COLORS,
    WIND_SPEED_LEVELS,
)
from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger
from fcn_regpgw.visual.coastlines import CoastlineProvider

logger = get_logger(__name__)


class WeatherPlotter:
    """Unified meteorological contour plotter with geographical context."""

    def __init__(
        self,
        coastline_provider: CoastlineProvider | None = None,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
    ) -> None:
        """Initialize WeatherPlotter.

        Args:
            coastline_provider (Optional[CoastlineProvider]): Coastline coordinate provider.
            lat_size (int): Latitude grid points.
            lon_size (int): Longitude grid points.
        """
        self.coast_provider = coastline_provider or CoastlineProvider()
        self.lat_size = lat_size
        self.lon_size = lon_size

        self.lons = np.linspace(0.0, 359.75, lon_size, dtype=np.float32)
        self.lats = np.linspace(-90.0, 90.0, lat_size, dtype=np.float32)
        self.grid_x, self.grid_y = np.meshgrid(
            self.lons, self.lats, indexing="xy"
        )

    def plot_wind_speed_850(
        self,
        weather_data: np.ndarray,
        lead_hour: int,
        output_file: str | Path,
        title: str | None = None,
    ) -> Path:
        """Plot 850 hPa wind speed magnitude with standard meteorological color levels.

        Args:
            weather_data (np.ndarray): Full atmospheric state array (73, H, W).
            lead_hour (int): Lead forecast hour.
            output_file (Union[str, Path]): Target output PNG image path.
            title (Optional[str]): Custom plot title string.

        Returns:
            Path: Path to saved figure image.
        """
        out_path = Path(output_file)
        ensure_dir(out_path.parent)

        u = weather_data[INDEX_U850, : self.lat_size, : self.lon_size]
        v = weather_data[INDEX_V850, : self.lat_size, : self.lon_size]
        wsp = np.sqrt(u**2 + v**2)

        fig, ax = plt.subplots(figsize=(12, 6.5), dpi=150)

        # Plot coastline background
        coast_lon, coast_lat = self.coast_provider.get_coordinates()
        ax.plot(coast_lon, coast_lat, color="gray", linewidth=0.8, zorder=2)

        # Plot wind speed filled contour
        cf = ax.contourf(
            self.grid_x,
            self.grid_y,
            wsp,
            levels=list(WIND_SPEED_LEVELS),
            colors=list(WIND_SPEED_COLORS),
            extend="max",
            zorder=1,
        )

        cbar = fig.colorbar(cf, ax=ax, orientation="vertical", pad=0.02, shrink=0.85)
        cbar.set_label("850 hPa Wind Speed [m/s]", fontsize=10)

        plot_title = (
            title
            if title
            else f"850 hPa Wind Speed Forecast — Lead Time +{lead_hour:03d}h"
        )
        ax.set_title(plot_title, fontsize=12, pad=10)
        ax.set_xlabel("Longitude [°E]", fontsize=10)
        ax.set_ylabel("Latitude [°N]", fontsize=10)
        ax.set_xlim(0, 360)
        ax.set_ylim(-90, 90)

        fig.tight_layout()
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)

        logger.info("Saved 850 hPa wind speed plot to %s", out_path)
        return out_path

    def plot_precipitation(
        self,
        precip_data: np.ndarray,
        lead_hour: int,
        output_file: str | Path,
        title: str | None = None,
    ) -> Path:
        """Plot surface total precipitation accumulation field.

        Args:
            precip_data (np.ndarray): Precipitation field array (1, H, W) or (H, W).
            lead_hour (int): Lead forecast hour.
            output_file (Union[str, Path]): Target output PNG image path.
            title (Optional[str]): Custom plot title string.

        Returns:
            Path: Path to saved figure image.
        """
        out_path = Path(output_file)
        ensure_dir(out_path.parent)

        p_field = (
            precip_data[0] if precip_data.ndim == 3 else precip_data
        )
        p_field = p_field[: self.lat_size, : self.lon_size]

        fig, ax = plt.subplots(figsize=(12, 6.5), dpi=150)

        coast_lon, coast_lat = self.coast_provider.get_coordinates()
        ax.plot(coast_lon, coast_lat, color="gray", linewidth=0.8, zorder=2)

        levels = [0.1, 1.0, 2.5, 5.0, 10.0, 20.0, 35.0, 50.0, 75.0, 100.0]
        cf = ax.contourf(
            self.grid_x,
            self.grid_y,
            p_field,
            levels=levels,
            cmap="Blues",
            extend="max",
            zorder=1,
        )

        cbar = fig.colorbar(cf, ax=ax, orientation="vertical", pad=0.02, shrink=0.85)
        cbar.set_label("Precipitation [mm]", fontsize=10)

        plot_title = (
            title
            if title
            else f"Precipitation Forecast — Lead Time +{lead_hour:03d}h"
        )
        ax.set_title(plot_title, fontsize=12, pad=10)
        ax.set_xlabel("Longitude [°E]", fontsize=10)
        ax.set_ylabel("Latitude [°N]", fontsize=10)
        ax.set_xlim(0, 360)
        ax.set_ylim(-90, 90)

        fig.tight_layout()
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)

        logger.info("Saved precipitation plot to %s", out_path)
        return out_path
