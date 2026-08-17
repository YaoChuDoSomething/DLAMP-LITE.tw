"""Constants and variable definitions for FCN-RegPGW modeling.

Defines atmospheric variable orderings, standard pressure levels, grid
dimensions for global and regional domains, boundary buffers, and color maps.
"""

from collections.abc import Sequence
from typing import Final

# Standard 13 pressure levels in hPa
PRESSURE_LEVELS: Final[Sequence[int]] = (
    50,
    100,
    150,
    200,
    250,
    300,
    400,
    500,
    600,
    700,
    850,
    925,
    1000,
)

# Surface variables (8 channels)
SURFACE_VARIABLES: Final[Sequence[str]] = (
    "10u",
    "10v",
    "100u",
    "100v",
    "2t",
    "sp",
    "msl",
    "tcwv",
)

# Upper-air variable prefixes
UPPER_AIR_PREFIXES: Final[Sequence[str]] = ("u", "v", "z", "t", "r")


def build_variable_list() -> list[str]:
    """Build the standard 73 atmospheric variable ordering list.

    Returns:
        List[str]: Complete list of 73 standard atmospheric variable names.
    """
    vars_list: list[str] = list(SURFACE_VARIABLES)
    for prefix in UPPER_AIR_PREFIXES:
        for level in PRESSURE_LEVELS:
            vars_list.append(f"{prefix}{level}")
    return vars_list


VARIABLES_73: Final[Sequence[str]] = tuple(build_variable_list())

# Channel index slices for quick access
SLICE_SURFACE: Final[slice] = slice(0, 8)
SLICE_U: Final[slice] = slice(8, 21)
SLICE_V: Final[slice] = slice(21, 34)
SLICE_Z: Final[slice] = slice(34, 47)
SLICE_T: Final[slice] = slice(47, 60)
SLICE_R: Final[slice] = slice(60, 73)
SLICE_Q: Final[slice] = slice(60, 73)

# 850 hPa wind indices
INDEX_U850: Final[int] = 18
INDEX_V850: Final[int] = 31

# Standard global grid shape (0.25 deg)
DEFAULT_GLOBAL_LAT_SIZE: Final[int] = 720
DEFAULT_GLOBAL_LON_SIZE: Final[int] = 1440
DEFAULT_LAT_SIZE: Final[int] = 720
DEFAULT_LON_SIZE: Final[int] = 1440

# Regional RegPGW Domain (Default: East Asia / Western Pacific / Taiwan)
# Global indices: lat 200..440 (~40N to ~20S or ~40N to ~10N), lon 400..640 (~100E to ~160E)
DEFAULT_REGIONAL_BOUNDS: Final[tuple[int, int, int, int]] = (200, 440, 400, 640)
DEFAULT_REGIONAL_LAT_SIZE: Final[int] = 240
DEFAULT_REGIONAL_LON_SIZE: Final[int] = 240
DEFAULT_BOUNDARY_WIDTH: Final[int] = 12

# Static channels
STATIC_CHANNELS: Final[Sequence[str]] = (
    "sin_lat",
    "cos_lat",
    "sin_lon",
    "cos_lon",
    "orography",
    "land_sea_mask",
)
NUM_STATIC_CHANNELS: Final[int] = len(STATIC_CHANNELS)
NUM_SOLAR_CHANNELS: Final[int] = 3
NUM_INTERP_INPUT_CHANNELS: Final[int] = 155  # 73 + 73 + 3 + 6

# RegPGW input channels: 73 (current regional) + 73 (boundary forcing) + 6 (static) = 152
NUM_REGPGW_INPUT_CHANNELS: Final[int] = 152
NUM_REGPGW_OUTPUT_CHANNELS: Final[int] = 73

# Windspeed visualization levels and colors
WIND_SPEED_LEVELS: Final[Sequence[float]] = (
    0,
    4,
    6,
    8,
    10,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    34,
    36,
    38,
    40,
    43,
    46,
    49,
    52,
    55,
    58,
    61,
    64,
    67,
    70,
    73,
    76,
    79,
    82,
    85,
)

WIND_SPEED_COLORS: Final[Sequence[str]] = (
    "#ffffff",
    "#80ffff",
    "#6fedf1",
    "#5fdde4",
    "#50cdd5",
    "#40bbc7",
    "#2facba",
    "#1f9bac",
    "#108c9f",
    "#007a92",
    "#00b432",
    "#33c341",
    "#67d251",
    "#99e060",
    "#cbf06f",
    "#ffff80",
    "#ffdd52",
    "#ffdc52",
    "#ffa63e",
    "#ff6d29",
    "#ff3713",
    "#ff0000",
    "#d70000",
    "#af0000",
    "#870000",
    "#5f0000",
    "#aa00ff",
    "#b722fe",
    "#c446ff",
    "#d46aff",
    "#e38dff",
    "#f1b1ff",
    "#ffd3ff",
    "#ffc6ea",
    "#ffb6d5",
    "#ffa6c1",
    "#ff97ac",
    "#ff8798",
    "#fe7884",
    "#ff696e",
    "#ff595a",
    "#e74954",
    "#cc3a4c",
    "#b22846",
    "#9a1941",
)
