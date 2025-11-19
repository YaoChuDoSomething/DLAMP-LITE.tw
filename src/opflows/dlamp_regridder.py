import yaml # Keep import for potential future use or if other methods use it
import numpy as np
import xarray as xr
import pandas as pd
from scipy.interpolate import griddata
from src.opflows.diagnostic_registry import load_diagnostics, sort_diagnostics_by_dependencies

from datetime import datetime, timedelta
import os
from typing import Dict, Any, List # Added for type hints


class DataRegridder:
    """
    Handles regridding (spatio-temporal interpolation) of meteorological data
    and calculates diagnostic variables.

    This class takes a consolidated configuration dictionary and performs
    horizontal interpolation, vertical interpolation (if applicable, though
    not explicitly in current horizontal_interp), and diagnostic variable
    calculation based on the provided data and target grid.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the DataRegridder with a configuration dictionary.

        Args:
            config (Dict[str, Any]): A dictionary containing the configuration
                                     for regridding, including 'share', 'regrid',
                                     and 'registry' sections.
        """
        self.cfg = config

        # time control
        self.cfg_time = self.cfg["share"]["time_control"]
        self.start_t = datetime.strptime(
            self.cfg_time["start"],
            self.cfg_time["format"],
        )
        self.end_t = datetime.strptime(
            self.cfg_time["end"],
            self.cfg_time["format"],
        )
        self.a_timestep = timedelta(
            hours=self.cfg_time['base_step_hours']
        )
        self.total_steps = ((self.end_t - self.start_t) // self.a_timestep) + 1

        # I/O control (from share)
        self.cfg_io = self.cfg["share"]["io_control"]
        self.base_dir = self.cfg_io["base_dir"]
        # The grib_dir and netcdf_dir should ideally come from the downloader's output_dir
        # For now, let's keep them as they are in the config, but note for future refactoring.
        self.grib_dir = os.path.join(
            self.base_dir,
            self.cfg_io["grib_subdir"]
        )
        self.netcdf_dir = os.path.join(
            self.base_dir,
            self.cfg_io["netcdf_subdir"]
        )
        self.prefix = self.cfg_io["prefix"]
        self.pl_prefix = self.prefix["upper"]
        self.sl_prefix = self.prefix["surface"]
        self.output_prefix = self.prefix["output"] # This is for the diagnostic output file
        self.timestr_fmt = self.prefix["timestr_fmt"]
        os.makedirs(self.grib_dir, exist_ok=True) # Ensure these directories exist
        os.makedirs(self.netcdf_dir, exist_ok=True)

        # preload target grids prevent from open file repeatly
        self.regrid = self.cfg["regrid"]
        self.target_nc = self.regrid["target_nc"]
        self.tgtlon = self.regrid["target_lon"]
        self.tgtlat = self.regrid["target_lat"]
        self.tgtpres = self.regrid["target_pres"]
        self.srclon = self.regrid["source_lon"]
        self.srclat = self.regrid["source_lat"]
        self.srcpres = self.regrid["source_pres"]
        self.pres_levels = self.regrid["levels"]
        self.adopted_varlist = self.regrid["adopted_varlist"]
        self.write_regrid = self.regrid["write_regrid"]
        with xr.open_dataset(self.target_nc, engine="netcdf4") as tgtds:
            self.XLONG = tgtds[self.tgtlon].values
            self.XLAT = tgtds[self.tgtlat].values
            self.static = tgtds[self.adopted_varlist]

        # diagnostics module
        # Pass the registry config dictionary directly
        self.diagnostics, self.source_dataset = load_diagnostics(self.cfg["registry"])

    # Removed _load_config method
    # def _load_config(self, yaml_path):
    #     with open(yaml_path, mode="r") as f:
    #         return yaml.safe_load(f)

    def build_timeline(self) -> List[datetime]: # Added type hint
        """
        Generates a list of datetime objects representing the timeline for processing.

        Returns:
            List[datetime]: A list of datetime objects.
        """
        return [
            self.start_t + t * self.a_timestep
            for t in range(self.total_steps)
        ]

    def gen_io_filename(self, curr_time: datetime) -> List[str]: # Added type hint
        """
        Generates input and output filenames based on the current time.

        Args:
            curr_time (datetime): The current datetime for file naming.

        Returns:
            List[str]: A list containing paths to pl_nc, sl_nc, and output_nc.
        """
        timestamp = curr_time.strftime(self.timestr_fmt)
        pl_nc = f"{self.netcdf_dir}/{self.pl_prefix}_{timestamp}.nc"
        sl_nc = f"{self.netcdf_dir}/{self.sl_prefix}_{timestamp}.nc"
        output_nc = f"{self.netcdf_dir}/{self.output_prefix}_{timestamp}.nc"
        return [pl_nc, sl_nc, output_nc]

    def _interpolate_with_fallback(self, points: np.ndarray, values: np.ndarray, xi: tuple) -> np.ndarray: # Added type hints
        """
        Perform linear interpolation with a nearest-neighbor fallback for NaN values.

        Parameters
        ----------
        points : np.ndarray
            Coordinates of the source data points.
        values : np.ndarray
            Values of the source data points.
        xi : tuple
            Coordinates of the target grid.

        Returns
        -------
        np.ndarray
            Interpolated grid.
        """
        # First, try linear interpolation
        grid_linear = griddata(points, values, xi, method="linear")

        # Check if any NaNs were produced
        nan_mask = np.isnan(grid_linear)

        # If there are NaNs, use nearest neighbor to fill them
        if np.any(nan_mask):
            # Perform nearest interpolation
            grid_nearest = griddata(points, values, xi, method="nearest")
            # Fill in the NaNs from the linear result with values from the nearest result
            grid_linear[nan_mask] = grid_nearest[nan_mask]

        return grid_linear

    def interp_horizontal_v2(self, out_dict: Dict[str, Any], curr_time: datetime, src_nc: str) -> Dict[str, Any]: # Added type hints
        """
        Interpolates data from a source grid to a target grid horizontally.
        Fills NaN values resulting from linear interpolation using the 'nearest' method.

        target_lat: "XLAT"
        target_lon: "XLONG"
        target_pres: "pres_levels"
        source_lat: "lat"
        source_lon: "lon"
        source_pres: "plev"

        Parameters
        ----------
        out_dict : Dict[str, Any]
            Dictionary to store the output interpolated data.
        curr_time : datetime
            Current time step being processed.
        src_nc : str
            Path to the source NetCDF file.

        Returns
        -------
        Dict[str, Any]
            The updated dictionary with interpolated data.
        """
        dim_upp = ["Time", "pres_bottom_top", "south_north", "west_east"]
        dim_sfc = ["Time", "south_north", "west_east"]

        with xr.open_dataset(src_nc, engine="netcdf4") as ncds:
            lon = ncds[self.srclon].values
            lat = ncds[self.srclat].values
            if np.ndim(lon) == 1 and np.ndim(lat) == 1:
                lons, lats = np.meshgrid(lon, lat)
            else:
                lons, lats = lon, lat

            # Prepare source points for griddata
            points = np.vstack((lons.ravel(), lats.ravel())).T
            # Prepare target points
            xi = (self.XLONG.ravel(), self.XLAT.ravel())
            # Changed to get shape from self.XLONG for consistency
            ny, nx = self.XLONG.shape 

            for var in ncds.keys():
                # Skip coordinate variables if they appear in the keys
                if var in [self.srclon, self.srclat, 'plev', 'time']:
                    continue

                data = np.squeeze(ncds[var].values)
                print(f"[REGRID] {var} => {data.shape}")

                if data.ndim == 3:
                    nl = data.shape[0]
                    data_h = np.empty((nl, ny, nx))
                    for pl in range(nl):
                        # Use the new interpolation function with fallback
                        interp_data = self._interpolate_with_fallback(
                            points, data[pl].ravel(), xi
                        )
                        data_h[pl] = np.reshape(interp_data, (ny, nx))

                    data_h = np.expand_dims(data_h, axis=0)
                    out_dict[var] = (dim_upp, data_h.astype(np.float32))

                elif data.ndim == 2:
                    # Use the new interpolation function with fallback
                    interp_data = self._interpolate_with_fallback(
                        points, data.ravel(), xi
                    )
                    data_h = np.reshape(interp_data, (ny, nx))
                    data_h = np.expand_dims(data_h, axis=0)

                    out_dict[var] = (dim_sfc, data_h.astype(np.float32))

        return out_dict

    def interp_horizontal(self, out_dict: Dict[str, Any], curr_time: datetime, src_nc: str) -> Dict[str, Any]: # Added type hints
        """
        Horizontal interpolation method (original, without fallback)
        """
        dim_upp = ["Time", "pres_bottom_top", "south_north", "west_east"]
        dim_sfc = ["Time", "south_north", "west_east"]

        with xr.open_dataset(src_nc, engine="netcdf4") as ncds:
            lon = ncds[self.srclon].values
            lat = ncds[self.srclat].values
            if np.ndim(lon) == 1 and np.ndim(lat) == 1:
                lons, lats = np.meshgrid(lon, lat)
            else:
                lons, lats = lon, lat

            points = list(zip(lons.ravel(), lats.ravel()))
            xi = (self.XLONG, self.XLAT)
            # Changed to get shape from self.XLONG for consistency
            ny, nx = self.XLONG.shape 

            for var in ncds.keys():
                data = np.squeeze(ncds[var].values)
                print(f"[REGRID] {var} => {data.shape}")
                if data.ndim == 3:
                    nl = data.shape[0]
                    data_h = np.empty((nl, ny, nx))
                    for pl in range(nl):
                        data_h[pl] = griddata(
                            points, data[pl].ravel(),
                            xi, method="linear"
                        )
                    data_h = np.expand_dims(data_h, axis=0)

                    out_dict[var] = (dim_upp, data_h.astype(np.float32))

                elif data.ndim == 2:
                    data_h = griddata(
                        points, data.ravel(), xi, method="linear"
                    )
                    data_h = np.expand_dims(np.reshape(data_h, (ny,nx)), axis=0)

                    out_dict[var] = (dim_sfc, data_h.astype(np.float32))

        return out_dict


    def process_single_time(self, curr_time: datetime) -> None: # Added type hint
        """
        Processes a single timestep by performing horizontal interpolation and
        calculating diagnostic variables.

        Args:
            curr_time (datetime): The current datetime to process.
        """
        print(f"[INFO] Processing single time: {curr_time}")
        [pl_nc, sl_nc, output_nc] = self.gen_io_filename(curr_time)

        out_dict = {}
        out2_dict = {}
        for var in self.static.data_vars: # Iterate over data_vars, not the Dataset itself
            static_data = self.static[var].values
            out_dict[var] = (self.static[var].dims, static_data) # Use original dimensions
            out2_dict[var] = (self.static[var].dims, static_data, self.static[var].attrs)

        # Ensure NetCDF files exist, otherwise skip this timestep
        if not os.path.exists(pl_nc) and not os.path.exists(sl_nc):
            print(f"[WARN] Missing NetCDF files for {curr_time}. Skipping regridding for this timestep.")
            return

        out_coords={
            "Time": ("Time", [np.datetime64(curr_time)]),
            "pres_bottom_top": ("pres_bottom_top", range(len(self.pres_levels))),
            "south_north": ("south_north", range(self.XLAT.shape[0])), # Use XLAT shape for ny
            "west_east": ("west_east", range(self.XLAT.shape[1])), # Use XLAT shape for nx
        }
        out2_coords = out_coords
        out_attrs={
            "title": f"Interpolated dataset at {curr_time}"
        }
        out2_attrs={
            "title": f"Diagnosed and interpolated dataset at {curr_time}"
        }


        # Horizontally interpolate pressure level data
        if os.path.exists(pl_nc):
            print("[REGRID]: ", pl_nc)
            self.interp_horizontal(out_dict, curr_time, pl_nc)

        # Horizontally interpolate surface level data
        if os.path.exists(sl_nc):
            print("[REGRID]: ", sl_nc)
            self.interp_horizontal(out_dict, curr_time, sl_nc)

        outds = xr.Dataset(
            data_vars = out_dict, coords = out_coords, attrs = out_attrs
        )
        out2ds = xr.Dataset(
            data_vars = out2_dict, coords = out2_coords, attrs = out2_attrs
        )
        # Assuming regrid_nc is handled via a configuration now
        regrid_output_dir = self.cfg["regrid"].get("regrid_output_dir", self.netcdf_dir) # New config for regrid output
        regrid_output_prefix = self.cfg["regrid"].get("regrid_output_prefix", "regrid_") # New config for regrid prefix
        regrid_output_filename = os.path.join(
            regrid_output_dir,
            f"{regrid_output_prefix}{curr_time.strftime(self.timestr_fmt)}.nc"
        )


        if self.write_regrid:
            outds.to_netcdf(regrid_output_filename, format="NETCDF4")
            print(f"[DONE] Saved interpolated NetCDF for {curr_time} to {regrid_output_filename}")
        else:
            print(f"[DONE] interpolated NetCDF for {curr_time} without saving the data")

        # --- Diagnostic variable calculation and output ---
        ordered_vars = sort_diagnostics_by_dependencies(self.diagnostics)

        for var in ordered_vars:
            if var not in self.diagnostics:
                continue

            info = self.diagnostics[var]
            requires = info["requires"]
            diag_func = info["function"]

            if all(req in outds.data_vars or req in outds.coords for req in requires):
                print(f"[DIAGNOSE] Calculating diagnostic: {var}")
                try:
                    diagnostic_dataarray = diag_func(self.source_dataset, outds)
                    out2ds[var] = diagnostic_dataarray
                    print(f"[DIAGNOSE] Calculated {var}, shape: {out2ds[var].shape}, mean: {out2ds[var].values.mean():.4f}")

                except Exception as e:
                     print(f"[ERROR] Failed to calculate diagnostic {var}: {e}")
                     import traceback
                     traceback.print_exc()
            else:
                missing = [req for req in requires if req not in outds.data_vars and req not in outds.coords]
                print(f"[WARN] Missing required inputs for diagnostic {var}: {missing}. Skipping calculation for this variable.")

        # Save once outside the loop
        diagnostic_output_dir = self.cfg["regrid"].get("diagnostic_output_dir", self.netcdf_dir) # New config for diagnostic output dir
        output_nc_final = os.path.join(
            diagnostic_output_dir, # Use the new config
            f"{self.output_prefix}_{curr_time.strftime(self.timestr_fmt)}.nc" # output_prefix is for diagnostic
        )
        os.makedirs(diagnostic_output_dir, exist_ok=True) # Ensure output dir exists

        out2ds.to_netcdf(output_nc_final, format="NETCDF4")
        print(f"[DONE] Saved diagnostic NetCDF for {curr_time} to {output_nc_final}")

    def main_process(self) -> None: # Added type hint
        """
        Executes the main regridding and diagnostic processing loop for all timesteps.
        """
        for curr_time in self.build_timeline():
            self.process_single_time(curr_time)
