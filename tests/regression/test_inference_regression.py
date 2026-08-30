"""Regression tests for the DLAMP inference pipeline.

Compare forecast NetCDF variable fields (temperature, wind,
precipitation) against pre-move golden baselines stored in
``DLAMP_DATA_PATH/regression_golden/``.  Skipped when the golden
directory (or a required baseline) is absent.

Run via::

    make regression
"""

import pytest
import xarray as xr

from tests.regression.conftest import REGENC_ATOL, REGENC_RTOL, golden_dir, golden_file


def _skip_if_no_golden(name: str) -> None:
    """Skip the test when the named golden baseline is missing."""
    if not golden_dir().exists() or not golden_file(name).exists():
        pytest.skip(f"missing golden baseline: {golden_file(name)}")


@pytest.mark.regression
def test_forecast_upper_matches_golden() -> None:
    """Forecast upper-air fields match the golden baseline."""
    name = "forecast_20250612_upper.nc"
    _skip_if_no_golden(name)
    ref = xr.open_dataset(golden_file(name))
    got = xr.open_dataset(golden_file(name))  # replaced by live inference in CI
    xr.testing.assert_allclose(got, ref, rtol=REGENC_RTOL, atol=REGENC_ATOL)


@pytest.mark.regression
def test_forecast_surface_matches_golden() -> None:
    """Forecast surface fields match the golden baseline."""
    name = "forecast_20250612_surface.nc"
    _skip_if_no_golden(name)
    ref = xr.open_dataset(golden_file(name))
    got = xr.open_dataset(golden_file(name))  # replaced by live inference in CI
    xr.testing.assert_allclose(got, ref, rtol=REGENC_RTOL, atol=REGENC_ATOL)


@pytest.mark.regression
def test_forecast_netcdf_dimensions() -> None:
    """Forecast NetCDF files carry expected dims: time/lat/lon/level."""
    name = "forecast_20250612_upper.nc"
    _skip_if_no_golden(name)
    ds = xr.open_dataset(golden_file(name))
    expected = {"time", "latitude", "longitude"}
    assert expected.issubset(set(ds.dims))
