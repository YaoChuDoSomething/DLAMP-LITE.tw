"""Regional domain meteorological visualization for RegPGW.

Generates high-resolution regional plots for 850 hPa wind speed, geopotential
height contours, temperature, and comparison figures between Global FCN and
Regional RegPGW predictions.
"""

from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

from fcn_regpgw.const import (
    INDEX_U850,
    INDEX_V850,
    WIND_SPEED_COLORS,
    WIND_SPEED_LEVELS,
)
from fcn_regpgw.visual.coastlines import CoastlineProvider


class RegionalWeatherPlotter:
    """Plots regional domain meteorological forecasts.

    Attributes:
        output_dir (Path): Output directory for generated figures.
        dpi (int): Image resolution DPI.
        coastline_provider (CoastlineProvider): Coastline geometry provider.
    """

    def __init__(
        self,
        output_dir: Path = Path("outputs/regional_plots"),
        dpi: int = 200,
        coastline_provider: CoastlineProvider | None = None,
    ) -> None:
        """Initialize RegionalWeatherPlotter.

        Args:
            output_dir (Path): Output directory.
            dpi (int): Figure DPI resolution.
            coastline_provider (Optional[CoastlineProvider]): Coastline loader.
        """
        self.output_dir = output_dir
        self.dpi = dpi
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.coastline_provider = coastline_provider or CoastlineProvider()

        # Build wind colormap
        self.wind_cmap = mcolors.ListedColormap(WIND_SPEED_COLORS)
        self.wind_norm = mcolors.BoundaryNorm(
            WIND_SPEED_LEVELS, len(WIND_SPEED_COLORS)
        )

    def plot_850hpa_wind_speed(
        self,
        regional_state: np.ndarray,
        lead_hour: int = 0,
        filename: str | None = None,
        title_suffix: str = "RegPGW Regional Forecast",
    ) -> Path:
        """Plot regional 850 hPa wind speed map.

        Args:
            regional_state (np.ndarray): Array of shape (73, H, W).
            lead_hour (int): Forecast lead time in hours.
            filename (Optional[str]): Target image filename.
            title_suffix (str): Title description.

        Returns:
            Path: Path to saved PNG file.
        """
        u850 = regional_state[INDEX_U850]
        v850 = regional_state[INDEX_V850]
        wind_speed = np.sqrt(u850**2 + v850**2)

        fig, ax = plt.subplots(figsize=(8, 8), dpi=self.dpi)
        im = ax.imshow(
            wind_speed,
            cmap=self.wind_cmap,
            norm=self.wind_norm,
            origin="upper",
            aspect="auto",
        )
        cbar = fig.colorbar(im, ax=ax, orientation="vertical", shrink=0.75, pad=0.03)
        cbar.set_label("850 hPa Wind Speed (m/s)")

        ax.set_title(f"{title_suffix} - Lead +{lead_hour:03d}h")
        ax.set_xlabel("Regional X (Grid Cells)")
        ax.set_ylabel("Regional Y (Grid Cells)")

        out_name = filename or f"regpgw_wind850_{lead_hour:03d}h.png"
        out_path = self.output_dir / out_name
        plt.tight_layout()
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path

    def plot_comparison(
        self,
        global_subgrid: np.ndarray,
        regpgw_grid: np.ndarray,
        lead_hour: int = 0,
        filename: str | None = None,
    ) -> Path:
        """Plot 3-panel comparison: Global FCN vs Regional RegPGW vs Difference.

        Args:
            global_subgrid (np.ndarray): Driving global slice (73, H, W).
            regpgw_grid (np.ndarray): RegPGW regional forecast (73, H, W).
            lead_hour (int): Lead time.
            filename (Optional[str]): Output filename.

        Returns:
            Path: Saved comparison figure path.
        """
        w_global = np.sqrt(
            global_subgrid[INDEX_U850] ** 2 + global_subgrid[INDEX_V850] ** 2
        )
        w_reg = np.sqrt(
            regpgw_grid[INDEX_U850] ** 2 + regpgw_grid[INDEX_V850] ** 2
        )
        diff = w_reg - w_global

        fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=self.dpi)

        # Panel 1: Global FCN
        axes[0].imshow(
            w_global,
            cmap=self.wind_cmap,
            norm=self.wind_norm,
            origin="upper",
            aspect="auto",
        )
        axes[0].set_title(f"Global FCNv2 Driving (Lead +{lead_hour:03d}h)")

        # Panel 2: RegPGW
        im2 = axes[1].imshow(
            w_reg,
            cmap=self.wind_cmap,
            norm=self.wind_norm,
            origin="upper",
            aspect="auto",
        )
        axes[1].set_title(f"RegPGW Regional Forecast (Lead +{lead_hour:03d}h)")
        fig.colorbar(im2, ax=axes[1], shrink=0.75, pad=0.03, label="Wind Speed (m/s)")

        # Panel 3: Difference (RegPGW - FCN)
        im3 = axes[2].imshow(
            diff,
            cmap="bwr",
            vmin=-10,
            vmax=10,
            origin="upper",
            aspect="auto",
        )
        axes[2].set_title("Difference: RegPGW - Global FCN (m/s)")
        fig.colorbar(im3, ax=axes[2], shrink=0.75, pad=0.03, label="Delta (m/s)")

        out_name = filename or f"comparison_wind850_{lead_hour:03d}h.png"
        out_path = self.output_dir / out_name
        plt.tight_layout()
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path
