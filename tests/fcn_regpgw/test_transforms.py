"""Unit tests for spatial, coordinate, and atmospheric transformations."""

from datetime import UTC, datetime

import numpy as np
import pytest

from fcn_regpgw.const import PRESSURE_LEVELS
from fcn_regpgw.data.transforms import (
    calculate_cos_zenith_series,
    flip_latitude,
    generate_sincos_grid,
    q_to_rh,
    rh_to_q,
)


def test_generate_sincos_grid() -> None:
    """Verify sincos grid shape and trigonometric range with deg2rad."""
    lat_size = 36
    lon_size = 72
    grid = generate_sincos_grid(lat_size=lat_size, lon_size=lon_size)

    assert grid.shape == (4, lat_size, lon_size)
    assert np.all(grid >= -1.0 - 1e-6)
    assert np.all(grid <= 1.0 + 1e-6)
    # North pole is 90 deg -> sin(90 deg) = 1.0, cos(90 deg) = 0.0
    assert pytest.approx(grid[0, 0, :].mean(), abs=1e-3) == 1.0
    assert pytest.approx(grid[1, 0, :].mean(), abs=1e-3) == 0.0


def test_flip_latitude() -> None:
    """Verify latitude flip along specified axis."""
    arr = np.arange(24).reshape(2, 3, 4)
    flipped = flip_latitude(arr, lat_axis=1)

    assert flipped.shape == (2, 3, 4)
    assert np.array_equal(flipped[:, 0, :], arr[:, 2, :])
    assert np.array_equal(flipped[:, 2, :], arr[:, 0, :])


def test_rh_to_q_and_q_to_rh_roundtrip() -> None:
    """Verify bidirectional consistency between rh_to_q and q_to_rh."""
    num_levels = len(PRESSURE_LEVELS)
    h, w = 10, 10

    # Initial RH between 10% and 90%
    np.random.seed(42)
    rh_orig = np.random.uniform(10.0, 90.0, size=(num_levels, h, w)).astype(
        np.float32
    )
    # Temperature between 220 K and 300 K
    t_k = np.random.uniform(220.0, 300.0, size=(num_levels, h, w)).astype(
        np.float32
    )

    q = rh_to_q(rh_orig, t_k, pressure_levels=PRESSURE_LEVELS)
    assert np.all(q > 0.0)

    rh_recovered = q_to_rh(q, t_k, pressure_levels=PRESSURE_LEVELS)
    assert np.allclose(rh_orig, rh_recovered, atol=1e-3)


def test_calculate_cos_zenith_series() -> None:
    """Verify solar zenith angle series computation."""
    dt1 = datetime(2025, 7, 24, 0, 0, tzinfo=UTC)
    dt2 = datetime(2025, 7, 24, 6, 0, tzinfo=UTC)

    zeniths = calculate_cos_zenith_series(
        [dt1, dt2], lat_size=18, lon_size=36
    )
    assert zeniths.shape == (2, 18, 36)
    assert np.all(zeniths >= -1.0)
    assert np.all(zeniths <= 1.0)
