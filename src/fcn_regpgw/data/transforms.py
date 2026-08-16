"""Atmospheric and spatial coordinate transformations for FCN-RegPGW.

Provides degree-to-radian trigonometric grid generation, latitude flips,
bidirectional specific humidity <-> relative humidity conversions, and
solar zenith angle computation.
"""

import math
from collections.abc import Sequence
from datetime import UTC, datetime

import numpy as np

from fcn_regpgw.const import (
    DEFAULT_LAT_SIZE,
    DEFAULT_LON_SIZE,
    PRESSURE_LEVELS,
)


def generate_sincos_grid(
    lat_size: int = DEFAULT_LAT_SIZE,
    lon_size: int = DEFAULT_LON_SIZE,
) -> np.ndarray:
    """Generate 4-channel sin/cos latitude and longitude static feature grid.

    Correctly applies degree-to-radian conversion before computing sine
    and cosine values.

    Args:
        lat_size (int): Number of latitude grid points.
        lon_size (int): Number of longitude grid points.

    Returns:
        np.ndarray: Array of shape (4, lat_size, lon_size) with
            [sin(lat), cos(lat), sin(lon), cos(lon)].
    """
    lat = np.linspace(90.0, -90.0, lat_size, endpoint=False, dtype=np.float32)
    lon = np.linspace(0.0, 360.0, lon_size, endpoint=False, dtype=np.float32)

    grid_y, grid_x = np.meshgrid(lat, lon, indexing="ij")

    # Apply deg2rad conversion
    grid_y_rad = np.deg2rad(grid_y)
    grid_x_rad = np.deg2rad(grid_x)

    sincos = np.stack(
        [
            np.sin(grid_y_rad),
            np.cos(grid_y_rad),
            np.sin(grid_x_rad),
            np.cos(grid_x_rad),
        ],
        axis=0,
    ).astype(np.float32)

    return sincos


def flip_latitude(
    data: np.ndarray,
    lat_axis: int = 1,
) -> np.ndarray:
    """Flip the latitude dimension of an atmospheric tensor.

    Args:
        data (np.ndarray): Multi-dimensional input array.
        lat_axis (int): Axis index corresponding to the latitude dimension.

    Returns:
        np.ndarray: Array with the latitude axis inverted.
    """
    return np.flip(data, axis=lat_axis).copy()


def rh_to_q(
    rh: np.ndarray,
    t_k: np.ndarray,
    pressure_levels: Sequence[float] = PRESSURE_LEVELS,
) -> np.ndarray:
    """Convert relative humidity [%] and temperature [K] to specific humidity [kg/kg].

    Uses the Tetens empirical formula for saturation vapor pressure over water.

    Args:
        rh (np.ndarray): Relative humidity [%], shape (num_levels, H, W).
        t_k (np.ndarray): Temperature [K], shape (num_levels, H, W).
        pressure_levels (Sequence[float]): Pressure level values in hPa.

    Returns:
        np.ndarray: Specific humidity q [kg/kg] with identical shape.

    Raises:
        ValueError: If array level count does not match pressure_levels count.
    """
    if rh.shape[0] != len(pressure_levels) or t_k.shape[0] != len(
        pressure_levels
    ):
        raise ValueError(
            f"Input channel count ({rh.shape[0]}) does not match "
            f"pressure level count ({len(pressure_levels)})"
        )

    # Reshape pressure to broadcast across spatial dimensions (C, 1, 1)
    p = np.array(pressure_levels, dtype=np.float32)[:, np.newaxis, np.newaxis]

    t_c = t_k - 273.15
    # Saturation vapor pressure in hPa
    es = 6.112 * np.exp((17.67 * t_c) / (t_c + 243.5))
    e = (rh / 100.0) * es
    # Mixing ratio w
    w = 0.622 * e / np.maximum(p - e, 1e-6)
    # Specific humidity q
    q = w / (1.0 + w)
    return q.astype(np.float32)


def q_to_rh(
    q: np.ndarray,
    t_k: np.ndarray,
    pressure_levels: Sequence[float] = PRESSURE_LEVELS,
) -> np.ndarray:
    """Convert specific humidity [kg/kg] and temperature [K] to relative humidity [%].

    Inverse transformation of rh_to_q.

    Args:
        q (np.ndarray): Specific humidity [kg/kg], shape (num_levels, H, W).
        t_k (np.ndarray): Temperature [K], shape (num_levels, H, W).
        pressure_levels (Sequence[float]): Pressure level values in hPa.

    Returns:
        np.ndarray: Relative humidity RH [%] with values clipped to [0, 100].

    Raises:
        ValueError: If array level count does not match pressure_levels count.
    """
    if q.shape[0] != len(pressure_levels) or t_k.shape[0] != len(
        pressure_levels
    ):
        raise ValueError(
            f"Input channel count ({q.shape[0]}) does not match "
            f"pressure level count ({len(pressure_levels)})"
        )

    p = np.array(pressure_levels, dtype=np.float32)[:, np.newaxis, np.newaxis]
    # Mixing ratio from specific humidity
    w = q / np.maximum(1.0 - q, 1e-6)
    # Vapor pressure e from mixing ratio
    e = (w * p) / (0.622 + w)

    t_c = t_k - 273.15
    es = 6.112 * np.exp((17.67 * t_c) / (t_c + 243.5))
    rh = (e / np.maximum(es, 1e-6)) * 100.0
    return np.clip(rh, 0.0, 100.0).astype(np.float32)


