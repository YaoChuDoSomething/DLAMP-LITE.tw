# Core Utils Test Plan

## 1. Scope & Target Submodules

- `dlamp.const` (Constants & `RuntimeConfig`)
- `dlamp.standardization` (`Standardizer`)
- `dlamp.utils.file_util` (`gen_path`, file pattern generators)
- `dlamp.visual` (Visualization utilities)

## 2. Unit Test Specifications

- `tests/dlamp/test_const.py`: Test environment variable reading (`DLAMP_EXP_CODE`, `DLAMP_DATA_SOURCE`, `DLAMP_DATA_PATH`), root directory anchoring (`ROOT_DIR`), and `RuntimeConfigError` raising on missing configuration files.
- `tests/dlamp/test_standardization.py`: Test z-score standardization and inverse transformation logic on synthetic arrays.
- `tests/dlamp/utils/test_file_util.py`: Test file path generation across data sources (`OP_ERA5`, `OP_E2S`, `CWA_RWRF`, `NEO171_RWRF`).
- `tests/dlamp/visual/test_visual.py`: Test map rendering and figure generation functions.

## 3. Integration Test Scenarios (`@pytest.mark.integration`)

- Standardizer loading real `z_score_3h_*.json` asset files and normalizing sample NetCDF variables.

## 4. Regression Test Specifications (`@pytest.mark.regression`)

- Verification that `gen_path` yields exact string paths matching legacy output for identical datetime and source inputs.

## 5. Fixtures & Environment Requirements

- Sample standardization JSON fixtures in `tests/fixtures/standardization/`.

## 6. Target Coverage & Acceptance Criteria

- Target Line Coverage: >90%
- `dlamp.const` environment validation tested for both success and failure cases.
