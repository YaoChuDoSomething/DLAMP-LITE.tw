# 06 Decide packaging and merged dependencies

Type: grilling
Status: resolved
Blocked by: 01, 02, 03

## Question

Decide the monorepo's `pyproject.toml` packaging and the merged dependency set:

- Build backend and tooling: setuptools vs hatchling; whether the current `uv`/`.venv` workflow (DLAMP.tw pins `torch==2.4.0`, `numpy<2.0`, Python 3.11) carries into the monorepo; Python version support and the 3.11-vs-3.12 tension with dlamp-data.
- Merged dependency matrix (from tickets 01 and 02): DLAMP.tw runtime deps (torch, lightning, hydra, onnxruntime, netcdf4/xarray?) vs dlamp-data deps (netcdf4, h5py, zarr, cdo, xarray) — dedupe versions, resolve conflicts, decide optional extras (e.g. `dlamp[data]` for the pipeline, `dlamp[dev]` for tests).
- `[project.scripts]` block per ticket 04's decision.
- LFS/pyproject wiring for non-packaged data dirs (exclude from wheel; `tool.setuptools` excludes).

Grill one decision at a time; the answer records the approved pyproject skeleton and dependency matrix.

## Answer

Grilled Q1–Q4, confirmed by user.

**Q1 — SFNO EXCLUDED, removed from dlamp.data history** (user: 排除：從歷史中移除). `git-filter-repo` strips `src/preproc/sfno_processor.py`, `SFNOPreproc.py`, `config/sfno.yaml`, `README.SFNO.md` from the dlamp.data history before the ticket-07 merge. earth2studio NOT in deps. Single universe: **py3.11 (`>=3.11,<3.12`) + torch==2.4.0 + numpy<2.0**; py3.12 tension gone. `dlamp[data]` extra cancelled. Revision to ticket 04: `sfno_downscaling.py` runner cancelled.

**Q2 — Dependency matrix (single set, deduped):** numpy `<2.0`, torch `==2.4.0`, lightning `>=2.0.0`, hydra-core `>=1.3.0`, xarray `>=2026.7.0`, netcdf4 `>=1.7.3`, h5netcdf `>=1.8.1`, cdsapi `>=0.7.7`, cdo `>=1.6.1`, eccodes (conda-only), pyproj (added, regrid), cfgrib, scipy, pandas (added, dlamp-data), pyyaml, cftime, matplotlib, dask, onnx, openvino, onnxruntime-gpu, etc. (rest of DLAMP.tw pyproject). Single `[project] dependencies`; **`dlamp[dev]` extra kept** (ruff/mypy/radon/pytest/pytest-cov/pre-commit). Build backend **`uv_build`** (already used in scaffolding). `cdo`/`eccodes` remain conda-forge install notes in README, not pyproject.

**Q3 — `[project.scripts]` block:**

```text
dlamp-train = "dlamp.train:main"
dlamp-predict = "dlamp.predict:main"
dlamp-export-onnx = "dlamp.export_onnx:main"
dlamp-infer-onnx = "dlamp.inference_onnx:main"
dlamp-gen-const-masks = "dlamp.generate_const_masks:main"
dlamp-unpack-tgz = "dlamp.unzip_tgz:main"
```

Root runnable `data_prep.py` stays out of the scripts block (04-Q3/Q4); SFNO entries cancelled. Verify Hydra `@hydra.main` main()s work as console entry points during execution.

**Q4 — LFS/packaging:** `uv_build` packages only `src/<name>/` — top-level `assets/ config/ export/ gallery/ outputs/ checkpoints/` excluded from wheel **by construction**; no `[tool.setuptools]`/exclude config needed. LFS via `.gitattributes` (ticket 07). Add explicit exclusions only if a test/CI later proves a leak.

Consumed by: pyproject.toml creation (execution), ticket 07 merge recipe (add SFNO strip step), design doc (12).
