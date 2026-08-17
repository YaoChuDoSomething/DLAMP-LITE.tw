# 03 Decide target src/dlamp submodule tree

Type: grilling
Status: resolved
Blocked by: 01, 02

## Question

Decide the exact target `src/dlamp/` directory tree for the monorepo, and approve it with the human. Work through each bucket:

- **DLAMP.tw legacy modules**: where each of `analysis/`, `inference/`, `visual/`, `src/{models,datasets,utils,managers,debug}` lands under `src/dlamp/` (e.g. `src/dlamp/{analysis,inference,visual,models,datasets,utils,managers,debug}`), preserving their internal structure.
- **The starter `src/dlamp/` package** from DLAMP.tw (`model.py`, `datamodule.py`, `lightning_module.py`, `train.py`, `config/config.yaml`) — how it merges with the folded-in modules (name collisions? `src/dlamp/config` vs top-level `config/`?).
- **Disposition of the nested `externals/dlamp-data` git repo** (an old, untracked copy of the data pipeline discovered by ticket 01): delete, convert to submodule, vendor, or ignore — and how it relates to the canonical DLAMP.data content folded into `dlamp.data.*`.
- **DLAMP.data components**: confirm the `dlamp.data.<component>` mapping for `src/{core,dlamp_data,io,registry,tasks,tools}` and where `definition/` specs land (`dlamp.data.definition` or `docs/`). Decide what happens to the redundant `src/dlamp/data` dir already present in dlamp-data.
- **Final tree diagram**: produce and lock the full annotated tree (top-level dirs + `src/dlamp/` + `src/dlamp/data/`), which tickets 04/05/06/09 consume.

Grill one branch at a time; the decision is the approved tree diagram, recorded in the answer.

## Answer

Grilled all 5 branches, confirmed by the user. Approved tree:

```text
dlamp-monorepo/
├── src/dlamp/                      # package `dlamp` (DLAMP.tw side)
│   ├── const.py                    # dlamp.const (hub, from src/const.py)
│   ├── standardization.py          # dlamp.standardization
│   ├── analysis/                   # forecast_saver, prediction, plotter, video_creator...
│   ├── inference/                  # inference_base, batch_inference_{ckpt,onnx}, infer_utils
│   ├── visual/                     # viz_*.py, tw_background
│   ├── models/                     # architectures, builders, callbacks, diffusion_process, lightning_modules, loss_fn, model_utils
│   ├── datasets/                   # custom_dataset
│   ├── managers/                   # data_manager, datetime_manager
│   ├── utils/                      # file_util, gen_path...
│   └── debug/                      # boundary_plots
├── src/dlamp/data/                 # package `dlamp.data` (DLAMP.data side)
│   ├── preproc/                    # cds_downloader, dlamp_regridder, sfno_processor
│   └── registry/                   # diagnostic_functions, diagnostic_registry
├── config/                         # UN-PACKAGED data dir (Hydra configs)
├── assets/                         # UN-PACKAGED data dir (LFS + target.nc)
├── export/                         # UN-PACKAGED data dir (LFS *.onnx)
├── gallery/                        # UN-PACKAGED output dir
├── outputs/                        # UN-PACKAGED runtime dir (Hydra logs)
├── docs/                           # CONTEXT.md, adr/, design/, testing/
├── tests/
├── GEMINI.md / AGENTS.md / Makefile / .pre-commit-config.yaml
├── pyproject.toml                  # merged deps (ticket 06)
└── .gitattributes                  # merged LFS rules (ticket 07)
```

Branch decisions:

- **A** — 8 legacy dirs fold in preserving structure (`dlamp.{analysis,inference,visual,models,datasets,utils,managers,debug}`); `src/const.py`→`dlamp.const`, `src/standardization.py`→`dlamp.standardization`; 4 standalone scripts (`export_onnx`, `generate_const_masks`, `inference_onnx`, `unzip_tgz`) → `[project.scripts]` (ticket 04).
- **B** — starter `src/dlamp/` toy-MLP scaffold (`model/datamodule/lightning_module/train/config`) **deleted** (no runtime deps on it); its `tests/` disposition → ticket 11.
- **C** — nested `externals/dlamp-data` (untracked) **deleted** from DLAMP.tw at archiving; canonical pipeline enters the monorepo via ticket 07's merged history, not as a copy/submodule.
- **D** — canonical dlamp.data = **`dlamp.data.preproc`** + **`dlamp.data.registry`** only. No `core/io/tasks/tools`, no `definition/`, no redundant `src/dlamp/data` — those were `github/dlamp-data`'s (redirected). Runners `DLAMPreproc.py`/`SFNOPreproc.py` → entry points (ticket 04); `config/{era5,sfno,dataDownloader}.yaml` → top-level `config/`; `assets/target.nc` → top-level `assets/` (LFS/regeneration territory → ticket 09); `updated.py` (duplicates `diagnostic_functions.py`) → **flagged to 09/11 for reconciliation**; `main.py` (uv stub) → delete.
- **E** — tree locked as above. `lightning_logs/` → runtime, ignored, not carried. **Correction to ticket 08's provisional note**: DLAMP.tw assets land at top-level `assets/`, not `src/dlamp/assets/`.

Consumed by tickets 04 (entry points), 05 (config/env wiring), 06 (deps), 09 (testing spec).
