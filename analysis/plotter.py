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
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.axes import Axes
from matplotlib.colors import CenteredNorm, LogNorm, PowerNorm, TwoSlopeNorm
from matplotlib.figure import Figure
from scipy.interpolate import griddata
from omegaconf import DictConfig

from analysis.data_manager import AnalysisDataManager
from analysis.plot_meta import ANALYSIS_PLOT_CONFIGS
from src.utils.data_type import DataType, Level
from src.const import MODEL_CODE

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

    def __init__(
        self,
        cfg: DictConfig,
        manager: AnalysisDataManager,
        output_dir: Path,
        exp_code: str = "analysis",
    ):
        """Initializes the WeatherPlotter.

        Args:
            cfg (DictConfig): The Hydra configuration object.
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): Target directory for saving plot images.
            exp_code (str): An experiment code to use as a prefix for filenames.
        """
        self.cfg: DictConfig = cfg
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.map_projection = ccrs.PlateCarree()
        self.exp_code: str = exp_code

        self._plot_dispatch_table: Dict[str, Callable[..., Any]] = {
            "wind_speed": self._plot_wind_speed,
            "vorticity": self._plot_vorticity,
            "temperature": self._plot_temperature,
            "column_max_qt": self._plot_column_max_qt,
            "hydrometeors_mixing_ratio": self._plot_mixing_ratio,
            "theta_e": self._plot_theta_e,
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
            f"DLAMP.tw | {MODEL_CODE} | Valid: {valid_time}Z | Initial: {start_time}Z {step_str}",
            fontsize=8, y=0.95
        )

        for idx, config in enumerate(ANALYSIS_PLOT_CONFIGS):
            ax_fc: Axes = fig.add_subplot(gs[0, idx])
            ax_gt: Axes = fig.add_subplot(gs[1, idx])

            plot_func_key: str = config["plot_func_key"]

            try:
                plot_func: Callable[..., Any] = self._plot_dispatch_table[plot_func_key]
                plot_func(ax_fc, ax_gt, forecast_step, config)
            except KeyError:
                logger.error(
                    "Plot function key '%s' not found in dispatch table.",
                    plot_func_key
                )
                continue

        start_time_str: str = self.manager.start_time.strftime('%Y%m%d_%H%M')
        step_str_for_filename: str
        if forecast_step == -1:
            step_str_for_filename = "F000H"
        else:
            step_str_for_filename = f"F{forecast_step + 1:03d}H"

        filename: str = f"{self.exp_code}_{start_time_str}_{step_str_for_filename}.png"
        output_path: Path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved analysis plot to {output_path}")
        return output_path

    def _plot_wind_speed(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots wind speed and geopotential height."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.PH, level)
        wspd_fc: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=False)
        u_fc, v_fc = self.manager._get_wind_components(step, level)

        time: datetime = self.manager.get_forecast_time(step)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.PH, level)
        wspd_gt: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=True)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)

        self._generic_grid_plot(
            ax_fc, f"FC: {title}", wspd_fc, z_fc, (u_fc, v_fc), "stream",
            cmap, vmin, vmax, unit, colorbar_scale, colorbar_gamma,
            colorbar_center=colorbar_center
        )
        self._generic_grid_plot(
            ax_gt, f"GT: {title}", wspd_gt, z_gt, (u_gt, v_gt), "stream",
            cmap, vmin, vmax, unit, colorbar_scale, colorbar_gamma,
            colorbar_center=colorbar_center
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
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        u_fc, v_fc = self.manager._get_wind_components(step, level)
        vort_fc: np.ndarray = self.manager.get_relative_vorticity(step, level, False) * 1e6
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.PH, level)

        time: datetime = self.manager.get_forecast_time(step)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)
        vort_gt: np.ndarray = self.manager.get_relative_vorticity(step, level, True) * 1e6
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.PH, level)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            np.clip(vort_fc, vmin, vmax),
            z_fc,
            (u_fc, v_fc), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            np.clip(vort_gt, vmin, vmax),
            z_gt,
            (u_gt, v_gt), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )

    # --- 新增：繪製 Theta-e 的方法 ---
    def _plot_theta_e(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots equivalent potential temperature (Theta-e) with geopotential
        height contours and 10-m wind streams, mirroring the temperature panel.
        """
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        # Forecast fields
        thetae_fc: np.ndarray = self.manager.get_equivalent_potential_temperature(
            step, level, is_gt=False
        )
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.PH, level)
        u_fc, v_fc = self.manager._get_wind_components(step, level)

        # Ground-truth fields
        time: datetime = self.manager.get_forecast_time(step)
        thetae_gt: np.ndarray = self.manager.get_equivalent_potential_temperature(
            step, level, is_gt=True
        )
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.PH, level)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)

        # Plot: FC (theta-e shading + Z contours + streamlines)
        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            thetae_fc,
            z_fc,
            (u_fc, v_fc),
            "stream",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

        # Plot: GT (theta-e shading + Z contours + streamlines)
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            thetae_gt,
            z_gt,
            (u_gt, v_gt),
            "stream",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
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
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        t_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.TK, level)
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.PH, level)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        t_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.TK, level)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.PH, level)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            t_fc,
            z_fc,
            (u10_fc, v10_fc), "stream",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            t_gt,
            z_gt,
            (u10_gt, v10_gt), "stream",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )

    def _plot_mixing_ratio(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots 925hPa Qt and 10-meter wind."""
        title: str = config["title"]
        level: Optional[Level] = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        qt_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Qt, level)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        qt_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Qt, level)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            qt_fc,
            None,
            (u10_fc, v10_fc), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            qt_gt,
            None,
            (u10_gt, v10_gt), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )

    def _plot_column_max_qt(
        self, ax_fc: Axes, ax_gt: Axes, step: int, config: Dict[str, Any]
    ):
        """Plots column-maximum Qt and 10-meter wind."""
        title: str = config["title"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: Optional[str] = config.get("colorbar_scale")
        colorbar_gamma: Optional[float] = config.get("colorbar_gamma")
        colorbar_center: Optional[float] = config.get("colorbar_center")

        qt_fc: np.ndarray = self.manager.get_column_max_qt(step, False)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        qt_gt: np.ndarray = self.manager.get_column_max_qt(step, True)
        time: datetime = self.manager.get_forecast_time(step)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            qt_fc,
            None,
            (u10_fc, v10_fc), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            qt_gt,
            None,
            (u10_gt, v10_gt), "barbs",
            cmap, vmin, vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center
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
        colorbar_scale: Optional[str] = None,
        colorbar_gamma: Optional[float] = None,
        colorbar_center: Optional[float] = None,
    ):
        """Plots data on a model grid with transformed coastlines.

        Args:
            ax: The matplotlib Axes object to plot on.
            title: The title for the subplot.
            color_data: 2D data for the pcolormesh.
            contour_data: 2D data for contours.
            wind_data: (u, v) winds.
            wind_type: 'stream' for streamplot or 'barbs' for barbs.
            cmap: The colormap for the color_data.
            vmin: The minimum value for the color scale.
            vmax: The maximum value for the color scale.
            unit: The unit label for the colorbar.
            colorbar_scale: Scale for the colorbar.
            colorbar_gamma: Gamma value for the power scale.
            colorbar_center: Center value for CenteredNorm or TwoSlopeNorm.
        """
        model_lon: np.ndarray = self.manager.results["lon"]
        model_lat: np.ndarray = self.manager.results["lat"]
        model_map: np.ndarray = self.manager.results["mask"]
        ny, nx = color_data.shape
        x_indices: np.ndarray = np.arange(nx)
        y_indices: np.ndarray = np.arange(ny)
        xgrid, ygrid = np.meshgrid(x_indices, y_indices)

        ax.set_title(title, fontsize=6)

        norm = None
        if colorbar_scale == 'log':
            safe_vmin = vmin if vmin > 0 else 1e-6  # Avoid vmin <= 0 for LogNorm
            norm = LogNorm(
                vmin=safe_vmin,
                vmax=vmax
            )
            if vmin <= 0:
                logger.warning(
                    f"LogNorm received vmin <= 0 ({vmin}). "
                    f"Adjusting vmin to {safe_vmin} for plotting '{title}'."
                )
        elif colorbar_scale == 'power' and colorbar_gamma is not None:
            norm = PowerNorm(
                gamma=colorbar_gamma,
                vmin=vmin,
                vmax=vmax
            )
        elif colorbar_scale == 'centered' and colorbar_center is not None:
            halfrange = max(
                abs(vmax - colorbar_center),
                abs(vmin - colorbar_center)
            )
            norm = CenteredNorm(
                vcenter=colorbar_center,
                halfrange=halfrange
            )
        elif colorbar_scale == 'two_slope' and colorbar_center is not None:
            norm = TwoSlopeNorm(
                vcenter=colorbar_center,
                vmin=vmin,
                vmax=vmax
            )
        else:
            norm = mpl.colors.Normalize(
                vmin=vmin,
                vmax=vmax,
            )

        pcm = ax.pcolormesh(
            xgrid,
            ygrid,
            color_data,
            cmap=cmap,
            shading="auto",
            norm=norm,
        )
        cbar = plt.colorbar(
            pcm, ax=ax,
            orientation="horizontal",
            pad=0.06,
            shrink=0.95
        )
        cbar.set_label(unit, size=4)
        cbar.ax.tick_params(labelsize=4, size=4, tickdir="in")

        if contour_data is not None:
            ax.contour(
                xgrid,
                ygrid,
                contour_data,
                colors="k",
                linewidths=0.4
            )

        if wind_data:
            u, v = wind_data
            skip = 11
            if wind_type == "barbs":
                ax.barbs(
                    xgrid[::skip, ::skip],
                    ygrid[::skip, ::skip],
                    u[::skip, ::skip] / 0.5144,
                    v[::skip, ::skip] / 0.5144,
                    color="gray",
                    length=3.5,
                    linewidth=0.35
                )
            elif wind_type == "stream":
                ax.streamplot(
                    xgrid,
                    ygrid,
                    u,
                    v,
                    color="navy",
                    linewidth=0.35,
                    density=1.0,
                    arrowstyle="->",
                )

        ax.contour(
            xgrid, ygrid, model_map, [0.5, 1.5],
            colors="black", linewidths=0.5, linestyles="-"
        )
        ax.contour(
            xgrid, ygrid, model_lon, np.linspace(-180, 180, 73),
            colors="gray", linewidths=0.35, linestyles=":"
        )
        ax.contour(
            xgrid, ygrid, model_lat, np.linspace(-90, 90, 37),
            colors="gray", linewidths=0.35, linestyles=":"
        )

        ax.set_xlim(xgrid.min(), xgrid.max())
        ax.set_ylim(ygrid.min(), ygrid.max())
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])

    def create_cross_section_figure(
        self,
        start_point: Tuple[float, float],
        end_point: Tuple[float, float],
        forecast_step: int,
        is_gt: bool = False,
        band_width_km: float = 0.0,
        num_points: int = 100,
    ) -> Path:
        """
        繪製指定兩點連線的垂直剖面圖。
        填色圖(contourf)為 Qv (水氣混和比)，等高線(contour)為位溫。

        Args:
            start_point (Tuple[float, float]): 起始點 (緯度, 經度)。
            end_point (Tuple[float, float]): 結束點 (緯度, 經度)。
            forecast_step (int): 預報步長 (0-indexed)。
            is_gt (bool): 是否使用 ground truth 資料。
            band_width_km (float): 剖面帶寬(km)。若為 0，則為"一刀切"剖面。
                                   若大於 0，則在剖面線法線方向上取此寬度的平均值。
            num_points (int): 剖面線上取樣點的數量。

        Returns:
            Path: 儲存的圖片路徑。
        """
        logger.info(f"Generating cross section from {start_point} to {end_point}...")

        # 1. 準備網格和資料
        model_lon: np.ndarray = self.manager.results["lon"]
        model_lat: np.ndarray = self.manager.results["lat"]
        points = np.vstack((model_lon.ravel(), model_lat.ravel())).T

        levels_enum = self.manager.levels
        pressure_levels = np.array([float(l.value.replace('hPa', '')) for l in levels_enum])

        # 獲取所有垂直層的 3D 資料
        all_level_qv = []
        all_level_t = []
        time = self.manager.get_forecast_time(forecast_step)

        for level in levels_enum:
            if is_gt:
                qv = self.manager.get_ground_truth_data(time, DataType.Qt, level)
                t = self.manager.get_ground_truth_data(time, DataType.TK, level)
            else:
                qv = self.manager.get_forecast_data(forecast_step, DataType.Qt, level)
                t = self.manager.get_forecast_data(forecast_step, DataType.TK, level)
            all_level_qv.append(qv)
            all_level_t.append(t)

        qv_3d = np.stack(all_level_qv)
        t_3d = np.stack(all_level_t)

        # 2. 定義剖面路徑
        lats = np.linspace(start_point[0], end_point[0], num_points)
        lons = np.linspace(start_point[1], end_point[1], num_points)
        path_points = list(zip(lats, lons))

        distances = [0.0]
        for i in range(1, len(path_points)):
            dist = great_circle(path_points[i-1], path_points[i]).kilometers
            distances.append(distances[-1] + dist)

        # 3. 內插資料到剖面路徑上
        cross_section_qv = np.zeros((len(pressure_levels), num_points))
        cross_section_theta = np.zeros((len(pressure_levels), num_points))

        for i, (lat, lon) in enumerate(path_points):
            query_points = np.array([[lon, lat]])

            if band_width_km <= 0: # "一刀切"模式
                for level_idx in range(len(pressure_levels)):
                    grid_qv = griddata(points, qv_3d[level_idx].ravel(), query_points, method='linear')
                    grid_t = griddata(points, t_3d[level_idx].ravel(), query_points, method='linear')
                    cross_section_qv[level_idx, i] = grid_qv[0]
                    cross_section_theta[level_idx, i] = grid_t[0] * (1000.0 / pressure_levels[level_idx]) ** (R_d / c_p)
            else: # 帶寬平均模式
                # 計算剖面線的法線方向
                if i < num_points - 1:
                    d_lat = lats[i+1] - lats[i]
                    d_lon = lons[i+1] - lons[i]
                else: # 最後一點使用前一點的方向
                    d_lat = lats[i] - lats[i-1]
                    d_lon = lons[i] - lons[i-1]

                # 法線向量 (注意經度在赤道附近與距離的換算)
                norm_vec = np.array([-d_lon * np.cos(np.deg2rad(lat)), d_lat])
                norm_vec /= np.linalg.norm(norm_vec)

                # 在法線方向上取樣5個點進行平均
                sample_points_ll = []
                for s in np.linspace(-0.5, 0.5, 5):
                    # 將帶寬轉換為經緯度偏移量 (近似)
                    offset_lat = s * (band_width_km / 111.0) * norm_vec[1]
                    offset_lon = s * (band_width_km / (111.0 * np.cos(np.deg2rad(lat)))) * norm_vec[0]
                    sample_points_ll.append([lon + offset_lon, lat + offset_lat])

                for level_idx in range(len(pressure_levels)):
                    grid_qv = griddata(points, qv_3d[level_idx].ravel(), sample_points_ll, method='linear')
                    grid_t = griddata(points, t_3d[level_idx].ravel(), sample_points_ll, method='linear')

                    cross_section_qv[level_idx, i] = np.nanmean(grid_qv)
                    theta = np.nanmean(grid_t) * (1000.0 / pressure_levels[level_idx]) ** (R_d / c_p)
                    cross_section_theta[level_idx, i] = theta

        # 4. 繪圖
        fig, ax = plt.subplots(figsize=(12, 6))

        # 繪製 Qv (水氣) 填色圖
        # 註: 請求是 contourf: Qv 和 contour: Qv，但目前資料只有 Qv。
        # 我們用位溫 theta 做 contour，這是更常見且有意義的物理剖面圖。
        qv_levels = np.linspace(0, 0.02, 21) # kg/kg
        cf = ax.contourf(distances, pressure_levels, cross_section_qv, levels=qv_levels, cmap='GnBu', extend='max')
        cbar = fig.colorbar(cf, ax=ax, label='Specific Humidity (Qv) [kg kg-1]')

        # 繪製位溫等高線
        theta_levels = np.arange(280, 400, 4) # K
        cs = ax.contour(distances, pressure_levels, cross_section_theta, levels=theta_levels, colors='k', linewidths=0.8)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%1.0f')

        ax.set_ylim(1000, 150) # Y軸反轉，地面在下
        ax.set_yscale('log')
        ax.set_yticks([1000, 850, 700, 500, 300, 200])
        ax.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
        ax.set_ylabel('Pressure (hPa)')
        ax.set_xlabel('Distance (km)')

        title_prefix = "Ground Truth" if is_gt else "Forecast"
        valid_time = self.manager.get_forecast_time(forecast_step).strftime('%Y-%m-%d %H:%M Z')
        ax.set_title(
            f"{title_prefix} Cross Section at {valid_time}\n"
            f"From ({start_point[0]:.2f}, {start_point[1]:.2f}) to ({end_point[0]:.2f}, {end_point[1]:.2f})"
        )

        # 在 X 軸上標示起點和終點
        ax.set_xticks(np.linspace(0, distances[-1], 5))
        secax = ax.secondary_xaxis('top')
        secax.set_xticks([distances[0], distances[-1]])
        secax.set_xticklabels([f'Start\n({start_point[0]:.1f}, {start_point[1]:.1f})',
                               f'End\n({end_point[0]:.1f}, {end_point[1]:.1f})'])

        ax.grid(True, linestyle='--', alpha=0.6)

        # 5. 儲存圖片
        filename = f"cross_section_{'gt' if is_gt else 'fc'}_{forecast_step:03d}.png"
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved cross section plot to {output_path}")
        return output_path
