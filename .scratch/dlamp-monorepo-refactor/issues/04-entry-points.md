# 04 Decide entry points and script disposition

Type: grilling
Status: resolved
Blocked by: 03

## Question

Decide the console entry points and what happens to every script the merge leaves behind:

- `train.py` / `predict.py` (DLAMP.tw) → `[project.scripts]` names, e.g. `dlamp-train`, `dlamp-predict`; what CLI surface they expose.
- dlamp-data's `main.py`, `dlamp_prep.py`, `scripts/` — folded into the `dlamp.data` CLI or separate entry points (e.g. `dlamp-data-*`)?
- Any scripts that stay as top-level runnable files vs become library entry points.
- The `dlamp.data` pipeline's command surface (tasks: download/convert/regrid/diagnostics) — does it get a unified CLI?

Grill one decision at a time; the answer records the approved entry-point table.

## Answer

Grilled Q1–Q4, confirmed by the user. Approved entry-point / script table:

**`[project.scripts]` entry points (Hydra passthrough, no wrapper flags):**
- `dlamp-train` ← `train.py` (configs `train_pangu` / `train_diffusion` via `--config-name`)
- `dlamp-predict` ← `predict.py` (inference → NetCDF → analysis pipeline)
- `dlamp-export-onnx` ← `src/export_onnx.py`
- `dlamp-infer-onnx` ← `src/inference_onnx.py`
- `dlamp-gen-const-masks` ← `src/generate_const_masks.py`
- `dlamp-unpack-tgz` ← `src/unzip_tgz.py`

**Top-level runnable files (kept, user choice):**
- `train.py` + `predict.py` at repo root — runnable as files (and mirrored as entry points)
- `data_prep.py` (renamed from `DLAMPreproc.py`) — repo-root thin wrapper → `dlamp.data.preproc`, config injected per 05-Q3
- `sfno_downscaling.py` (renamed from `SFNOPreproc.py`) — repo-root thin wrapper → `dlamp.data.preproc`, config injected

**Deleted:** `main.py` (uv stub); `updated.py` flagged to 09/11 (duplicates `diagnostic_functions.py`).

**Decisions:**
- Q1 — `dlamp-train`/`dlamp-predict` = Hydra passthrough; 4 `src/*.py` utilities → `dlamp-*` entry points.
- Q2 — the 2 dlamp-data runners stay **separate runnable files**, NOT `dlamp-data-*` entry points; **no unified task CLI** (the download/convert/regrid/diagnostics subcommand list came from the redirected-away `github/dlamp-data` layout and doesn't exist canonically). Stage toggles preserved as-is.
- Q3 — all invocations are either entry points or the 4 root runnable files; logic lives in importable package modules (`dlamp.inference`, `dlamp.analysis`, `dlamp.data.preproc`); no other top-level runnables.
- Q4 — root wrappers named `data_prep.py` (ERA5) + `sfno_downscaling.py` (SFNO), delegating to the package with config path injected (05-Q3); runner logic stays in `src/dlamp/data/preproc/` for testability.

**Revision (ticket 06-Q1):** `sfno_downscaling.py` **cancelled** — SFNO is excluded from the merge and stripped from dlamp.data history. Only `data_prep.py` (ERA5 runner) remains as the dlamp-data top-level runnable.
