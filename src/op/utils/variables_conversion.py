# src/op/utils/
# File: src/op/utils/variables_conversion.py
# Description: This module transforms variables from the model's native format
#              to the RWRF-compatible format.

import logging
from typing import Any, Dict, List

import xarray as xr

# Module-level logger setup
logger = logging.getLogger(__name__)


def transform_to_rwrf(
    regridded_da: xr.DataArray,
    model_config: Dict[str, Any],
    gfs_config: Dict[str, Any],
) -> xr.Dataset:
    """
    Transforms a 73-channel SFNO DataArray into an RWRF-compatible Dataset.

    This function performs:
    1.  Variable renaming based on the registry mapping.
    2.  Unit conversions (e.g., geopotential to geopotential height).
    3.  Restructuring of pressure-level data.

    Args:
        regridded_da (xr.DataArray): The input regridded DataArray.
        model_config (Dict[str, Any]): The SFNO model configuration,
                                       containing pressure level information.
        gfs_config (Dict[str, Any]): The GFS data source configuration,
                                     containing variable mappings.

    Returns:
        xr.Dataset: The transformed dataset ready for RWRF processing.
    """
    logger.info("Starting transformation to RWRF dataset format.")
    rwrf_vars = {}
    mappings: Dict[str, str] = gfs_config["registry"]["mappings"]
    pressure_levels: List[int] = model_config["model"]["pressure_levels"]

    # Process 2D surface variables
    for sfno_var in model_config["model"]["variable_2d"]:
        if sfno_var in mappings:
            rwrf_name = mappings[sfno_var]
            rwrf_vars[rwrf_name] = regridded_da.sel(variable=sfno_var).drop_vars(
                "variable"
            )
            logger.debug(f"Mapped SFNO '{sfno_var}' to RWRF '{rwrf_name}'.")

    # Process 3D pressure-level variables
    for prefix_3d in model_config["model"]["variable_3d"]:
        sfno_var_names = [f"{prefix_3d}{p}" for p in pressure_levels]
        data_subset = regridded_da.sel(variable=sfno_var_names)

        # Apply specific unit conversions
        if prefix_3d == "z":  # Geopotential to Geopotential Height
            data_subset = data_subset / 9.80665
            data_subset.attrs["units"] = "m"
        elif prefix_3d == "q":  # Specific Humidity to Mixing Ratio
            data_subset = data_subset / (1.0 - data_subset)
            data_subset.attrs["units"] = "kg kg-1"

        # Reshape and assign coordinates
        data_subset = data_subset.rename({"variable": "pressure"}).assign_coords(
            pressure=pressure_levels
        )

        rwrf_name = mappings[prefix_3d]
        rwrf_vars[rwrf_name] = data_subset
        logger.debug(f"Processed 3D var '{prefix_3d}' into RWRF '{rwrf_name}'.")

    rwrf_ds = xr.Dataset(rwrf_vars)
    logger.info("Transformation to RWRF dataset complete.")
    return rwrf_ds


