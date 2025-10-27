# src/op/io/rwrf_io.py
# File: src/op/io/rwrf_io.py
# Description: Handles input/output operations for RWRF-compatible NetCDF files.

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import numpy as np
import xarray as xr

# Module-level logger setup
logger = logging.getLogger(__name__)


def save_hourly_rwrf_series(
    ds6h: xr.Dataset,
    gattrs: Dict[str, str],
    outdir: str,
    bbox: Dict[str, float],
) -> None:
    """
    Interpolates a 6-hourly dataset to hourly, crops to a bounding box,
    and saves each time step as a separate RWRF-compatible NetCDF file.

    Args:
        ds6h (xr.Dataset): Dataset with 6-hourly data points.
        gattrs (Dict[str, str]): Global attributes for the output files.
        outdir (str): The output directory to save files.
        bbox (Dict[str, float]): Dictionary with keys 'lat_min', 'lat_max',
                                 'lon_min', 'lon_max' for cropping.
    """
    output_path = Path(outdir)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Preparing to save hourly RWRF series to: {outdir}")

    # Interpolate from 6-hourly to hourly data
    logger.info("Interpolating from 6-hourly to hourly resolution.")
    ds_hourly = ds6h.resample(time="1H").interpolate("linear")
    logger.info(f"Interpolation resulted in {len(ds_hourly.time)} time steps.")

    for i, time_step in enumerate(ds_hourly.time.values):
        ds_single_time = ds_hourly.sel(time=time_step)

        # Crop to the specified bounding box
        ds_cropped = _crop_bbox(ds_single_time, **bbox)

        # Define filename based on forecast hour, e.g., F000, F001, etc.
        filename = f"sfno_rwrf_F{i:03d}H.nc"
        file_path = output_path / filename

        _write_rwrf_file(
            ds=ds_cropped,
            global_attrs=gattrs,
            path=str(file_path),
        )

    logger.info("Finished writing all hourly RWRF files.")


def _crop_bbox(
    ds: xr.Dataset, lat_min: float, lat_max: float, lon_min: float, lon_max: float
) -> xr.Dataset:
    """
    Crops a dataset to a specified latitude/longitude bounding box.
    This function assumes coordinate names are 'XLAT' and 'XLONG'.

    Args:
        ds (xr.Dataset): The input dataset.
        lat_min (float): Minimum latitude.
        lat_max (float): Maximum latitude.
        lon_min (float): Minimum longitude.
        lon_max (float): Maximum longitude.

    Returns:
        xr.Dataset: The cropped dataset.
    """
    # Use where to mask data outside the bounding box
    is_within_bbox = (
        (ds["XLAT"] >= lat_min)
        & (ds["XLAT"] <= lat_max)
        & (ds["XLONG"] >= lon_min)
        & (ds["XLONG"] <= lon_max)
    )
    ds_cropped = ds.where(is_within_bbox, drop=True)
    logger.debug(
        f"Cropped dataset to bounds: LAT ({lat_min}, {lat_max}), "
        f"LON ({lon_min}, {lon_max})."
    )
    return ds_cropped


def _write_rwrf_file(
    ds: xr.Dataset, global_attrs: Dict[str, str], path: str
) -> None:
    """
    Writes a single-time-step dataset to a NetCDF file in a
    WRF-compatible format.

    Args:
        ds (xr.Dataset): The dataset for a single time step.
        global_attrs (Dict[str, str]): Global attributes for the file.
        path (str): The full path for the output file.
    """
    time_val = ds["time"].item() if ds["time"].ndim == 0 else ds["time"].values
    time_str = np.datetime_as_string(time_val, unit="s").replace("T", "_")
    times_char_array = np.array([list(time_str)], dtype="S1")

    ds_to_write = ds.copy()
    # Guarantee Time dimension for all variables
    if "Time" not in ds_to_write.dims:
        ds_to_write = ds_to_write.expand_dims(Time=[0])

    new_vars = {}
    for v in ds_to_write.data_vars:
        da = ds_to_write[v]
        if "Time" not in da.dims:
            da = da.expand_dims(Time=[0])
            desired = ["Time"]
            if "pres_bottom_top" in da.dims:
                desired += ["pres_bottom_top"]
            if "south_north" in da.dims:
                desired += ["south_north"]
            if "west_east" in da.dims:
                desired += ["west_east"]
            remaining = [d for d in da.dims if d not in desired]
            da = da.transpose(*(desired + remaining))
        new_vars[v] = da
    ds_to_write = ds_to_write.assign(**new_vars)

    ds_to_write["Times"] = (("Time", "DateStrLen"), times_char_array)
    ds_to_write.attrs.update(global_attrs)

    encoding = {}
    for var in ds_to_write.data_vars:
        if ds_to_write[var].dtype in (np.float32, np.float64):
            encoding[var] = {"dtype": "float32", "_FillValue": -9999.0}

    ds_to_write.to_netcdf(path, engine="netcdf4", format="NETCDF4", encoding=encoding)
    logger.info(f"Successfully wrote RWRF file: {path}")