def compute_solar_declination_and_hour_angle(
    dt: datetime,
    lon_deg: np.ndarray,
) -> tuple[float, np.ndarray]:
    """Compute solar declination and local hour angle for a given UTC datetime.

    Args:
        dt (datetime): UTC datetime timestamp.
        lon_deg (np.ndarray): Longitude array in degrees [-180, 180] or [0, 360].

    Returns:
        Tuple[float, np.ndarray]: (solar declination in radians, local hour
            angle in radians).
    """
    # Day of year
    day_of_year = dt.timetuple().tm_yday
    # Fractional hour in UTC
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    # Solar declination angle approximation (Cooper 1969)
    declination_deg = 23.45 * math.sin(
        math.radians((360.0 / 365.0) * (284 + day_of_year))
    )
    declination_rad = math.radians(declination_deg)

    # Normalize longitude to [-180, 180]
    lon_norm = (lon_deg + 180.0) % 360.0 - 180.0
    # Solar hour angle: 15 deg per hour from solar noon (approx 12 UTC at 0 lon)
    hour_angle_deg = 15.0 * (hour - 12.0) + lon_norm
    hour_angle_rad = np.deg2rad(hour_angle_deg)

    return declination_rad, hour_angle_rad


def calculate_cos_zenith_single_time(
    dt: datetime,
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
) -> np.ndarray:
    """Calculate cosine of solar zenith angle for a single timestamp over grid.

    Args:
        dt (datetime): UTC datetime.
        lat_deg (np.ndarray): 2D Latitude grid array in degrees.
        lon_deg (np.ndarray): 2D Longitude grid array in degrees.

    Returns:
        np.ndarray: Cosine zenith angle array of shape (H, W), values clamped
            in [-1, 1].
    """
    lat_rad = np.deg2rad(lat_deg)
    declination_rad, hour_angle_rad = (
        compute_solar_declination_and_hour_angle(dt, lon_deg)
    )

    # Spherical law of cosines for solar zenith angle
    cos_zenith = np.sin(lat_rad) * math.sin(declination_rad) + np.cos(
        lat_rad
    ) * math.cos(declination_rad) * np.cos(hour_angle_rad)

    return np.clip(cos_zenith, -1.0, 1.0).astype(np.float32)


def calculate_cos_zenith_series(
    timestamps: Sequence[datetime | np.datetime64 | str],
    lat_size: int = DEFAULT_LAT_SIZE,
    lon_size: int = DEFAULT_LON_SIZE,
) -> np.ndarray:
    """Calculate cosine of solar zenith angle for multiple timestamps.

    Args:
        timestamps (Sequence[Union[datetime, np.datetime64, str]]): List of
            timestamps.
        lat_size (int): Number of latitude points.
        lon_size (int): Number of longitude points.

    Returns:
        np.ndarray: Array of shape (len(timestamps), lat_size, lon_size).
    """
    lat = np.linspace(90.0, -90.0, lat_size, endpoint=False, dtype=np.float32)
    lon = np.linspace(0.0, 360.0, lon_size, endpoint=False, dtype=np.float32)
    grid_lat, grid_lon = np.meshgrid(lat, lon, indexing="ij")

    results = []
    for ts in timestamps:
        if isinstance(ts, np.datetime64):
            # Convert np.datetime64 to python datetime
            ts_sec = ts.astype("datetime64[s]").astype(int)
            dt = datetime.fromtimestamp(ts_sec, tz=UTC)
        elif isinstance(ts, str):
            # Parse ISO or YYYYMMDDHH
            cleaned = ts.replace("T", " ").replace(":", "").replace("-", "")
            if len(cleaned) == 10:
                dt = datetime.strptime(cleaned, "%Y%m%d%H").replace(
                    tzinfo=UTC
                )
            else:
                dt = datetime.fromisoformat(ts).replace(tzinfo=UTC)
        elif isinstance(ts, datetime):
            dt = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
        else:
            raise TypeError(f"Unsupported timestamp type: {type(ts)}")

        cos_z = calculate_cos_zenith_single_time(dt, grid_lat, grid_lon)
        results.append(cos_z)

    return np.stack(results, axis=0).astype(np.float32)
