# Data Pipeline Test Plan

## 1. Scope & Target Submodules

- `dlamp.data.preproc.cds_downloader` (`CDSDataDownloader`)
- `dlamp.data.preproc.dlamp_regridder` (`DataRegridder`)
- `dlamp.data.registry.diagnostic_functions` (31 diagnostic functions)
- `dlamp.data.registry.diagnostic_registry` (`DiagnosticRegistry`)

## 2. Unit Test Specifications

- `tests/dlamp/data/preproc/test_cds_downloader.py`: Mock CDS API requests, verify download parameter formatting and error handling.
- `tests/dlamp/data/preproc/test_dlamp_regridder.py`: Verify grid coordinate transformations, interpolation bounds, and mask application.
- `tests/dlamp/data/registry/test_diagnostic_functions.py`: Test all 31 diagnostic functions against synthetic input arrays with known mathematical solutions.
- `tests/dlamp/data/registry/test_diagnostic_registry.py`: Verify function registration, lookup by name, and parameter passing.

## 3. Integration Test Scenarios (`@pytest.mark.integration`)

- End-to-end processing of a sample ERA5 raw NetCDF file into an `e5dlamp_*` formatted output using local CDO binaries.

## 4. Regression Test Specifications (`@pytest.mark.regression`)

- Compare regridded output NetCDF arrays and diagnostic calculations against pre-move golden outputs in `DLAMP_DATA_PATH/regression_golden/`.
- Tolerance: `rtol=1e-5`, `atol=1e-6`.

## 5. Fixtures & Environment Requirements

- `DLAMP_DATA_PATH` pointing to ERA5 sample pool.
- Mock CDS API response fixtures in `tests/fixtures/cds_mocks.py`.

## 6. Target Coverage & Acceptance Criteria

- Target Line Coverage: >85%
- All 31 diagnostic functions unit tested and passing.
