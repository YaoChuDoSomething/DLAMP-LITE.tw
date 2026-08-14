# DLAMP Monorepo Refactor PRD

Status: ready-for-agent

## Problem Statement

The deep-learning weather forecasting codebase (**DLAMP.tw**) and its corresponding ERA5 data preprocessing pipeline (**DLAMP.data**) exist in separate repositories and fragmented directory structures. Researchers and developers experience friction due to:

- **Fragmented Workflows:** Training and data preparation require managing distinct repository clones, manual path manipulations, and mismatched environment setups.
- **Fragile Path Dependencies:** Code components rely on current-working-directory (CWD) relative paths and unvalidated environment variables (`DLAMP_EXP_CODE`), leading to runtime failures or silent loading of incorrect standardization stats.
- **Untested Data Pipeline:** The data preprocessing modules lack unit test coverage and automated quality gates, risking silent regression during data transformation.
- **Dependency Conflicts:** Independent dependency definitions create environment mismatches (e.g., PyTorch, NumPy, and Earth2Studio dependencies).

## Solution

Unify **DLAMP.tw** and **DLAMP.data** into a single monorepo (`YaoChuDoSomething/DLAMP`) with a clean `src/` layout under the `dlamp` Python namespace (`dlamp` for forecasting, `dlamp.data` for data pipelines).

Key highlights of the solution include:

1. **Git History Preservation:** Combine commit histories of both source repositories using `git-filter-repo` and `git merge --allow-unrelated-histories`.
2. **Anchored Path & Environment Security:** Anchor all asset, config, and output paths relative to the repository root (`dlamp.const`) and enforce strict startup validation between experiment codes and standardization assets.
3. **Packaging & CLI Integration:** Provide a single `pyproject.toml` with `uv_build` backend, exposing standardized console entry points (`dlamp-train`, `dlamp-predict`, etc.) while retaining backwards-compatible root script wrappers (`train.py`, `predict.py`, `data_prep.py`).
4. **Comprehensive Testing & Regression Strategy:** Establish a test suite (`tests/dlamp/`) with fast unit tests, integration markers, and an automated regression test suite (`make regression`) that asserts numerical parity (`rtol=1e-5`, `atol=1e-6`) against pre-refactor golden baseline snapshots.
5. **Scope Optimization:** Exclude legacy/unsupported components (SFNO processor and `earth2studio` dependencies) to maintain a lean, robust codebase.

## User Stories

1. As an AI/ML Researcher, I want to install `dlamp` as a single editable Python package (`pip install -e .`), so that I can access both forecasting architectures and data pipeline tools within one unified environment.
2. As an AI/ML Researcher, I want to launch model training and inference via standard CLI commands (`dlamp-train`, `dlamp-predict`) or root script wrappers (`train.py`, `predict.py`), so that my existing operational habits and scripts remain intact.
3. As a Data Engineer, I want the data preprocessing tools accessible under `dlamp.data.preproc` and `dlamp.data.registry`, so that I can download, regrid, and compute diagnostic features programmatically.
4. As an MLOps Engineer, I want `dlamp.const` to validate that `DLAMP_EXP_CODE` matches existing YAML configs and standardization JSON stats on import, so that execution halts immediately with a clear error if configurations do not match.
5. As an MLOps Engineer, I want all default asset and output directories anchored to absolute paths derived from the repo root, so that running entry points from any working directory produces deterministic output locations.
6. As a Developer, I want full Git history from both source repositories preserved in the monorepo, so that I can inspect commit history and git blame across past refactors.
7. As a Developer, I want legacy SFNO code and `earth2studio` dependencies removed from the repository history, so that the monorepo has no unmaintained external dependencies.
8. As a QA Engineer, I want fast unit tests running under `tests/dlamp/` without external dataset dependencies, so that CI/CD passes complete in seconds.
9. As a QA Engineer, I want an automated regression test suite (`@pytest.mark.regression`) comparing model inference and data pipeline outputs against pre-move golden arrays, so that I can guarantee zero numerical drift after restructuring.
10. As a Project Maintainer, I want single-source-of-truth design documentation and test specifications under `docs/design/` and `docs/testing/`, so that future architectural decisions and test plans remain transparent.

## Implementation Decisions

