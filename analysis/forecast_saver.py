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
from typing import Any, Dict

import numpy as np
import xarray as xr

from analysis.data_manager import AnalysisDataManager
from analysis.netcdf_meta import GLOBAL_ATTRIBUTES, VARIABLE_ATTRIBUTES
from src.utils.data_type import DataType, Level

logger = logging.getLogger(__name__)


class ForecastSaver:
    """Serializes forecast results into WRF-style NetCDF files.

    Attributes:
        manager (AnalysisDataManager): The data manager instance.
        output_dir (Path): Directory where NetCDF files will be saved.
    """

    def __init__(self, manager: AnalysisDataManager, output_dir: Path):
        """Initializes the ForecastSaver.

        Args:
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): The target directory for saving files.
        """
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_all_forecasts(self) -> None:
        """Saves all forecast steps (F001H onwards) to NetCDF files."""
        num_steps: int = self.manager.results["output_upper"].shape[1]
        logger.info("Saving %d forecast steps to NetCDF.", num_steps)

        for step in range(num_steps):
            self._save_single_step(step)

        logger.info("Saved all forecast steps to %s", self.output_dir)

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

        pres_levels_val: np.ndarray = np.array(
            [float(lv.nc_key) for lv in self.manager.pressure_levels],
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
            "umet10": "U10",
            "vmet10": "V10",
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
            if dc.var_name == DataType.Qw:
                key = "QWATER_p"  # Special key for total water
            elif dc.level.is_surface():
                key = key_map.get(dc.combined_key, dc.combined_key)

            if dc.level.is_surface():
                data_vars[key] = (
                    ("Time", "south_north", "west_east"),
                    arr[None, ...],
                )
            else:
                level_idx: int = self.manager.pressure_levels.index(dc.level)
                upper_air_cubes[dc.var_name.name][0, level_idx, :, :] = arr

        # Add all completed upper-air cubes to the data_vars
        for var_name, cube in upper_air_cubes.items():
            var_type: DataType = DataType[var_name]
            key = "QWATER_p" if var_name == "Qw" else var_type.nc_key
            data_vars[key] = (
                ("Time", "pres_bottom_top", "south_north", "west_east"),
                cube,
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
        filename: str = f"dlamp_{start_time_str}_F{step_plus_one:03d}.nc"
        output_path: Path = self.output_dir / filename

        encoding: Dict[str, Dict[str, Any]] = {
            var: {"zlib": True, "complevel": 4} for var in data_vars
        }
        dataset.to_netcdf(output_path, encoding=encoding)
