# analysis/plotter.py
"""Generates and saves detailed 12-panel weather analysis plots.

This module provides the WeatherPlotter for creating visualizations that
compare the model's forecast against ground truth data across multiple
variables and atmospheric levels in a single figure, using cartopy for
correct geospatial projection.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy.interpolate import griddata

from analysis.data_manager import AnalysisDataManager
from analysis.plot_meta import ANALYSIS_PLOT_CONFIGS  # <-- IMPORT NEW CONFIG
from src.utils import DataType, Level

logger = logging.getLogger(__name__)


class WeatherPlotter:
    """Creates and saves 12-panel forecast vs. ground truth plots.

    This class orchestrates the creation of a complex meteorological figure
    that visualizes multiple variables side-by-side for forecast and ground
    truth, aiding in qualitative model performance assessment.

    Attributes:
        manager (AnalysisDataManager): The data manager for data retrieval.
        output_dir (Path): Directory where plot images will be saved.
        map_projection: The cartopy projection used for all subplots.
    """

    def __init__(self, manager: AnalysisDataManager, output_dir: Path):
        """Initializes the WeatherPlotter.

        Args:
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): Target directory for saving plot images.
        """
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.map_projection = ccrs.PlateCarree()

        # A dispatch table mapping string keys from the config to actual
        # plotting methods. This is the core of the refactoring.
        self._plot_dispatch_table: Dict[str, Callable[..., Any]] = {
            "wind_speed": self._plot_wind_speed,
            "vorticity": self._plot_vorticity,
            "temperature": self._plot_temperature,
            "column_max_qw": self._plot_column_max_qw,
            "total_water_mixing_ratio": self._plot_mixing_ratio,
        }

    def create_analysis_figure(self, forecast_step: int) -> Path:
        """Creates and saves a single 12-panel analysis figure.

        Args:
            forecast_step (int): The 0-indexed forecast step to visualize.

        Returns:
            Path: The path to the saved PNG image file.
        """
        fig: Figure = plt.figure(figsize=(12, 5))
        gs = gridspec.GridSpec(2, 6, figure=fig, hspace=0.1, wspace=0.1)
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        start_time: str = self.manager.start_time.strftime('%Y-%m-%d_%H%M')
        valid_time: str = forecast_time.strftime('%Y-%m-%d_%H%M')

        step_str: str = (
            "F000H"
            if forecast_step == -1
            else f"F{forecast_step + 1:03d}H"
        )
        fig.suptitle(
            f"Initial: {start_time}Z {step_str} | Valid: {valid_time}Z",
            fontsize=12, y=0.95
        )

        # Iterate through the configuration from plot_meta.py
        for idx, config in enumerate(ANALYSIS_PLOT_CONFIGS):
            ax_fc: Axes = fig.add_subplot(gs[0, idx])
            ax_gt: Axes = fig.add_subplot(gs[1, idx])

            title: str = config["title"]
            level: Level = config["level"]
            unit: str = config["unit"]
            plot_func_key: str = config["plot_func_key"]

            try:
                # Look up the plotting method from the dispatch table
                plot_func: Callable[..., Any] = self._plot_dispatch_table[plot_func_key]
                # Call the dynamically selected method
                plot_func(ax_fc, ax_gt, forecast_step, config)
            except KeyError:
                logger.error(
                    "Plot function key '%s' not found in dispatch table.",
                    plot_func_key
                )
                continue  # Skip this panel if the key is invalid

        start_time_str: str = self.manager.start_time.strftime('%Y%m%d_%H%M')
        step_str_for_filename: str
        if forecast_step == -1:
            step_str_for_filename = "F000H"
        else:
            step_str_for_filename = f"F{forecast_step + 1:03d}H"

        filename: str = f"analysis_{start_time_str}_{step_str_for_filename}.png"
        output_path: Path = self.output_dir / filename
        #plt.show()
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved analysis plot to {output_path}")
        return output_path

    def _plot_wind_speed(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots wind speed as color mesh and geopotential height as contours."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]

        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)
        wspd_fc: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=False)
        u_fc: np.ndarray
        v_fc: np.ndarray
        u_fc, v_fc = self.manager._get_wind_components(step, level)

        time: datetime = self.manager.get_forecast_time(step)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)
        wspd_gt: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=True)
        u_gt: np.ndarray
        v_gt: np.ndarray
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)

        self._generic_grid_plot(
            ax_fc, f"FC: {title}", wspd_fc, z_fc, (u_fc, v_fc), "stream",
            cmap, vmin, vmax, unit
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", wspd_gt, z_gt, (u_gt, v_gt), "stream",
            cmap, vmin, vmax, unit
        )

    def _plot_vorticity(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots relative vorticity and geopotential height."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        clip_max: float = config["clip_max"]
        #fc_dx: float = self.manager.cfg.data.grid_spacing.forecast_m
        #gt_dx: float = self.manager.cfg.data.grid_spacing.ground_truth_m

        # The 1e6 is a scaling factor for meteorological convention.
        u_fc, v_fc = self.manager._get_wind_components(step, level)
        vort_fc: np.ndarray = self.manager.get_relative_vorticity(step, level, False) * 1e6
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)

        time: datetime = self.manager.get_forecast_time(step)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)
        vort_gt: np.ndarray = self.manager.get_relative_vorticity(step, level, True) * 1e6
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)

        self._generic_grid_plot(
            ax_fc, f"FC: {title}", np.clip(vort_fc, vmin, clip_max), z_fc, (u_fc, v_fc), "barbs", 
            cmap, vmin, vmax, unit
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", np.clip(vort_gt, vmin, clip_max), z_gt, (u_gt, v_gt), "barbs", 
            cmap, vmin, vmax, unit
        )

    def _plot_temperature(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots temperature and 10-meter wind."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]

        t_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.T, level)
        u10_fc: np.ndarray
        v10_fc: np.ndarray
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        t_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.T, level)
        u10_gt: np.ndarray
        v10_gt: np.ndarray
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc, f"FC: {title}", t_fc, None, (u10_fc, v10_fc), "stream",
            cmap, vmin, vmax, unit
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", t_gt, None, (u10_gt, v10_gt), "stream",
            cmap, vmin, vmax, unit
        )

    def _plot_mixing_ratio(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots 925hPa Qw and 10-meter wind."""
        title: str = config["title"]
        level: Optional[Level] = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]

        qw_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Qw, level) * 1000
        u10_fc: np.ndarray
        v10_fc: np.ndarray
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)
        
        time: datetime = self.manager.get_forecast_time(step)
        qw_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Qw, level) * 1000
        u10_gt: np.ndarray
        v10_gt: np.ndarray
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)
        
        self._generic_grid_plot(
            ax_fc, f"FC: {title}", qw_fc, None, (u10_fc, v10_fc), "barbs",
            cmap, vmin, vmax, unit
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", qw_gt, None, (u10_gt, v10_gt), "barbs",
            cmap, vmin, vmax, unit
        )

    def _plot_column_max_qw(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots column-maximum Qw and 10-meter wind."""
        title: str = config["title"]
        level: Optional[Level] = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]

        qw_fc: np.ndarray = self.manager.get_column_max_qw(step, False)
        u10_fc: np.ndarray
        v10_fc: np.ndarray
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        qw_gt: np.ndarray = self.manager.get_column_max_qw(step, True)
        u10_gt: np.ndarray
        v10_gt: np.ndarray
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc, f"FC: {title}", qw_fc, None, (u10_fc, v10_fc), "barbs",
            cmap, vmin, vmax, unit
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", qw_gt, None, (u10_gt, v10_gt), "barbs",
            cmap, vmin, vmax, unit
        )

    def _generic_grid_plot(
        self,
        ax: Axes,
        title: str,
        color_data: np.ndarray,
        contour_data: Optional[np.ndarray],
        wind_data: Optional[Tuple[np.ndarray, np.ndarray]],
        wind_type: str,
        cmap: str,
        vmin: float,
        vmax: float,
        unit: str,
    ):
        """Plots data on a model grid with transformed coastlines.

        This method operates in a non-geographic, rectilinear grid space
        defined by the model's output array indices. It transforms cartopy
        coastline coordinates from lon/lat into this grid space to provide
        a geographical reference.

        Args:
            ax (Axes): The matplotlib Axes object to plot on.
            title (str): The title for the subplot.
            color_data (np.ndarray): 2D data for the pcolormesh.
            contour_data (Optional[np.ndarray]): 2D data for contours.
            wind_data (Optional[Tuple[np.ndarray, np.ndarray]]): (u, v) winds.
            wind_type (str): 'stream' for streamplot or 'barbs' for barbs.
            cmap (str): The colormap for the color_data.
            vmin (float): The minimum value for the color scale.
            vmax (float): The maximum value for the color scale.
            unit (str): The unit label for the colorbar.
        """
        model_lon: np.ndarray = self.manager.results["lon"]
        model_lat: np.ndarray = self.manager.results["lat"]
        model_map: np.ndarray = self.manager.results["mask"]
        ny: int
        nx: int
        ny, nx = color_data.shape

        x_indices: np.ndarray = np.arange(nx)
        y_indices: np.ndarray = np.arange(ny)
        xgrid: np.ndarray
        ygrid: np.ndarray
        xgrid, ygrid = np.meshgrid(x_indices, y_indices)

        ax.set_title(title, fontsize=6)

        pcm = ax.pcolormesh(
            xgrid,
            ygrid,
            color_data,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            shading="auto",
        )
        cbar = plt.colorbar(
            pcm, ax=ax, orientation="horizontal", pad=0.06, shrink=0.95
        )
        #cbar.set_label(unit, size=4)
        
        cbar.ax.tick_params(labelsize=4, size=4, tickdir="in")

        if contour_data is not None:
            ax.contour(xgrid, ygrid, contour_data, colors="k", linewidths=0.4)

        if wind_data:
            u: np.ndarray
            v: np.ndarray
            u, v = wind_data
            skip: int = 15  # Plot a wind barb every 15 grid points
            if wind_type == "barbs":
                ax.barbs(
                    xgrid[::skip, ::skip],
                    ygrid[::skip, ::skip],
                    u[::skip, ::skip],
                    v[::skip, ::skip],
                    length=3.5,
                    linewidth=0.35,
                )
            elif wind_type == "stream":
                ax.streamplot(
                    xgrid, ygrid, u, v, color="gray", linewidth=0.35, density=1
                )

        ax.contour(
            xgrid, ygrid, model_map, [0.5, 1.5],
            colors="black", linewidths=0.5, linestyles="-"
        )
        ax.contour(
            xgrid, ygrid, model_lon, np.linspace(-180, 180, 361), 
            colors="gray", linewidths=0.35, linestyles=":"
        )
        ax.contour(
            xgrid, ygrid, model_lat, np.linspace(-90, 90, 181), 
            colors="gray", linewidths=0.35, linestyles=":"
        )

        ax.set_xlim(xgrid.min(), xgrid.max())
        ax.set_ylim(ygrid.min(), ygrid.max())
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