- **Namespace & Directory Structure:** Standard `src/` layout with `src/dlamp/` housing legacy DLAMP.tw submodules (`analysis`, `inference`, `visual`, `models`, `datasets`, `managers`, `utils`, `debug`) alongside `const.py` and `standardization.py`. The data pipeline resides under `src/dlamp/data/` (`preproc`, `registry`).
- **Un-packaged Root Directories:** Top-level data and artifact directories (`config/`, `assets/`, `export/`, `gallery/`, `outputs/`) remain outside the packaged Python wheel and are referenced via anchored root constants.
- **Repository Scaffolding & Merging:** Clean repository creation using `git init -b main`. Preserves source histories via `git-filter-repo` (filtering out SFNO components) and merging with `--allow-unrelated-histories`.
- **Environment & Path Resolution:** Derives `ROOT_DIR = Path(__file__).resolve().parents[2]` inside `dlamp.const` to replace hardcoded `./` paths. Import-time startup check validates matching config and z-score JSON files.
- **Packaging & Dependency Pins:** Standardized `pyproject.toml` with `uv_build` backend, targeting Python 3.11 (`>=3.11,<3.12`), `torch==2.4.0`, `numpy<2.0`, `lightning>=2.0.0`, and `hydra-core>=1.3.0`. Console scripts map `dlamp-train`, `dlamp-predict`, `dlamp-export-onnx`, `dlamp-infer-onnx`, `dlamp-gen-const-masks`, and `dlamp-unpack-tgz`.
- **Root Wrapper Scripts:** `train.py`, `predict.py`, and `data_prep.py` maintained at repository root as thin Hydra wrappers delegating directly to `dlamp.*` package entry points.
- **Legacy Repositories:** Source repositories (`DLAMP.tw` and `DLAMP.data`) updated with deprecation banners and archived on GitHub.

## Testing Decisions

- **Good Test Definition:** Tests strictly evaluate external module behavior, public function contracts, numerical correctness, and configuration validation. Private internal routines and temporary state are not directly coupled in unit tests.
- **Modules Tested:**
  - `src/dlamp/models/architectures/`: UNet, Glide UNet, Earth3D specifics.
  - `src/dlamp/data/preproc/`: CDS downloader, DLAMP regridder.
  - `src/dlamp/data/registry/`: Diagnostic functions and diagnostic registry.
  - `src/dlamp/utils/`: File utility paths, standardized z-score transformers.
  - End-to-end inference and data pipeline regression suites.
- **Prior Art & Test Hierarchy:**
  - Migrates legacy unittests from `src/dlamp/models/architectures/*_test.py` into `tests/dlamp/models/architectures/`.
  - Establishes unit tests (`tests/dlamp/`), integration tests (`@pytest.mark.integration`), and regression tests (`@pytest.mark.regression`).
  - Uses `xarray.testing.assert_allclose` and `numpy.testing.assert_allclose` with `rtol=1e-5`, `atol=1e-6` for numerical array verification against `DLAMP_DATA_PATH/regression_golden/` baseline snapshots. Exact array equality is enforced for discrete land-sea and topography masks.

## Out of Scope

- **Algorithmic/Model Logic Changes:** No modifications to forecasting model logic, loss functions, or neural network architectures.
- **Domain Variable Renaming:** No changes to physical variable names or domain vocabulary.
- **New Feature Addition:** No new data sources, diagnostic variables, or prediction tasks are added during this refactoring effort.
- **Cloud Infrastructure & Deployment:** Cloud orchestration, CI/CD runners, and deployment infrastructure setup remain out of scope for this task.

## Further Notes

- The refactor follow a 5-stage sequential execution sequence:
  1. *Stage 1:* Pre-move baseline generation (`DLAMP_DATA_PATH/regression_golden/`).
  2. *Stage 2:* Git history filtering and union merge into `dlamp-monorepo`.
  3. *Stage 3:* Package restructuring and `dlamp.const` path anchoring.
  4. *Stage 4:* Packaging setup (`pyproject.toml`) and environment verification.
  5. *Stage 5:* Test migration, unit test execution, and regression verification (`make regression`).
- Complete technical details are documented in [`docs/design/refactor-design.md`](file:///wk2/yaochu/main/dlamp/docs/design/refactor-design.md) and [`docs/testing/testing-specification.md`](file:///wk2/yaochu/main/dlamp/docs/testing/testing-specification.md).
