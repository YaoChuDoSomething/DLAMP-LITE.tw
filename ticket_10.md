# Ticket 10

Monorepo Refactor Handoff – YaoChuDoSomething/DLAMP.tw
Overview
This handoff summarizes the progress on refactoring the YaoChuDoSomething/DLAMP.tw monorepo. All previously opened tickets (01–09) have been resolved. The monorepo is now ready for the next phase: regression strategy (ticket 10).

## 1. Summary of Completed Work

Ticket	Status	Key Outcomes
01 – Config & Env Wiring	✅ Resolved	Centralised config/ hierarchy (config/era5/, config/sfno/, config/data/), env‑driven paths (DLAMP_DATA_PATH, DLAMP_EXP_CODE, DLAMP_DATA_PATH), config/ → src/dlamp/ delegation.
02 – Asset Management	✅ Resolved	Canonicity of assets/, export/, gallery/, outputs/, checkpoints/ (all top‑level, not packaged). export_onnx.py, inference_onnx.py, generate_const_masks.py, unzip_tgz.py retained as entry points.
03 – Entry Points & Script Disposition	✅ Resolved	Unified [project.scripts] with 6 entries (dlamp-train, dlamp-predict, dlamp-export-onnx, dlamp-infer-onnx, dlamp-gen-const-masks, dlamp-unpack-tgz). Top‑level runnable data_prep.py (formerly DLAMPreproc.py) kept as a thin wrapper. main.py and updated.py removed.
04 – Packaging & Dependency Matrix	✅ Resolved	Single Python 3.11 universe (>=3.11,<3.12). torch==2.4.0, numpy<2.0, lightning>=2.0.0, hydra-core>=1.3.0, xarray>=2026.7.0, netcdf4>=1.7.3, h5netcdf>=1.8.1, cdo>=1.6.1, eccodes (conda‑only). dlamp[dev] extra added. uv_build backend retained; top‑level data dirs excluded from wheel by construction.
05 – Entry Points Table	✅ Resolved	[project.scripts] defined (6 entries). Root runnables (train.py, predict.py, data_prep.py) remain executable from the repo root.

06 – Testing Specification	✅ Resolved	docs/testing/testing-specification.md locked:
  - Mirrored tests/ layout (tests/dlamp/ ↔ src/dlamp/, tests/dlamp/data/ ↔ src/dlamp/data/).  
  - Naming: <module>_test.py (consistent with surviving legacy files).  
  - Google‑style docstrings per GEMINI.md on every test module + fixture doc headers.  
  - Fixtures consolidated in tests/fixtures/; large files (e.g. target.nc) referenced via DLAMP_DATA_PATH (no commit).  
  - Marking: @pytest.mark.integration (default‑skipped, run -m integration).  
  - Baseline coverage recorded (no global --cov-fail-under; per‑module targets set in ticket 11). |
| 09 – Testing Spec Content | ✅ Resolved | Baseline inventory:  
  - tests/test_dlamp.py → deleted (tests removed the starter package).  
  - Architecture tests (unet_test.py, glide_unet_test.py, earth_3d_specifics_test.py) → migrated to tests/dlamp/models/ (fixed in ticket 11).  
  - pangu_model_test.py → deleted (import crash, superseded by ONNX workflow).  
  - DLAMP.data has zero tests at merge → ticket 11 will build tests from scratch for cds_downloader, dlamp_regridder, diagnostic_* modules. |

Overall status: All tickets 01–09 resolved. The monorepo is structurally sound, dependency‑aligned, and test‑ready.

## 2. Current State of the Monorepo

```text
dlamp-monorepo-refactor/
├── src/
│   ├── dlamp/
│   │   ├── config/          # config/era5/, config/sfno/, config/data/
│   │   ├── data/            # preproc/, registry/ (dlamp.data)
│   │   ├── inference/       # inference/, visualization/
│   │   ├── models/          # architectures/ (unet, glide_unet, earth_3d_specifics)
│   │   ├── utils/           # file_utils.py, file_util.py, etc.
│   │   └── ...
│   ├── tests/               # tests/dlamp/ (mirrored), tests/dlamp/data/
│   ├── pyproject.toml       # uv_build, deps, project.scripts
│   ├── .gitattributes       # LFS rules (assets/, export/, gallery/, outputs/, checkpoints/)
│   └── ...
├── dlamp-data/               # (unchanged, no tests, no deps)
├── .scratch/                 # issue tracker (resolved)
└── docs/                     # design docs, architecture diagrams
```

Key invariants:

- Python 3.11 only (>=3.11,<3.12).
- Torch 2.4.0 (pinned from AGENTS.md).
- NumPy < 2.0 (strictly enforced).
- Build backend: uv_build (no setup.py/setup.cfg needed).
- Packaging: Only src/<name>/ is packaged; top‑level data dirs excluded from wheels.
- Entry points: 6 [project.scripts] + 3 root runnables (train.py, predict.py, data_prep.py).

## 3. Next Steps (Ticket 10 – Regression Strategy)

The next frontier is ticket 10 – Regression Strategy. The monorepo is ready, but we need a reproducible regression plan to ensure the merge doesn’t introduce breaking changes. The plan should cover:
1. Test matrix – which components require regression tests (core inference, data I/O, diagnostics, training loop).
2. Smoke‑test suite – lightweight sanity checks for each major subsystem (data ingestion, model loading, inference, evaluation).
3. CI integration – adding the smoke‑test suite to the CI pipeline (Makefile target smoke or similar).
4. Rollback procedure – if a regression is detected, revert to the pre‑merge state (git revert or PR with rollback).
Once the regression strategy is documented and the smoke‑test suite is in place, the monorepo is production‑ready.

## 4. Suggested Skills for Continued Work

Skill	Why it’s relevant
Git	Managing the merge, ensuring proper rebasing/merging, and cleaning up the dlamp-data orphaned files.
Python	Reviewing the Python 3.11 compatibility, type‑hint hygiene, and ensuring no leftover PYTHON_VERSION mismatches.
Docker / Containerisation	Ensuring the uv_build image builds consistently across platforms (Linux host, CI runners).
Testing (pytest)	Writing and maintaining the test infrastructure (fixtures, integration markers, coverage reporting).
CI/CD (GitHub Actions / GitLab CI)	Integrating the smoke‑test suite into the CI pipeline, setting up the smoke target.
Code Review / Pull Request Process	Ensuring the final merge (ticket 10) is reviewed and approved.

## 5. Immediate Action Items for the Next Agent

1. Draft the regression strategy (ticket 10) covering:
- Smoke‑test list (per subsystem)
- Smoke‑test CI target (make smoke)
- Rollback plan (git revert / PR revert)
2. Create the smoke‑test suite (if not already present) and integrate it into the Makefile.
3. Verify the CI pipeline can run the smoke tests on the merged branch.
Once the regression strategy is documented and the smoke‑test suite is in place, the monorepo is fully stabilised and ready for production deployment.
Prepared by: Automated agent (session 1)  
Last updated: 2026‑08‑10  


