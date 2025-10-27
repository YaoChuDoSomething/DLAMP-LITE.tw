# src/op/utils/time_interp.py
# File: src/op/utils/time_interp.py
# Description: This module provides time interpolation utilities.

import logging

import xarray as xr

# Module-level logger setup
logger = logging.getLogger(__name__)


def to_hourly_linear(ds: xr.Dataset) -> xr.Dataset:
    """
    Performs linear interpolation on a dataset from 6-hourly to hourly frequency.

    Args:
        ds (xr.Dataset): An xarray Dataset with a 'time' coordinate, containing
                         data at 6-hour intervals.

    Returns:
        xr.Dataset: A new xarray Dataset with data interpolated to a 1-hour
                    frequency.
    """
    logger.info("Interpolating time series from 6-hourly to hourly resolution.")
    if "time" not in ds.coords:
        raise ValueError("Dataset must have a 'time' coordinate for interpolation.")

    hourly_ds = ds.resample(time="1H").interpolate("linear")
    logger.info("Time interpolation successful.")
    return hourly_ds
