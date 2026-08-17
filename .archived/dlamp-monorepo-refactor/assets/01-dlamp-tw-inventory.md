# DLAMP.tw Inventory (ticket 01)

Source: `/wk2/yaochu/main/dlamp` (repo: DLAMP.tw, branch `dev`, 53 commits).

## 1. Git facts

- Branch `dev` only; remote branches: `origin/Inference`, `origin/dev`, `origin/v25.06_Tutorial`, `origin/v25.10/m20250627`, `origin/v25.11/OP`.
- Remote: `https://github.com/YaoChuDoSomething/DLAMP.tw.git`.
- LFS-tracked (`.gitattributes`): `assets/demo/**`, `assets/town_shp/**`, `assets/terrain_shp/**`, `assets/constant_masks/**`, `export/*.onnx`.
  - Actual LFS objects present (`git lfs ls-files`): `assets/constant_masks/{land_sea_mask_2km,land_sea_mask_4km,topography_mask_2km,topography_mask_4km}.npy`, `assets/demo/typhoons.gif`, `assets/terrain_shp/{GIS_terrain.dbf,shp,shx,gt30e100n40.tif}`, `assets/town_shp/COUNTY_MOI_1090820.{shp,shx}`.
  - Note the LFS/ignore conflict: `export/*.onnx` is LFS-tracked in `.gitattributes` but `export/` and `**.onnx` are gitignored — `export/` is currently empty (no committed onnx).
- `.gitignore`: `__pycache__/`, `*.py[cod]`, `outputs/`, `lat.npy`, `lon.npy`, `predict_yaochu*.py`, `logs/`, `*.err`/`*.out`, `checkpoints/`, `export/`, `**.onnx`, `profiler/`, `*.log`, `*.docx`, `.ipynb_checkpoints`, `*.ipynb`, `output/**nc`, `debug_plots/**png`, `*.png`, `*.gif`.
- **Untracked (uncommitted) scaffolding**: `.coverage`, `.gemini/`, `.pre-commit-config.yaml`, `AGENTS.md`, `CLAUDE.md` (symlink→AGENTS.md), `Makefile`, `docs/`, `externals/`, `lightning_logs/`, `pyproject.toml`, `src/dlamp/`, `tests/`, `uv.lock`. The new package, tests, and tooling are **not yet committed**.
- `externals/dlamp-data/` is a **nested git repo** (own `.git`), currently untracked by the parent — an embedded copy of an older DLAMP.data-era pipeline (SFNO/ERA5 preproc). **Hazard**: with the monorepo decision (ticket 03) this is a third copy of the data pipeline that must be reconciled with the `github/dlamp-data` repo.

## 2. Entrypoints

| Entrypoint | Purpose |
|---|---|
| `train.py` | `@hydra.main` train entry (`config/train_pangu.yaml`). Builds `DataManager` (Lightning DataModule) via `DataCompose.from_config`, builder via `get_builder(cfg.model.model_name)`, W&B logger, `Trainer.fit`. `OmegaConf.set_struct(True)`. |
| `predict.py` | `@hydra.main` full inference→NetCDF→plots pipeline (`config/predict.yaml`): `PredictionRunner` → `AnalysisDataManager` → `ForecastSaver` (WRF-compatible NetCDF) → `WeatherPlotter` 12-panel figures. |
| `src/export_onnx.py` | Export a checkpoint to `export/<model>_model_<date>.onnx`. |
| `src/inference_onnx.py` | Standalone ONNX inference driver. |
| `src/generate_const_masks.py` | Generates land-sea / topography constant masks. |
| `src/unzip_tgz.py` | Extracts `.tgz` data archives under `DATA_PATH`. |

## 3. Top-level directories

| Dir | Contents |
|---|---|
| `analysis/` | Post-inference analysis & outputs: `data_manager.py` (disassembles prediction arrays into physical vars/levels, derives wind speed/vorticity), `forecast_saver.py` (writes WRF-compatible NetCDF), `netcdf_meta.py` (WRF metadata dicts), `plot_meta.py` (12-panel plot configs), `plotter.py` (cartopy analysis figures), `prediction.py` (orchestrates inference via `inference.InferenceBase`), `video_creator.py` (images→MP4). |
| `inference/` | Inference engines: `inference_base.py` (abstract base; boundary/FFT blending debug hooks), `batch_inference_ckpt.py` / `batch_inference_onnx.py` (PyTorch vs ONNX runtime loops), `infer_utils.py` (ORT init, load Pangu model, prediction postprocess/destandardization). |
| `visual/` | Matplotlib viz panels: `tw_background.py` (Taiwan GIS background), `viz_{gph,pressure,temp,wind,radar,vor,mixing_ratio,omega,swdown}.py` (per-variable plotting with colormap conventions). |
| `config/` | Hydra configs: `data/` (`rwrf_<expcode>.yaml`, dated model versions), `lightning/`, `model/`, `inference/` (ckpt/onnx engines), `plot/`; entry files `train_pangu.yaml`, `train_diffusion.yaml`, `train_diffusion_radar.yaml`, `predict.yaml`. |
| `assets/` | `standardization/z_score_3h{,_20250611,_20250627,_20250729}.json`, `constant_masks/` (LFS npy), `terrain_shp/`, `town_shp/`, `demo/typhoons.gif`, `blacklist_rwrf_3h.txt` (**currently empty**). |
| `gallery/` | (empty) figure output dir. |
| `export/` | (empty, gitignored) ONNX export target. |
| `externals/dlamp-data/` | Nested git repo, older data-pipeline copy (see §1 hazard). |
| `docs/` | Agent/process docs (`agents/`, `architecture-init.md`, handoff summaries, prompts, tutorials). |
| `tests/` | `test_dlamp.py` — only pytest-collected tests (see §6). |

