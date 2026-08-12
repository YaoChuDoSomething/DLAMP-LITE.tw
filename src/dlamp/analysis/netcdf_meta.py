# analysis/netcdf_meta.py
"""Metadata for creating WRF-compatible NetCDF files.

This module provides dictionaries containing attributes (like units and
descriptions) for variables and global properties of the NetCDF files,
ensuring consistency with WRF output standards.
"""
from typing import Any

# Global attributes to be written to the NetCDF file
# A subset of common WRF attributes for reproducibility
GLOBAL_ATTRIBUTES: dict[str, Any] = {
    "TITLE": "DLAMP AI MODEL OUTPUT",
    "MAP_PROJ_CHAR": "Lambert Conformal",
    "MMINLU": "MODIFIED_IGBP_MODIS_NOAH",
    "SIMULATION_INITIALIZATION_TYPE": "REAL-DATA CASE",
    "GRIDTYPE": "A",
}

# Variable-specific attributes (units, description, etc.)
VARIABLE_ATTRIBUTES: dict[str, Any] = {
    "Times": {
        "description": "model time"
    },
    "XLAT": {
        "description": "Latitude, South is Negative",
        "units": "degree_north",
    },
    "XLONG": {
        "description": "Longitude, West is Negative",
        "units": "degree_east",
    },
    "pres_levels": {
        "description": "Constant Pressure Levels", 
        "units": "hPa"
    },
    "HGT": {
        "description": "Terrain Height",
        "units": "m",
    },
    "LANDMASK": {
        "description": "Land Sea Mask (1=Land and 0=Sea)",
        "units": "1",
    },
    "z_p": {
        "description": "Geopotential Height",
        "units": "m",
    },
    "tk_p": {
        "description": "Air Temperature",
        "units": "K",
    },
    "umet_p": {
        "description": "U-component of Wind Rotated to Earth Coordinates",
        "units": "m s-1",
    },
    "vmet_p": {
        "description": "V-component of Wind Rotated to Earth Coordinates",
        "units": "m s-1",
    },
    "wa_p": {
        "description": "Vertical Velocity",
        "units": "m s-1",
    },
    "QVAPOR_p": {
        "description": "Water Vapor Mixing Ratio",
        "units": "kg kg-1",
    },
    "QWATER_p": {
        "description": "Total Hydrometeors Mixing Ratio (cloud+rain+ice+snow+graupel)",
        "units": "kg kg-1",
    },
    "PSFC": {
        "description": "Surface Pressure",
        "units": "Pa",
    },
    "SLP": {
        "description": "Sea-Level Pressure",
        "units": "hPa",
    },
    "SST": {
        "description": "Sea Surface Temperature",
        "units": "K",
    },
    "RAINNC": {
        "description": "Accumulated Grid Scale Precipitation",
        "units": "mm",
    },
    "PBLH": {
        "description": "Planetary Boundary Layer Height",
        "units": "m",
    },
    "pw": {
        "description": "Precipitable Water",
        "units": "kg m-2",
    },
    "SWDOWN": {
        "description": "Downward Shortwave Radiation Flux at Ground Surface",
        "units": "W m-2",
    },
    "OLR": {
        "description": "Outgoing Longwave Radiation Flux at Top of Atmosphere(TOA)",
        "units": "W m-2",
    },
    "T2": {
        "description": "Air Temperature at 2 Meters Height ",
        "units": "K",
    },
    "Q2": {
        "description": "Water Vapor Mixing Ratio at 2 Meters Height",
        "units": "kg kg-1",
    },
    "umet10": {
        "description": "U-component of Wind Rotated to Earth Coordinates at 10 Meters Height",
        "units": "m s-1",
    },
    "vmet10": {
        "description": "V-component of Wind Rotated to Earth Coordinates at 10 Meters Height",
        "units": "m s-1",
    },
}
