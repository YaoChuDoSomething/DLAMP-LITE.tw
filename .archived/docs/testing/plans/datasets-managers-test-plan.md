# Datasets & Managers Test Plan

## 1. Scope & Target Submodules

- `dlamp.datasets.custom_dataset` (`CustomDataset`)
- `dlamp.managers.data_manager` (`DataManager`)
- `dlamp.managers.datetime_manager` (`DatetimeManager`)

## 2. Unit Test Specifications

- `tests/dlamp/datasets/test_custom_dataset.py`: Test PyTorch `Dataset` item indexing, sequence window sliding, and data loading pipeline.
- `tests/dlamp/managers/test_data_manager.py`: Test data batching, cache management, and memory allocation.
- `tests/dlamp/managers/test_datetime_manager.py`: Test timestamp parsing, step incrementing, and lead-time calculations.

## 3. Integration Test Scenarios (`@pytest.mark.integration`)

- Loading PyTorch `DataLoader` with `CustomDataset` over actual ERA5 NetCDF files.

## 4. Regression Test Specifications (`@pytest.mark.regression`)

- Verification that dataset sequence generation produces identical tensor indexing to legacy `CustomDataset`.

## 5. Fixtures & Environment Requirements

- Dummy NetCDF dataset fixtures generated via `xarray` in `@pytest.fixture`.

## 6. Target Coverage & Acceptance Criteria

- Target Line Coverage: >85%
- `DatetimeManager` handles all edge cases (month transitions, leap years, time zone offsets) correctly.
