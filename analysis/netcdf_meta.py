# analysis/netcdf_meta.py
"""Metadata for creating WRF-compatible NetCDF files.

This module provides dictionaries containing attributes (like units and
descriptions) for variables and global properties of the NetCDF files,
ensuring consistency with WRF output standards.
"""
from typing import Any, Dict

# Global attributes to be written to the NetCDF file
# A subset of common WRF attributes for reproducibility
GLOBAL_ATTRIBUTES: Dict[str, Any] = {
    "TITLE": "DLAMP AI MODEL OUTPUT",
    "MAP_PROJ_CHAR": "Lambert Conformal",
    "MMINLU": "MODIFIED_IGBP_MODIS_NOAH",
    "SIMULATION_INITIALIZATION_TYPE": "REAL-DATA CASE",
    "GRIDTYPE": "C",
}

# Variable-specific attributes (units, description, etc.)
VARIABLE_ATTRIBUTES: Dict[str, Any] = {
    "Times": {"description": "model time"},
    "XLAT": {
        "description": "LATITUDE, SOUTH IS NEGATIVE",
        "units": "degree_north",
        "coordinates": "west_east south_north Time"
    },
    "XLONG": {
        "description": "LONGITUDE, WEST IS NEGATIVE",
        "units": "degree_east",
        "coordinates": "west_east south_north Time"
    },
    "pres_levels": {"description": "Pressure Levels", "units": "hPa"},
    "HGT": {
        "description": "Terrain Height",
        "units": "m",
        "coordinates": "west_east south_north Time"
    },
    "LANDMASK": {
        "description": "Land Sea mask (1=land and 0=sea)",
        "units": "1",
        "coordinates": "west_east south_north Time",
    },
    "z_p": {
        "description": "Geopotential Height",
        "units": "m",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "tk_p": {
        "description": "Temperature",
        "units": "K",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "umet_p": {
        "description": "U-component of wind",
        "units": "m s-1",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "vmet_p": {
        "description": "V-component of wind",
        "units": "m s-1",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "wa_p": {
        "description": "W-component of Wind on Mass Points",
        "units": "m s-1",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "QVAPOR_p": {
        "description": "Water vapor mixing ratio",
        "units": "kg kg-1",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "QWATER_p": {
        "description": "Total water mixing ratio (cloud+rain+ice+snow+graupel)",
        "units": "kg kg-1",
        "coordinates": "XLONG XLAT pres_levels",
    },
    "PSFC": {
        "description": "SFC PRESSURE",
        "units": "Pa",
        "coordinates": "XLONG XLAT",
    },
    "SST": {
        "description": "SEA SURFACE TEMPERATURE",
        "units": "K",
        "coordinates": "XLONG XLAT",
    },
    "SWDOWN": {
        "description": "DOWNWARD SHORT WAVE FLUX AT GROUND SURFACE",
        "units": "W m-2",
        "coordinates": "XLONG XLAT",
    },
    "OLR": {
        "description": "TOA OUTGOING LONG WAVE",
        "units": "W m-2",
        "coordinates": "XLONG XLAT",
    },
    "T2": {
        "description": "TEMP at 2 M",
        "units": "K",
        "coordinates": "XLONG XLAT",
    },
    "Q2": {
        "description": "Water vapor mixing ratio at 2 M",
        "units": "kg kg-1",
        "coordinates": "XLONG XLAT",
    },
    "umet10": {
        "description": "U at 10 M",
        "units": "m s-1",
        "coordinates": "XLONG XLAT",
    },
    "vmet10": {
        "description": "V at 10 M",
        "units": "m s-1",
        "coordinates": "XLONG XLAT",
    },
}
