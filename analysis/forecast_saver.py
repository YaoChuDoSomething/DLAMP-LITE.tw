# analysis/forecast_saver.py
"""Saves forecast data to NetCDF files in a WRF-compatible format.

This module provides the ForecastSaver class, which takes disassembled
forecast data and saves each time step into a separate NetCDF file that
adheres to WRF naming conventions for dimensions, coordinates, and variables.
It uses metadata defined in `analysis.netcdf_meta`.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import xarray as xr
import cftime

from analysis.data_manager import AnalysisDataManager
from analysis.netcdf_meta import GLOBAL_ATTRIBUTES, VARIABLE_ATTRIBUTES
from src.utils.data_type import DataType, Level
from src.const import KG_PER_KG

logger = logging.getLogger(__name__)


class ForecastSaver:
    """Serializes forecast results into WRF-style NetCDF files.

    Attributes:
        manager (AnalysisDataManager): The data manager instance.
        output_dir (Path): Directory where NetCDF files will be saved.
    """

    def __init__(
        self,
        manager: AnalysisDataManager,
        output_dir: Path,
        earth2studio_output_dir: Optional[Path] = None,
        exp_code: str = "dlamp",
    ):
        """Initializes the ForecastSaver.

        Args:
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): The target directory for saving WRF-style files.
            earth2studio_output_dir (Optional[Path]): Target directory for
                saving Earth2Studio-ready NetCDF files.
            exp_code (str): An experiment code to use as a prefix for filenames.
        """
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.exp_code: str = exp_code

        self.earth2studio_output_dir: Optional[Path] = earth2studio_output_dir
        if self.earth2studio_output_dir:
            self.earth2studio_output_dir.mkdir(parents=True, exist_ok=True)

    def save_all_forecasts(self) -> None:
        """Saves all forecast steps (F001H onwards) to NetCDF files."""
        num_steps: int = self.manager.results["output_upper"].shape[1]
        logger.info("Saving %d forecast steps to NetCDF.", num_steps)

        for step in range(num_steps):
            self._save_single_step(step)

        logger.info("Saved all forecast steps to %s", self.output_dir)

    def save_earth2studio_forecasts(self) -> None:
        """Saves all forecast steps (F001H onwards) to Earth2Studio-ready NetCDF files."""
        if not self.earth2studio_output_dir:
            logger.warning("Earth2Studio output directory not set. Skipping save.")
            return

        num_steps: int = self.manager.results["output_upper"].shape[1]
        logger.info("Saving %d forecast steps to Earth2Studio-ready NetCDF.", num_steps)

        for step in range(num_steps):
            self._save_earth2studio_format(step)

        logger.info("Saved all Earth2Studio-ready forecast steps to %s", self.earth2studio_output_dir)

    def _save_earth2studio_format(self, forecast_step: int) -> None:
        """Saves a single forecast step to an Earth2Studio-compatible NetCDF file.

        Args:
            forecast_step (int): The 0-indexed forecast step to save.
        """
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        lat: np.ndarray = self.manager.results["lat"]
        lon: np.ndarray = self.manager.results["lon"]
        H, W = lat.shape

        # Determine the full list of variables and their order
        # This needs to be consistent for the 'variable' dimension
        all_variables_with_levels: List[Tuple[DataType, Level]] = []
        for level in self.manager.pressure_levels:
            for var in self.manager.upper_vars:
                all_variables_with_levels.append((var, level))
        for var in self.manager.surface_vars:
            # For surface variables, use Level.Surface as a consistent identifier
            all_variables_with_levels.append((var, Level.Surface))

        variable_names: List[str] = []
        for var_type, level_type in all_variables_with_levels:
            # Create a unique string identifier for each variable-level combination
            if level_type.is_surface():
                variable_names.append(f"{var_type.name}_sfc")
            else:
                variable_names.append(f"{var_type.name}_{level_type.nc_key}hPa")

        num_variables = len(variable_names)
        # The prompt states variable = 73. We should log a warning if it doesn't match.
        if num_variables != 73:
            logger.warning(
                f"Number of variables ({num_variables}) does not match "
                "expected Earth2Studio format (73). Proceeding with available variables."
            )

        # Initialize the 4D data array
        initial_data_array = np.zeros((1, num_variables, H, W), dtype=np.float32)

        # Populate the data array
        for idx, (var_type, level_type) in enumerate(all_variables_with_levels):
            data: np.ndarray = self.manager.get_forecast_data(
                forecast_step, var_type, level_type
            )
            # Handle Qw unit conversion if necessary (from g/kg to kg/kg)
            # The manager's _qw_output_unit_gkg indicates if Qw was converted to g/kg for plotting.
            # If so, convert it back to kg/kg for the Earth2Studio output.
            if var_type == DataType.Qt:
                data = data / 1000.0

            initial_data_array[0, idx, :, :] = data

        # Calculate time as hours since 0001-01-01 00:00:00.0
        reference_time = cftime.DatetimeGregorian(1, 1, 1, 0, 0, 0)
        forecast_cftime = cftime.DatetimeGregorian(
            forecast_time.year, forecast_time.month, forecast_time.day,
            forecast_time.hour, forecast_time.minute, forecast_time.second
        )
        time_value = (forecast_cftime - reference_time).total_seconds() / 3600.0

        # Create xarray Dataset
        ds = xr.Dataset(
            {
                "initial_data": (
                    ("time", "variable", "lat", "lon"),
                    initial_data_array,
                    {
                        "description": "Initial forecast data",
                        "units": "various (see variable names)",
                    },
                )
            },
            coords={
                "time": (
                    "time", [time_value],
                    {
                        "units": "hours since 0001-01-01 00:00:00.0",
                        "calendar": "proleptic_gregorian",
                    },
                ),
                "variable": ("variable", variable_names),
                "lat": ("lat", lat[:, 0]),  # Assuming lat is (H, W) and we need a 1D array
                "lon": ("lon", lon[0, :]),  # Assuming lon is (H, W) and we need a 1D array
            },
        )

        filename: str = f"earth2studio_{self.exp_code}_{forecast_time.strftime('%Y%m%d_%H%M%S')}.nc"
        output_path: Path = self.earth2studio_output_dir / filename

        encoding: Dict[str, Dict[str, Any]] = {
            "initial_data": {"zlib": True, "complevel": 4}
        }
        ds.to_netcdf(output_path, encoding=encoding)
        logger.info(f"Saved Earth2Studio-ready NetCDF to {output_path}")

    def _save_single_step(self, forecast_step: int) -> None:
        """Saves a single forecast step to a WRF-compatible NetCDF file.

        Args:
            forecast_step (int): The 0-indexed forecast step to save.
        """
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        lat: np.ndarray = self.manager.results["lat"]
        lon: np.ndarray = self.manager.results["lon"]
        mask: np.ndarray = self.manager.results["mask"]
        H: int
        W: int
        H, W = lat.shape
        time_str: str = forecast_time.strftime("%Y-%m-%d_%H:%M:%S")

        coords: Dict[str, Any] = {
            "Time": (("Time",), [0]),
            "south_north": (("south_north",), np.arange(H, dtype=np.int32)),
            "west_east": (("west_east",), np.arange(W, dtype=np.int32)),
        }

        data_vars: Dict[str, Any] = {
            "Times": (
                ("Time", "DateStrLen"),
                np.array([list(time_str.ljust(19))], dtype="S1"),
            ),
            "XLAT": (("Time", "south_north", "west_east"), lat[None, ...]),
            "XLONG": (("Time", "south_north", "west_east"), lon[None, ...]),
            "LANDMASK": (("Time", "south_north", "west_east"), mask[None, ...]),
        }

        # Per RWRF format, pressure levels should be from high to low (e.g., 1000 -> 50)
        # The manager provides them from low to high, so we reverse them.
        pressure_levels_reversed = self.manager.pressure_levels[::-1]
        pres_levels_val: np.ndarray = np.array(
            [float(lv.nc_key) for lv in pressure_levels_reversed],
            dtype=np.float32,
        )
        data_vars["pres_levels"] = (("pres_bottom_top",), pres_levels_val)

        # Initialize containers for upper-air data
        upper_air_cubes: Dict[str, np.ndarray] = {
            var.name: np.full(
                (1, len(pres_levels_val), H, W), np.nan, dtype=np.float32
            )
            for var in self.manager.upper_vars
        }

        # Map from internal enum names to NetCDF variable keys
        key_map: Dict[str, str] = {
            "umet10": "umet10",
            "vmet10": "vmet10",
            "t2m": "T2",
            "q2m": "Q2",
            "psfc": "PSFC",
            "sst": "SST",
            "swdown": "SWDOWN",
            "olr": "OLR",
        }

        for dc in self.manager.data_compositions:
            arr: np.ndarray = self.manager.get_forecast_data(
                forecast_step, dc.var_name, dc.level
            )
            # Default key is from the DataType enum's nc_key
            key: str = dc.var_name.nc_key

            # Handle special cases and surface variables
            if dc.var_name == DataType.Qt:
                key = "QTOTAL_p"  # Special key for total water
            elif dc.level.is_surface():
                key = key_map.get(dc.combined_key, dc.combined_key)

            if dc.level.is_surface():
                # Ensure arr is 2D (H, W) for surface variables
                if arr.ndim > 2:
                    logger.warning(
                        f"Surface data for {key} has unexpected shape {arr.shape}. "
                        "Squeezing extra dimensions to ensure (H, W) shape."
                    )
                    arr = np.squeeze(arr)
                elif arr.ndim == 1: # Handle case where it might be (H,) or (W,)
                    logger.warning(
                        f"Surface data for {key} has unexpected shape {arr.shape}. "
                        "Attempting to reshape to (H, W)."
                    )
                    arr = arr.reshape(H, W) # Reshape to (H, W) if it's 1D
                
                data_vars[key] = (
                    ("Time", "south_north", "west_east"),
                    arr[None, ...],
                )
            else:
                # Find the index in the reversed list to place the data correctly
                level_idx: int = pressure_levels_reversed.index(dc.level)
                upper_air_cubes[dc.var_name.name][0, level_idx, :, :] = arr

        # Add all completed upper-air cubes to the data_vars.
        # If a standardization path is provided in the config, it's assumed
        # that the de-standardized Qw is in g/kg and must be converted to
        # kg/kg by dividing by 1000. Otherwise, it's assumed to be in kg/kg.
        #adjust_qw_units: bool = (
        #    self.manager.cfg.data.get("standardization_path") is not None
        #)
        for var_name, cube in upper_air_cubes.items():
            var_type: DataType = DataType[var_name]
            key = var_type.nc_key
            data_vars[key] = (
                ("Time", "pres_bottom_top", "south_north", "west_east"),
                cube / 1000 if var_name == "Qt" and not KG_PER_KG else cube,
            )

        dataset: xr.Dataset = xr.Dataset(data_vars, coords=coords)
        dataset.attrs.update(GLOBAL_ATTRIBUTES)
        dataset.attrs["FORECAST_VALID_TIME"] = forecast_time.isoformat()

        # Assign variable attributes from the metadata file
        for var_name, var_data in dataset.variables.items():
            if var_name in VARIABLE_ATTRIBUTES:
                var_data.attrs = VARIABLE_ATTRIBUTES[var_name]

        start_time_str: str = self.manager.start_time.strftime("%Y%m%d_%H%M")
        step_plus_one: int = forecast_step + 1
        filename: str = f"{self.exp_code}_{start_time_str}_F{step_plus_one:03d}.nc"
        output_path: Path = self.output_dir / filename

        encoding: Dict[str, Dict[str, Any]] = {
            var: {"zlib": True, "complevel": 4} for var in data_vars
        }
        dataset.to_netcdf(output_path, encoding=encoding)
