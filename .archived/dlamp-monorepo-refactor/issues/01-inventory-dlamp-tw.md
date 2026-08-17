# 01 Inventory DLAMP.tw layout

Type: research
Status: resolved
Blocked by:

## Question

Read `/wk2/yaochu/main/dlamp` (DLAMP.tw @ `dev`). Produce a markdown inventory — linked as an asset in this issue's resolution — that documents:

- Every top-level dir: `analysis/` (data_manager, forecast_saver, netcdf_meta, plot_meta, plotter, prediction, video_creator), `inference/` (batch_inference_ckpt/onnx, infer_utils, inference_base), `visual/` (viz_* modules), `config/` (data/, lightning/, model/, inference/, plot/ + the dated `rwrf_YYYYMMDD` versions), `assets/` (standardization z_score files), `gallery/`, `export/`, `externals/`, `docs/`, `tests/`.
- The `src/` subtree: `src/{datasets,debug,dlamp,managers,models,utils}`, including `src/models/{architectures,builders,callbacks,diffusion_process,lightning_modules,loss_fn}` — one line each on purpose and key dependencies.
- The **new starter package** `src/dlamp/` (datamodule, lightning_module, model, train, `config/config.yaml`) — what it already covers and what's missing.
- The import graph among the above (who imports whom), and the entrypoints `train.py` / `predict.py`.
- Stale, dead, or test-only code (e.g. the crashing `pangu_model_test.py`, tests that reference a non-existent `config/model/dlamp_train.yaml`).

Also capture the git facts: LFS-tracked assets (`assets/**/*.npy`, `export/*.onnx`), `.gitignore` contents, current branch/history shape.

Output: an inventory markdown doc (saved under `docs/design/inputs/` in a scratch location or attached path recorded in the resolution comment) that ticket 03 consumes to propose the target tree.

## Answer

Inventory completed. Full asset: `.scratch/dlamp-monorepo-refactor/assets/01-dlamp-tw-inventory.md`.

Key findings for ticket 03:

- **Entrypoints**: `train.py`, `predict.py` (`@hydra.main`), plus standalone tools `src/export_onnx.py`, `src/inference_onnx.py`, `src/generate_const_masks.py`, `src/unzip_tgz.py`.
- **Five top-level code dirs to fold**: `analysis/` (post-inference analysis/saving/plotting), `inference/` (ckpt/onnx engines), `visual/` (matplotlib panels), `config/` (Hydra, dated), `assets/` (z-score json, LFS masks/shp/gif).
- **`src/` submodules to fold**: `const` (env-driven hub), `standardization`, `datasets`, `managers`, `utils` (incl. `file_util.gen_path` per-source naming), `debug` (boundary/FFT plots), `models/` (architectures, builders, lightning_modules, diffusion_process, loss_fn, callbacks).
- **Starter package `src/dlamp/`** is a toy MLP scaffold (importable as `dlamp`, pytest via `pythonpath=["src"]`, mypy strict) — unrelated to the real models; config is toy-only.
- **Two test worlds**: new `dlamp.*` pytest suite (`tests/test_dlamp.py`, 5 tests) vs stale `unittest` `src/models/architectures/*_test.py` (pangu crashes at import — missing `config/model/dlamp_train.yaml`; glide/unet/earth tests hardcode `.cuda()`).
- **Git**: `dev` branch, 53 commits; new scaffolding is **uncommitted** (must be captured before history merge); LFS assets listed; `export/` empty despite LFS rule.
- **Top hazards**: nested git repo `externals/dlamp-data` (a *third* copy of the data pipeline, untracked) — needs disposition; `models ↔ inference` bidirectional coupling (`glide_builder → inference.infer_utils`); `src.const` hub; dated config↔z-score alignment trap.
