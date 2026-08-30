# Agent Instructions

## Environment

src-layout package: `pyproject.toml` (uv_build backend) declares deps; `requirements.txt` pins `numpy<2.0`, `torch==2.4.0`. Python 3.11. Repo has root `.venv/` — `which python` → `.venv/bin/python`, and `src/` is on sys.path, so `import dlamp` works from anywhere.

Always run entrypoints from repo root: every Hydra config sets `chdir: False`, so `outputs/<YYYY-MM-DD>/<HH:MM:SS>/` is written into the CWD, and some paths are CWD-relative (`export/`, and stale tests open `config/model/dlamp_train.yaml`).

## Entrypoints

| Command | Purpose |
| --------- | --------- |
| `python train.py` | Train Pangu model (`train_pangu` config); use `python train.py --config-name train_diffusion` for the DDPM/Glide model, or `--config-name train_diffusion_radar` for the radar-only variant (`model.only_radar: True`) |
| `python predict.py` | Full pipeline: inference → NetCDF forecasts → analysis plots (`predict` config, ONNX engine by default) |
| `python predict_dscale.py` | One-way downscaling inference (no boundary feedback); `bdy_swap_method` forced null |
| `python predict_feedback.py` | Two-way boundary-feedback inference; re-injects observations at every model step |
| `python data_prep.py` | Generate constant masks (land-sea, topography) required before first training/inference |
| `python data_stats.py` | Compute z-score standardization stats and write to `assets/standardization/` |
| `python -m dlamp.export_onnx` | Export a checkpoint to `export/<model>_model_<date>.onnx` |

All are `@hydra.main`; logs/artifacts go to `outputs/<YYYY-MM-DD>/<HH:MM:SS>/`.

## Runtime Config

- Env vars are read in `src/dlamp/runtime_config.py` (NOT `const.py`, which is pure constants): `DLAMP_EXP_CODE` (default `20250627`), `DLAMP_DATA_SOURCE` (default `OP_ERA5`), `DLAMP_DATA_PATH` (default `/wk2/yaochu/CASE_DATA/Pool/`).
- `DLAMP_EXP_CODE` selects `config/data/rwrf_<code>.yaml` and `assets/standardization/z_score_3h_<code>.json`. `RuntimeConfig.from_env()` now validates both files exist and raises `RuntimeConfigError` at startup — but a wrong code whose files happen to exist still silently loads that code's stats, so the code must match the model version.
- Raw per-hour NetCDF input lives in `DLAMP_DATA_PATH`; filename pattern depends on `DLAMP_DATA_SOURCE` (`src/dlamp/utils/file_util.py:gen_path`; sources: `OP_ERA5`, `OP_E2S`, `CWA_RWRF`, `NEO171_RWRF`).
- Config is strict (`OmegaConf.set_struct(cfg, True)`): unknown or missing keys raise errors.

## Config Layout

`config/` splits into `data/`, `lightning/`, `model/`, `inference/`, `plot/`, wired together in `predict.yaml`, `predict_dscale.yaml`, `predict_feedback.yaml`, `data_prep.yaml`, `data_stats.yaml`, `train_pangu.yaml`, `train_diffusion.yaml`, `train_diffusion_radar.yaml`. Dated names (`rwrf_YYYYMMDD`) are model versions. `config/inference/*` picks the engine: `onnx` needs `export/*.onnx` (gitignored — export first), `ckpt` needs `checkpoints/*.ckpt` (gitignored).

Runner classes: `PredictDscaleRunner`, `PredictFeedbackRunner`, `DataPrepRunner`, `DataStatsRunner` live in `src/dlamp/workflows/` (exported from `__init__.py`); entrypoints are thin Hydra shells delegating to them. Exception: `predict.py` has no workflows runner — its logic is `dlamp.analysis.prediction.PredictionRunner` in `src/dlamp/analysis/`.

## Models

Architectures live in `src/dlamp/models/architectures/`, lightning modules in `src/dlamp/models/lightning_modules/`, builders in `src/dlamp/models/builders/`. Dispatch is by `cfg.model.model_name` (`Pangu` → `PanguBuilder`, `Glide` → `GlideBuilder`).

## Tests

Mostly broken — don't trust them as a pass/fail gate.

- Only working tests: `python -m pytest src/dlamp/models/architectures/{glide_unet,unet,earth_3d_specifics}_test.py` (unittest-style, collect fine under pytest).
- `pangu_model_test.py` crashes at import: opens non-existent `config/model/dlamp_train.yaml` (config/model holds only dated yamls).
- The `tests/` dir (pyproject `testpaths=["tests"]`, `pythonpath=["src"]`) is 100% broken — all 6 files fail collection: wrong import paths (`dlamp.models.glide_unet` vs actual `dlamp.models.architectures.glide_unet`) and modules that no longer exist (`dlamp.diagnostics`, `dlamp.downloader`, `dlamp.regridder`). Bare `pytest` errors at collection.

## Commit Attribution

AI commits MUST include:

```test
Co-Authored-By: (the agent model's name and attribution byline)
```

## Agent skills

### Issue tracker

Issues and PRDs live as markdown files under `.scratch/<feature>/` in this repo (no external PR surface). See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles use their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as `Status:` lines in issue files. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root; ADRs (if any) go in `docs/adr/` — none exist yet. See `docs/agents/domain.md`.

## Conventions

- Style rules live in `GEMINI.md`: Google-style docstrings, PEP 8 (79 cols), `logging` over `print`, full type hints. Follow it for new code.
- Enforced tooling: pre-commit (`.pre-commit-config.yaml`) runs ruff `--fix` + ruff-format + basic hooks; `pyproject.toml` has `[tool.mypy]` strict and `[tool.ruff]`. Note: ruff `line-length` is 120 in the working-tree pyproject vs GEMINI.md's 79 — unresolved; write ~79 cols so both are satisfied.
- Makefile gates: `make check` is the blocking quality gate (ruff + radon) and must stay green. `make typecheck` (mypy strict) is deliberately **non-blocking**: ~812 pre-existing errors at HEAD (see `.scratch/dlamp-monorepo-refactor/issues/13-mypy-strict-debt.md`). Do not require `make typecheck` to pass for normal work; fix mypy only when explicitly scoped.
- Large assets (`assets/demo/`, `assets/town_shp/`, `assets/terrain_shp/`, `assets/constant_masks/`, `export/*.onnx`) are Git LFS per `.gitattributes` — run `git lfs pull` after clone.
- Commit messages are short imperative summaries (see git log).

Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:

- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
