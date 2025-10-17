# analysis/data_manager.py
"""Manages access to forecast and ground truth weather data.

This module provides the AnalysisDataManager class, which serves as a
high-level interface for accessing model forecast outputs and corresponding
ground truth data. It disassembles raw NumPy arrays into physical variables
and levels, and computes derived quantities like wind speed and vorticity.

Usage:
    data_manager = AnalysisDataManager(cfg, results)
    # Get F000H data (returns ground truth)
    fc_f000 = data_manager.get_forecast_data(-1, DataType.TK, Level.Hpa500)
    # Get vorticity for the 3rd forecast hour
    vort_f003 = data_manager.get_relative_vorticity(2, Level.Hpa500)
"""

import logging
import re  # NEW: robust pressure parsing with regex
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Tuple

import numpy as np
from omegaconf import DictConfig

from src.const import DATA_PATH
from src.utils import DataCompose, DataType, Level
from src.utils import DataGenerator

logger = logging.getLogger(__name__)

# --- Physical Constants for Meteorological Calculations ---
R_d = 287.058  # J kg^-1 K^-1, Gas constant for dry air
c_p = 1004.0  # J kg^-1 K^-1, Specific heat of dry air at constant pressure
kappa = R_d / c_p  # Poisson constant, ~0.286
epsilon = 0.622  # Ratio of molar masses of water vapor to dry air
L_v = 2.5e6  # J kg^-1, Latent heat of vaporization

