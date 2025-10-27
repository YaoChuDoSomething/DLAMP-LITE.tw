# src/op/diag/diagnostics.py
# File: src/op/diag/diagnostics.py
# Description: This module computes diagnostic variables for RWRF outputs.

import logging

import xarray as xr

# Module-level logger setup
logger = logging.getLogger(__name__)


def run_diagnostics(ds: xr.Dataset, diag_set: str) -> None:
    """
    Run diagnostics based on a specified set (e.g., 'rwrf_default').

    Computes and attaches diagnostic variables to the dataset in-place.

    Args:
        ds (xr.Dataset): The input RWRF dataset to process.
        diag_set (str): The name of the diagnostic set to apply.

    Raises:
        ValueError: If the specified diagnostic set is not supported.
    """
    if diag_set != "rwrf_default":
        logger.warning(f"Unsupported diagnostic set: {diag_set}. Skipping.")
        return

    logger.info("Running diagnostics for the '%s' set.", diag_set)

    # Example Diagnostic: Compute 10m Wind Speed from U10 and V10
    if "U10" in ds and "V10" in ds:
        wind_speed_10m = (ds["U10"] ** 2 + ds["V10"] ** 2) ** 0.5
        ds["WSPD10"] = wind_speed_10m.assign_attrs(
            units="m s-1",
            long_name="10-meter Wind Speed",
            description="Computed from U10 and V10 components.",
        )
        logger.info("Computed 10m Wind Speed (WSPD10).")

    logger.info("Diagnostics execution complete.")


