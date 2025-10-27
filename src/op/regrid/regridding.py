# src/op/regrid/regridding.py
# File: src/op/regrid/regridding.py
# Description: This module handles regridding operations.

import logging

import numpy as np
import xarray as xr
from scipy.interpolate import griddata

# Module-level logger setup
logger = logging.getLogger(__name__)


def to_rwrf_grid(sfno_da: xr.DataArray, target_grid_path: str) -> xr.DataArray:
    """
    Regrids a DataArray from a global lat-lon grid to a specified RWRF grid.

    Uses bilinear interpolation with a nearest-neighbor fill for any NaN values
    that may result at the boundaries.

    Args:
        sfno_da (xr.DataArray): The input DataArray with dimensions
                                ('variable', 'lat', 'lon').
        target_grid_path (str): Path to the target RWRF grid file, which
                                must contain 'XLAT' and 'XLONG' variables.

    Returns:
        xr.DataArray: A new DataArray regridded to the target grid with
                      dimensions ('variable', 'south_north', 'west_east').

    Raises:
        FileNotFoundError: If the target grid file does not exist.
        KeyError: If 'XLAT' or 'XLONG' are missing from the target grid file.
        ValueError: If the input DataArray lacks 'lat' or 'lon' dimensions.
    """
    if "lat" not in sfno_da.dims or "lon" not in sfno_da.dims:
        raise ValueError("Input DataArray must have 'lat' and 'lon' dimensions.")



    logger.info(f"Starting regridding process to target grid: {target_grid_path}")

    # Load target grid coordinates
    try:
        with xr.open_dataset(target_grid_path, engine="h5netcdf") as target_ds:
            target_lat = target_ds["XLAT"].values
            target_lon = target_ds["XLONG"].values
    except FileNotFoundError:
        logger.error(f"Target grid file not found at: {target_grid_path}")
        raise
    except KeyError:
        logger.error("Target grid must contain 'XLAT' and 'XLONG' variables.")
        raise

    # Prepare source grid points for interpolation
    source_lat_grid, source_lon_grid = np.meshgrid(
        sfno_da["lat"].values, sfno_da["lon"].values, indexing="ij"
    )
    source_points = np.vstack(
        (source_lat_grid.ravel(), source_lon_grid.ravel())
    ).T

    # Prepare target grid points
    target_points = np.vstack((target_lat.ravel(), target_lon.ravel())).T

    regridded_vars = []
    # Iterate over each variable in the input DataArray # Using tqdm to display the 
    for var_name in sfno_da["variable"].values:
        logger.info(f"Regridding variable: {var_name}")
        source_data = sfno_da.sel(variable=var_name).values.ravel()

        # Perform bilinear interpolation
        interpolated_data = griddata(
            source_points, source_data, target_points, method="linear"
        )

        # Fill any remaining NaNs with nearest-neighbor interpolation
        #nan_mask = np.isnan(interpolated_data)
        #if np.any(nan_mask):
        #    logger.debug(f"Found {np.sum(nan_mask)} NaN points. Filling them.")
        #    nearest_fill = griddata(
        #        source_points, source_data, target_points[nan_mask], method="nearest"
        #    )
        #    interpolated_data[nan_mask] = nearest_fill

        regridded_vars.append(interpolated_data.reshape(target_lat.shape))
        regridded_vars.append(target_lat.reshape(target_lon.shape))
        regridded_vars.append(target_lon.reshape(target_lat.shape))

    # Construct the final regridded DataArray
    regridded_da = xr.DataArray(
        coords={
            "variable": sfno_da["variable"].values,
            "south_north": np.arange(target_lat.shape[0]),
            "west_east": np.arange(target_lat.shape[1]),
        },
    )

    for i, var_name in enumerate(sfno_da["variable"].values):
        regridded_da.loc[dict(variable=var_name)]
        data_vars={ var_name: (("time", "south_north", "west_east"), regridded_vars[i*3]),
        }
        regridded_da = regridded_da.assign_coords(
        {   
            "XLAT": (("time", "south_north", "west_east"), target_lat),
            "XLONG": (("time", "south_north", "west_east"), target_lon),
        },
    )
    logger.info("Regridding complete.")
    return regridded_da