class AnalysisDataManager:
    """Handles disassembly and retrieval of forecast and ground truth data.

    This class takes raw model output, provides methods to access specific
    variables, and calculates derived meteorological fields for analysis
    and plotting. It also handles the special case for F000H by providing
    ground truth data as the initial forecast state.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        results (Dict[str, Any]): The dictionary from PredictionRunner.
        start_time (datetime): The initial time of the forecast run.
        data_generator (DataGenerator): Instance for fetching ground truth.
        data_compositions (List[DataCompose]): Variable-level combinations.
        upper_vars (List[DataType]): Ordered list of upper-air variables.
        surface_vars (List[DataType]): Ordered list of surface variables.
        pressure_levels (List[Level]): Ordered list of pressure levels.
    """

    def __init__(self, cfg: DictConfig, prediction_results: Dict[str, Any]):
        """Initializes the AnalysisDataManager.

        Args:
            cfg (DictConfig): The Hydra configuration object.
            prediction_results (Dict[str, Any]): Output from
                PredictionRunner.run(). It must contain 'output_upper',
                'output_surface', 'lat', 'lon', and 'start_time'.
        """
        self.cfg: DictConfig = cfg
        self.results: Dict[str, Any] = prediction_results
        self.start_time: datetime = self.results["start_time"]
        self.data_generator: DataGenerator = DataGenerator(
            cfg.data.data_shape, cfg.data.image_shape
        )

        self.data_compositions: List[DataCompose] = (
            DataCompose.from_config(cfg.data.train_data)
        )
        self.upper_vars: List[DataType] = DataCompose.get_all_vars(
            self.data_compositions, only_upper=True
        )
        self.surface_vars: List[DataType] = DataCompose.get_all_vars(
            self.data_compositions, only_surface=True
        )
        self.pressure_levels: List[Level] = DataCompose.get_all_levels(
            self.data_compositions, only_upper=True
        )
        self._qw_output_unit_gkg: bool = self.cfg.plot.get('qw_display_unit', 'kg/kg').lower() == 'g/kg'
        logger.info(f"AnalysisDataManager initialized. Qw display unit for plots set to g/kg: {self._qw_output_unit_gkg}")

    def _get_pressure_from_level(self, level: Level) -> float:
        """Extract pressure in Pascals [Pa] from a Level object robustly.

        Args:
            level (Level): e.g., Level.Hpa500 (upper-air constant-pressure level).

        Returns:
            float: Pressure in Pascals [Pa].

        Raises:
            ValueError: If the level is a surface level or pressure cannot be parsed.
        """
        if level.is_surface():
            # This helper is for constant-pressure (upper-air) levels only.
            # Surface pressure must be read from data (e.g., PSFC).
            raise ValueError(
                f"Cannot extract a fixed pressure from a surface level: {level.name}"
            )
        # Prefer a string payload if available; fall back to str(level)
        text = getattr(level, "value", str(level))
        m = re.search(r"\d+(?:\.\d+)?", str(text))
        if not m:
            raise ValueError(f"Could not parse pressure value from level: {text}")
        pressure_hpa = float(m.group(0))
        return pressure_hpa * 100.0  # hPa -> Pa

    @lru_cache(maxsize=128)
    def get_forecast_data(
        self, forecast_step: int, variable: DataType, level: Level
    ) -> np.ndarray:
        """Retrieves a specific forecast variable grid.

        Handles the special case where `forecast_step = -1`, which corresponds
        to the initial state (F000H) and returns the ground truth data.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            variable (DataType): The meteorological variable to retrieve.
            level (Level): The pressure or surface level to retrieve.

        Returns:
            np.ndarray: A 2D NumPy array (height, width) of forecast data.
                Units are standard (e.g., K for temperature, m/s for wind).

        Raises:
            ValueError: If the variable or level is not found in the config.
            IndexError: If the forecast_step is out of bounds.
        """
        if forecast_step == -1:  # F000H case (ground truth)
            return self.get_ground_truth_data(self.start_time, variable, level)

        seq_len: int = self.results["output_upper"].shape[1]
        if not (0 <= forecast_step < seq_len):
            raise IndexError(
                f"forecast_step {forecast_step} out of range (0..{seq_len-1})."
            )

        if level.is_surface():
            try:
                var_idx: int = self.surface_vars.index(variable)
                data: np.ndarray = self.results["output_surface"][
                    0, forecast_step, 0, :, :, var_idx
                ]
            except ValueError:
                valid: str = ", ".join([v.name for v in self.surface_vars])
                raise ValueError(
                    f"Surface variable '{variable.name}' not found. "
                    f"Available: [{valid}]"
                )
        else:
            try:
                var_idx: int = self.upper_vars.index(variable)
                lvl_idx: int = self.pressure_levels.index(level)
                data: np.ndarray = self.results["output_upper"][
                    0, forecast_step, lvl_idx, :, :, var_idx
                ]
            except ValueError:
                valid_v: str = ", ".join([v.name for v in self.upper_vars])
                valid_l: str = ", ".join([l.name for l in self.pressure_levels])
                raise ValueError(
                    f"Upper-air var/level '{variable.name}/{level.name}' "
                    f"not found. Available vars: [{valid_v}], "
                    f"levels: [{valid_l}]"
                )
        return data.astype(np.float32)

    def get_ground_truth_data(
        self, time: datetime, variable: DataType, level: Level
    ) -> np.ndarray:
        """Retrieves the corresponding ground truth data for a given time.

        Args:
            time (datetime): The timestamp for which to retrieve GT data.
            variable (DataType): The meteorological variable.
            level (Level): The pressure or surface level.

        Returns:
            np.ndarray: A 2D NumPy array of ground truth data.
        """
        dc: DataCompose = DataCompose(var_name=variable, level=level)
        return self.data_generator.yield_data(time, dc).astype(np.float32)

    def get_forecast_time(self, forecast_step: int) -> datetime:
        """Calculates the calendar time for a given forecast step.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).

        Returns:
            datetime: The wall-clock time of the specified forecast step.
        """
        if forecast_step == -1:
            return self.start_time
        time_interval: timedelta = timedelta(**self.cfg.inference.output_itv)
        return self.start_time + (forecast_step + 1) * time_interval

    def _get_wind_components(
        self,
        forecast_step: int,
        level: Level
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper to get U and V wind components for a forecast step."""
        u: np.ndarray = self.get_forecast_data(forecast_step, DataType.UM, level)
        v: np.ndarray = self.get_forecast_data(forecast_step, DataType.VM, level)
        return u, v

    def _get_gt_wind_components(
        self,
        time: datetime,
        level: Level
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Helper to get U and V ground truth wind components for a time."""
        u: np.ndarray = self.get_ground_truth_data(time, DataType.UM, level)
        v: np.ndarray = self.get_ground_truth_data(time, DataType.VM, level)
        return u, v

    def get_wind_speed(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates wind speed from U and V components.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            level (Level): The pressure or surface level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of wind speed in meters per second.
        """
        if is_gt:
            time: datetime = self.get_forecast_time(forecast_step)
            u: np.ndarray
            v: np.ndarray
            u, v = self._get_gt_wind_components(time, level)
        else:
            u: np.ndarray
            v: np.ndarray
            u, v = self._get_wind_components(forecast_step, level)
        return np.sqrt(u**2 + v**2)

    def get_relative_vorticity(
        self,
        forecast_step: int,
        level: Level,
        is_gt: bool = False
    ) -> np.ndarray:
        """Calculates relative vorticity using a centered finite difference.

        This method uses `np.gradient` with a fixed grid spacing.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            level (Level): The pressure level (must be an upper-air level).
            dx (float): The grid spacing in meters for the data (e.g., 2000.0 for GT, 4000.0 for FC).
            is_gt (bool): If True, uses GT data.

        Returns:
            np.ndarray: 2D grid of relative vorticity in units of s^-1.
        """
        u: np.ndarray
        v: np.ndarray
        if is_gt:
            time: datetime = self.get_forecast_time(forecast_step)
            u, v = self._get_gt_wind_components(time, level)
            dx = self.cfg.plot.grid_spacing.ground_truth_m
            logger.debug(f"GT shape: u={np.shape(u)}, v={np.shape(v)}")
        else:
            u, v = self._get_wind_components(forecast_step, level)
            dx = self.cfg.plot.grid_spacing.forecast_m
            logger.debug(f"FC shape: u={np.shape(u)}, v={np.shape(v)}")

        du_dy: np.ndarray
        dv_dx: np.ndarray
        dv_dx, du_dy = np.gradient(v, dx, axis=1), np.gradient(u, dx, axis=0)
        vorticity: np.ndarray = dv_dx - du_dy
        return vorticity

    def get_column_max_qw(
        self,
        forecast_step: int,
        is_gt: bool = False
    ) -> np.ndarray:
        """Calculates the maximum water content (Qw) in the vertical column.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of the maximum Qw value at each (x, y) point.
                Units are kg/kg.

        Raises:
            ValueError: If no Qw data is defined in the configuration.
        """
        qw_levels: List[Level] = [
            dc.level for dc in self.data_compositions
            if dc.var_name == DataType.Qt
        ]
        if not qw_levels:
            raise ValueError("No Qw data found in configuration.")

        all_qw_layers: List[np.ndarray] = []
        time: datetime = self.get_forecast_time(forecast_step)
        for level in qw_levels:
            data: np.ndarray
            if is_gt:
                data = self.get_ground_truth_data(
                    time, DataType.Qt, level
                )
            else:
                data = self.get_forecast_data(
                    forecast_step, DataType.Qt, level
                )
            all_qw_layers.append(data)

        return np.max(np.stack(all_qw_layers, axis=0), axis=0)

    def get_potential_temperature(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates potential temperature (Theta).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of potential temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)

        pressure_pa = self._get_pressure_from_level(level)
        p0 = 100000.0  # Pa
        theta = T * (p0 / pressure_pa) ** kappa
        return theta

    def get_saturation_vapor_pressure(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates saturation vapor pressure (es).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of saturation vapor pressure in Pascals [Pa].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)

        T_c = T - 273.15
        es = 611.2 * np.exp((17.67 * T_c) / (T_c + 243.5))
        return es

    def get_dew_point_temperature(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates dew point temperature (Td) from mixing ratio r (kg/kg).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of dew point temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        pressure_pa = self._get_pressure_from_level(level)
        e = (r * pressure_pa) / (epsilon + r)
        e = np.maximum(e, 1.0)

        val = np.log(e / 611.2)
        Td_c = (243.5 * val) / (17.67 - val)
        Td = Td_c + 273.15
        return Td

    def get_relative_humidity(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates relative humidity (RH) from mixing ratio r (kg/kg).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of relative humidity in percent [%].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        pressure_pa = self._get_pressure_from_level(level)
        e = (r * pressure_pa) / (epsilon + r)
        T_c = T - 273.15
        es = 611.2 * np.exp((17.67 * T_c) / (T_c + 243.5))

        rh = (e / es) * 100.0
        return np.clip(rh, 0, 100)

    def get_equivalent_potential_temperature(
        self, forecast_step: int, level: Level, is_gt: bool = False
    ) -> np.ndarray:
        """Calculates equivalent potential temperature (Theta-e) using Bolton (1980).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of equivalent potential temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        # 1) Use the existing method to get potential temperature (reduces duplication)
        theta = self.get_potential_temperature(forecast_step, level, is_gt)
        # 2) Get pressure for vapor pressure / dewpoint
        pressure_pa = self._get_pressure_from_level(level)

        e = (r * pressure_pa) / (epsilon + r)
        e = np.maximum(e, 1.0)
        val = np.log(e / 611.2)
        Td_c = (243.5 * val) / (17.67 - val)
        Td = Td_c + 273.15

        Tlcl = 1.0 / (1.0 / (Td - 56.0) + np.log(T / Td) / 800.0) + 56.0

        theta_e = theta * np.exp((L_v * r) / (c_p * Tlcl)) * (T / Tlcl) ** (0.28 * r)
        return theta_e