## 4. `src/` subtree

| Module | Purpose / key deps |
|---|---|
| `src/const.py` | Global constants: env-driven `MODEL_CODE`/`DATA_SOURCE`/`DATA_PATH` (`DLAMP_EXP_CODE`, `DLAMP_DATA_SOURCE`, `DLAMP_DATA_PATH`), standardization/data-config paths, blacklist/checkpoint/mask/shp paths, radar/rain/wind/temp colormaps, `EVAL_CASES`. Imported by nearly everything. |
| `src/standardization.py` | z-score calc + (de)standardization against `z_score_3h_<code>.json`; `Qt` log-transform special case. |
| `src/export_onnx.py`, `src/inference_onnx.py`, `src/generate_const_masks.py`, `src/unzip_tgz.py` | Standalone tools (see §2). |
| `src/datasets/` | `custom_dataset.py`: `CustomDataset(torch Dataset)` — loads via `DataGenerator`, applies `standardization`. |
| `src/managers/` | `data_manager.py`: `DataManager(L.LightningDataModule)`; `datetime_manager.py`: `DatetimeManager` (time-range sampling, blacklist, eval cases). |
| `src/utils/` | `data_type.py`: `DataType`/`Level` enums (var codes + nc keys); `data_compose.py`: pydantic `DataCompose` (var×level composition, config parsing); `data_generator.py`: `DataGenerator` (shapes/crops/resizes); `file_util.py`: `gen_path` (per-source filename patterns), `gen_data` (source dispatch), `read_cwa_ncfile`/`read_cwa_npfile`, `convert_hydra_dir_to_timestamp`; `time_util.py`: `TimeUtil`. |
| `src/debug/` | `boundary_plots.py`: boundary/blending verification + FFT blending debug plots (used by inference base). |
| `src/models/` | Model package (see below). |
| `src/models/architectures/` | `pangu_model.py` (Swin/Pangu backbone, 3D-specific layers), `earth_3d_specifics.py`, `unet.py` + `glide_unet.py` (ResUNet / Glide UNet), `multilayer_perceptron.py`, `smoothing.py`, `drop_path.py`. |
| `src/models/builders/` | `base_builder.py` (ABC), `pangu_builder.py`, `glide_builder.py` (builds model/trainer, W&B, checkpointing). |
| `src/models/lightning_modules/` | `pangu_lightning_module.py`, `diffusion_lightning_module.py` (also creates DDIM/DDPM modules). |
| `src/models/diffusion_process/` | `ddpm_process.py`, `ddim_process.py` (noise schedules / sampling). |
| `src/models/loss_fn/` | `crps.py` (CRPS), `euclidean.py`. |
| `src/models/callbacks/` | `log_prediction_samples_callback.py`, `log_diffusion_pred_samples_callback.py` (W&B image logging). |
| `src/models/model_utils.py` | `get_builder`, crop/pad helpers, schedulers, `RunningAverage`, shape restructuring. |

## 5. The new starter package `src/dlamp/`

- Files: `__init__.py` (version 0.1.0), `model.py` (`SimpleMLP`), `datamodule.py` (`SyntheticDataModule`/`SyntheticDataset`), `lightning_module.py` (`DLAMPModule`), `train.py` (hydra entry, config_path=`config`), `config/config.yaml` (toy in/out/hidden/lr), `py.typed`.
- **It is a toy/synthetic scaffold** — trains an MLP on random data, CPU-only. It does NOT wrap the real Pangu/Glide models yet. Its purpose is to validate the src-layout/package/test toolchain (pyproject `name="dlamp"`, `uv_build` backend, mypy strict, ruff 79 cols, pytest `pythonpath=["src"]`).
- Imported as `from dlamp...` (package name `dlamp`), so under the standard layout it lives at `src/dlamp/` and resolves via `pythonpath=["src"]`.
- The `src/dlamp/config/config.yaml` is a **separate toy config** — unrelated to the real top-level `config/` Hydra tree. Ticket 03 must reconcile (the `dlamp` namespace is also where the real models should eventually move).

