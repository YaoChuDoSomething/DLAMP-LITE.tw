# DLAMP Monorepo Architecture & Refactor Design

**Document Version:** 1.0.0  
**Target Repo:** `YaoChuDoSomething/DLAMP` @ `/wk2/yaochu/main/dlamp-monorepo`  
**Status:** Approved & Locked  

---

## 1. Executive Summary & Scope

This document details the refactoring design for merging **DLAMP.tw** (deep learning weather forecasting) and **DLAMP.data** (ERA5/SFNO data pipeline) into a single, unified monorepo (`YaoChuDoSomething/DLAMP`).

### Invariant Rules & Boundaries

- **Python Version:** Single universe **Python 3.11** (`>=3.11,<3.12`).
- **Framework Pins:** `torch==2.4.0`, `numpy<2.0`, `lightning>=2.0.0`, `hydra-core>=1.3.0`.
- **SFNO Scope Exclusion:** SFNO processor and dependencies (`earth2studio`) are explicitly **excluded** from the monorepo.
- **Git History:** Complete commit histories of both source repositories are preserved via `git-filter-repo` and `git merge --allow-unrelated-histories`.

---

## 2. Target Repository Architecture

```text
dlamp-monorepo/
├── src/
│   ├── dlamp/                      # Package `dlamp` (DLAMP.tw side)
│   │   ├── const.py                # dlamp.const (repo-root anchored constants)
│   │   ├── standardization.py      # dlamp.standardization
│   │   ├── analysis/               # forecast_saver, prediction, plotter, video_creator
│   │   ├── inference/              # inference_base, batch_inference_{ckpt,onnx}, infer_utils
│   │   ├── visual/                 # viz_*.py, tw_background
│   │   ├── models/                 # architectures, builders, callbacks, diffusion_process, lightning_modules, loss_fn, model_utils
│   │   ├── datasets/               # custom_dataset
│   │   ├── managers/               # data_manager, datetime_manager
│   │   ├── utils/                  # file_util, gen_path...
│   │   └── debug/                  # boundary_plots
│   └── dlamp/
│       └── data/                   # Package `dlamp.data` (DLAMP.data side)
│           ├── preproc/            # cds_downloader, dlamp_regridder
│           └── registry/           # diagnostic_functions, diagnostic_registry
├── config/                         # UN-PACKAGED top-level Hydra configs
│   ├── data/                       # rwrf_*.yaml, era5.yaml, data_downloader.yaml
│   ├── model/
│   ├── lightning/
│   ├── inference/
│   └── plot/
├── assets/                         # UN-PACKAGED top-level LFS asset data
│   ├── constant_masks/
│   ├── terrain_shp/
│   ├── town_shp/
│   └── target.nc
├── export/                         # UN-PACKAGED ONNX models (*.onnx)
├── gallery/                        # UN-PACKAGED plot output directory
├── outputs/                        # UN-PACKAGED Hydra runtime output logs
├── docs/                           # Documentation, ADRs, design, testing
├── tests/                          # Mirrored unit, integration & regression tests
├── GEMINI.md                       # Verbatim code quality rules
├── AGENTS.md                       # Updated agent instructions
├── Makefile                        # Updated automation targets
├── .pre-commit-config.yaml         # Verbatim pre-commit config
├── pyproject.toml                  # Merged dependencies & [project.scripts]
└── .gitattributes                  # Merged LFS tracking rules
```

---

## 3. Entry Points & CLI Disposition

### Standard Console Entry Points (`[project.scripts]`)

Defined in `pyproject.toml`:

- `dlamp-train` -> `dlamp.train:main`
- `dlamp-predict` -> `dlamp.analysis.prediction:main`
- `dlamp-export-onnx` -> `dlamp.export_onnx:main`
- `dlamp-infer-onnx` -> `dlamp.inference_onnx:main`
- `dlamp-gen-const-masks` -> `dlamp.generate_const_masks:main`
- `dlamp-unpack-tgz` -> `dlamp.unzip_tgz:main`

### Repo Root Thin Wrappers

Runnable from repository root:

- `train.py` -> delegates to Hydra `dlamp-train`
- `predict.py` -> delegates to Hydra `dlamp-predict`
- `data_prep.py` -> thin wrapper delegating to `dlamp.data.preproc`

---

## 4. Configuration & Environment Policy

1. **Environment Variables:**
   - `DLAMP_EXP_CODE` (default `"20250627"`)
   - `DLAMP_DATA_SOURCE` (default `"OP_ERA5"`)
   - `DLAMP_DATA_PATH` (default `"/wk2/yaochu/CASE_DATA/Pool/"`)
2. **Startup File Validation:** `dlamp.const` validates on import that matching `config/data/rwrf_<code>.yaml` and `assets/standardization/z_score_3h_<code>.json` exist, raising an explicit `RuntimeConfigError` on mismatch.
3. **Repository Root Anchoring:** `dlamp.const` derives `ROOT_DIR = Path(__file__).resolve().parents[2]`, making all derived path constants CWD-independent.
4. **Hydra Configuration:** All Hydra entrypoints set `chdir: False` so outputs land in `./outputs/<YYYY-MM-DD>/<HH-MM-SS>/`.

---

## 5. Merged Packaging & Dependencies (`pyproject.toml`)

- **Build Backend:** `uv_build`
- **Dependencies:**
  - `torch==2.4.0`
  - `numpy<2.0`
  - `lightning>=2.0.0`
  - `hydra-core>=1.3.0`
  - `xarray>=2026.7.0`
  - `netcdf4>=1.7.3`
  - `h5netcdf>=1.8.1`
  - `pyproj`
  - `pandas`
  - `matplotlib`
  - `scipy`
  - `cdo` / `eccodes` (noted as conda-forge requirements)
- **Extra `[project.optional-dependencies]`:** `dlamp[dev]` containing `pytest`, `pytest-cov`, `ruff`, `mypy`.

---

## 6. Execution Breakdown & Definition of Done

1. **Stage 1 (Pre-Move Baselines):** Capture golden baseline arrays in `DLAMP_DATA_PATH/regression_golden/`.
2. **Stage 2 (History Merge):** Run `git-filter-repo` (excluding SFNO) and union-merge into `dlamp-monorepo`.
3. **Stage 3 (Restructuring & Path Anchoring):** Move modules to `src/dlamp/` and `src/dlamp/data/`, update `dlamp.const`.
4. **Stage 4 (Packaging & Scripts):** Write `pyproject.toml`, test `uv pip install -e .`.
5. **Stage 5 (Testing & Regression):** Migrate tests, run `pytest -m "not integration and not regression"` and `make regression`.
