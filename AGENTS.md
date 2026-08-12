# Agent Instructions

## Package Manager
No package manager. Plain Python 3.11 repo (`.python-version`); deps pinned in `requirements.txt` (`numpy<2.0`, `torch==2.4.0`). Not installed as a package — always run scripts from repo root, since all imports (`from src...`, `from analysis...`, `from inference...`) assume CWD = repo root. Hydra runs with `chdir: False`.

## Entrypoints
| Command | Purpose |
|---------|---------|
| `python train.py` | Train Pangu model (`train_pangu` config); use `python train.py --config-name train_diffusion` for the DDPM/Glide model |
| `python predict.py` | Full pipeline: inference → NetCDF forecasts → analysis plots (`predict` config, ONNX engine by default) |
| `python src/export_onnx.py` | Export a checkpoint to `export/<model>_model_<date>.onnx` |

All are `@hydra.main`; logs/artifacts go to `outputs/<YYYY-MM-DD>/<HH:MM:SS>/`.

## Runtime Config
- `src/const.py` reads env vars: `DLAMP_EXP_CODE` (default `20250627`), `DLAMP_DATA_SOURCE` (default `OP_ERA5`), `DLAMP_DATA_PATH` (default `/wk2/yaochu/CASE_DATA/Pool/`).
- `DLAMP_EXP_CODE` must match the model version (e.g. `20250729`): it selects `config/data/rwrf_<code>.yaml` and `assets/standardization/z_score_3h_<code>.json`. A mismatch silently applies the wrong standardization.
- Raw per-hour NetCDF input lives in `DLAMP_DATA_PATH`; filename pattern depends on `DLAMP_DATA_SOURCE` (`src/utils/file_util.py:gen_path`).
- Config is strict (`OmegaConf.set_struct(cfg, True)`): unknown or missing keys raise errors.

## Config Layout
`config/` splits into `data/`, `lightning/`, `model/`, `inference/`, `plot/`, wired together in `predict.yaml`, `train_pangu.yaml`, `train_diffusion.yaml`. Dated names (`rwrf_YYYYMMDD`) are model versions. `config/inference/*` picks the engine: `onnx` needs `export/*.onnx` (gitignored — export first), `ckpt` needs `checkpoints/*.ckpt` (gitignored).

## Models
Architectures live in `src/models/architectures/`, lightning modules in `src/models/lightning_modules/`, builders in `src/models/builders/`. Dispatch is by `cfg.model.model_name` (`Pangu` → `PanguBuilder`, `Glide` → `GlideBuilder`).

## Tests
`src/models/architectures/*_test.py` are `unittest`, run via `python -m src.models.architectures.<name>_test`. They are stale: `pangu_model_test.py` opens a non-existent `config/model/dlamp_train.yaml` and crashes at import. Do not assume tests pass or match current configs.

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent model's name and attribution byline)
```

## Agent skills

### Issue tracker
Issues and PRDs live as markdown files under `.scratch/<feature>/` in this repo (no external PR surface). See `docs/agents/issue-tracker.md`.

### Triage labels
The five canonical roles use their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), recorded as `Status:` lines in issue files. See `docs/agents/triage-labels.md`.

### Domain docs
Single-context: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Conventions
- Style rules live in `GEMINI.md`: Google-style docstrings, PEP 8 (79 cols), `logging` over `print`, full type hints, isort/flake8/pydocstyle-clean. Follow it for new code.
- Large assets (`assets/**/*.npy`, demo gifs, `export/*.onnx`) are Git LFS — run `git lfs pull` after clone.
- Commit messages are short imperative summaries (see git log).