## 6. Tests

- **Runnable now** (pytest, `tests/`): `test_dlamp.py` — 5 tests for the starter package only (MLP forward, module loss, synthetic dataset/datamodule, config loading). Relies on `dlamp.*` imports.
- **Stale `unittest` tests** under `src/models/architectures/`:
  - `pangu_model_test.py` — **crashes at import**: `open("config/model/dlamp_train.yaml")` which does not exist (config tree has only `pangu_rwrf_*`/`diffusion_rwrf_*`). Run via `python -m src.models.architectures.pangu_model_test`.
  - `glide_unet_test.py`, `unet_test.py`, `earth_3d_specifics_test.py` — valid-looking shape tests but hardcode `.cuda()` (need GPU) and are not pytest-collected (`testpaths=["tests"]`).
- `.coverage` present from a prior `pytest --cov=src/dlamp` run.
- **Hazard for ticket 11**: the `architectures/*_test.py` files live inside the package and import from `src.models` (old namespace), while the new suite imports `dlamp.*` (new namespace) — two coexisting test worlds.

## 7. Import graph (condensed)

```
train.py        → src.managers.DataManager, src.models.get_builder, src.utils.DataCompose
predict.py      → analysis.{data_manager,forecast_saver,plotter,prediction}
analysis.prediction → inference.InferenceBase, src.utils.{DataCompose,DataGenerator}
analysis.*      → src.const, src.utils.{DataCompose,DataType,Level,DataGenerator}, analysis.{netcdf_meta,plot_meta}
inference.*     → src.{datasets,debug,managers,models,standardization,utils}
src.models      → src.const, src.utils, (pangu_model reads mask npy via src.const paths)
src.managers    → src.datasets, src.utils, src.const
src.datasets    → src.standardization, src.utils
src.utils       → src.const, src.utils.data_type/data_compose
visual.*        → src.const, src.utils, visual.tw_background
src.models.builders.glide_builder → inference.infer_utils  (ONNX path; couples models→inference)
tests/test_dlamp → dlamp.{datamodule,lightning_module,model}
```

Couplings worth flagging for the move: `inference`↔`models` (bidirectional), `models.builders.glide_builder → inference.infer_utils`, `visual → src`, and `src.const` being the hub nearly everything imports.

## 8. Packaging facts (for ticket 06)

- `pyproject.toml` (new, source of truth): `name="dlamp"`, `version=0.1.0`, `requires-python=">=3.11,<3.12"`, backend `uv_build`. Deps: torch, lightning, hydra-core, pyyaml, numpy<2.0, pydantic, torchvision, scipy, matplotlib, xarray, dask, h5netcdf, netcdf4, cfgrib, cftime, cdsapi, cdo, eccodeslib, eckitlib, onnx, openvino, onnxruntime-gpu, onnxruntime-openvino, ipykernel, scikit-learn, wandb, importlib-metadata, requests, termcolor, mlflow, opencv-python, metpy, cartopy, geopandas, einops, rasterio. Dev extras: ruff, mypy, radon, pytest, pytest-cov, pre-commit.
- `requirements.txt` (older, README-referenced): torch==2.4.0, torchvision==0.19.0, numpy<2.0, + minimal set. Overlap with pyproject; torch pin is stricter here.
- Tooling: `Makefile` (`install`=`uv sync --extra dev`; `test`=`uv run pytest --cov=src/dlamp tests/`; `check`=ruff+mypy+radon on `src/dlamp`), `.pre-commit-config.yaml` (trailing-whitespace, eof-fixer, check-yaml, check-added-large-files, ruff --fix, ruff-format), `.python-version` (3.11), `uv.lock`, `.venv`.
- mypy: `strict=true`, `python_version=3.11`, `mypy_path="src"`. ruff: `line-length=79`, `target-version=py311`.

## 9. Hazards / notes for the map

1. `externals/dlamp-data` nested git repo — third copy of the data pipeline; disposition needed in ticket 03 (delete / convert to submodule / ignore).
2. New scaffolding (src/dlamp, tests, pyproject, Makefile, docs, AGENTS.md) is **uncommitted** on `dev` — history-preserving merge (ticket 07) must capture it before the merge or it's lost.
3. Two test worlds: `dlamp.*` (pytest) vs `src.models` (`unittest`, GPU-bound, one import-crashing).
4. `src.const` is the hub; `models ↔ inference` bidirectional coupling — moving to a namespace must preserve or refactor these edges.
5. Dated config/z-score files must stay aligned (`MODEL_CODE`↔`rwrf_<code>.yaml`↔`z_score_3h_<code>.json`); a mismatch silently mis-standardizes.
6. `assets/blacklist_rwrf_3h.txt` is empty (may be an incomplete migration).
