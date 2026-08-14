# 05 Decide config and env wiring

Type: grilling
Status: resolved
Blocked by: 03

## Question

Decide how configuration and environment-driven paths carry into the monorepo:

- `src/const.py` env vars (`DLAMP_EXP_CODE`, `DLAMP_DATA_SOURCE`, `DLAMP_DATA_PATH`) — keep env-driven, and confirm the mismatch trap (exp code must match model version) stays enforced.
- Hydra config layout: `config/` stays top-level per the asset decision (Q10), but `src/dlamp/config/config.yaml` from the starter package — where does it land relative to top-level `config/`? One canonical config home or two?
- dlamp-data's `config/` and `test/fixtures/test_config.yaml` — how configs cross the `dlamp.data` boundary.
- Path references to top-level data dirs (`assets/`, `export/`, `outputs/`) — relative-to-repo-root vs env-injected; how a running monorepo locates them.

Grill one decision at a time; the answer records the approved config/env policy (an input to the design doc and ticket 09's env-fixtures section).

## Answer

Grilled Q1–Q4, all confirmed. Approved config/env policy:

**Q1 — env vars (keep, + validation).** `DLAMP_EXP_CODE` / `DLAMP_DATA_SOURCE` / `DLAMP_DATA_PATH` stay env-driven with current defaults. `dlamp.const` validates at import that `MODEL_CODE` has matching `config/data/rwrf_<code>.yaml` + `assets/standardization/z_score_3h_<code>.json`, raising a clear error instead of silently mis-applying standardization. Dead hardcode `DATA_SOURCE = "OP_E2S"` (src/const.py:11) removed.

**Q2 — one canonical config home.** Top-level `config/` only; starter's `src/dlamp/config/config.yaml` dies with the starter (ticket 03-B). All `[project.scripts]` entry points resolve top-level `config/` via **package-relative absolute path** (`Path(__file__).parents[N] / "config"`), never hand-written `../config` (breaks when package depth changes). dlamp-data yamls (`era5.yaml`, `sfno.yaml`, `dataDownloader.yaml`) land in `config/data/` alongside `rwrf_*` (no name collisions).

**Q3 — dlamp.data configs injected, not CWD-guessed.** Runners (`DLAMPreproc`/`SFNOPreproc` → entry points) resolve the yaml path package-relatively and pass it into `CDSDataDownloader`/`DataRegridder`/`SFNODataProcessor`; `./config/era5.yaml` CWD-literals removed. `test_config.yaml` doesn't exist canonically (ticket 02) — nothing crosses that boundary.

**Q4 — env-anchored absolute paths.** `dlamp.const` derives repo root from its own location (`Path(__file__).parents[2]` since `dlamp.const` lives at fixed depth `src/dlamp/const.py`), exports top-level dir constants (`ASSETS_DIR`, `CONFIG_DIR`, `EXPORT_DIR`, `GALLERY_DIR`, `OUTPUTS_DIR`, `CHECKPOINT_DIR`, plus derived `STANDARDIZATION_PATH`/`DATA_CONFIG_PATH`). All `./assets/...` literals across src/analysis/inference/visual and the hardcoded `base_dir` in dlamp-data's yamls → these constants. CWD-independence makes the AGENTS "run from repo root" rule unnecessary; `chdir: False` stays irrelevant. `DLAMP_DATA_PATH` default remains for the data-source pool.

Inputs to: design doc (ticket 12), testing spec env-fixtures (ticket 09), AGENTS.md rewrite (ticket 08).
