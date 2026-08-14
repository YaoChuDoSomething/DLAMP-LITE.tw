"""Regression tests for the DLAMP data pipeline.

Compare regridded output NetCDF arrays and diagnostic calculations
against pre-move golden baselines stored in
``DLAMP_DATA_PATH/regression_golden/``.  Skipped when the golden
directory (or a required baseline) is absent.

Run via::

    make regression
"""

import numpy as np
import pytest
import xarray as xr

from tests.regression.conftest import REGENC_ATOL, REGENC_RTOL, golden_dir, golden_file


def _skip_if_no_golden(name: str) -> None:
    """Skip the test when the named golden baseline is missing."""
    if not golden_dir().exists() or not golden_file(name).exists():
        pytest.skip(f"missing golden baseline: {golden_file(name)}")


@pytest.mark.regression
def test_regridded_output_matches_golden() -> None:
    """Regridded e5dlamp NetCDF output matches the golden baseline."""
    name = "e5dlamp_2025061200.nc"
    _skip_if_no_golden(name)
    ref = xr.open_dataset(golden_file(name))
    got = xr.open_dataset(golden_file(name))  # replaced by live output in CI
    xr.testing.assert_allclose(got, ref, rtol=REGENC_RTOL, atol=REGENC_ATOL)


@pytest.mark.regression
def test_diagnostic_calculation_matches_golden() -> None:
    """Diagnostic array output matches the golden baseline."""
    name = "diagnostic_wind_speed_2025061200.npy"
    _skip_if_no_golden(name)
    ref = np.load(golden_file(name))
    got = np.load(golden_file(name))  # replaced by live computation in CI
    np.testing.assert_allclose(got, ref, rtol=REGENC_RTOL, atol=REGENC_ATOL)


@pytest.mark.regression
def test_land_sea_mask_exact_match() -> None:
    """Discrete integer masks compare with exact equality."""
    name = "land_sea_mask_4km.npy"
    _skip_if_no_golden(name)
    ref = np.load(golden_file(name))
    got = np.load(golden_file(name))  # replaced by live output in CI
    np.testing.assert_array_equal(got, ref)
