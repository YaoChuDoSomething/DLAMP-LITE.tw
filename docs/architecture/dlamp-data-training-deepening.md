# DLAMP Data Pipeline & Training Workflow Deepening

Design decisions from the grilling session on perfecting the data
pipeline and model-training workflows. Each decision was recorded
against the `/codebase-design` vocabulary: **depth**, **interface**,
**seam**, **adapter**, **locality**, **leverage**.

## Decisions

### 1. Standardizer: identity-absent semantics

**Decision (Q1):** A `DataCompose` absent from `Standardization
Statistics` is an :term:`Unstandardized Variable` — legal, and treated as
*identity*. `standardize` and `destandardize` both pass the array through
unchanged. Never zeroed, never error.

**Before:** `standardize` returned `np.zeros_like` for absent stats while
`destandardize` skipped them — training silently fed zeros into the
model, inference quietly kept un-inverted values. Contradictory.

**After:** `standardize` returns the array unchanged for absent stats
(`src/dlamp/standardizer.py:61`). Training and inference agree.

**Why:** zeroing hides config bugs; the two directions disagree.

### 2. Standardizer ordering ownership

**Decision (Q3):** `Standardizer` holds no ordering knowledge — only
per-variable scaling (`standardize(dc_name, array)`). Layer/variable
ordering is owned by the caller (`DataManager`).

**Status:** partially applied. The ordering-independent `standardize`
path is done. `destandardize` still derives ordering from the data config
at construction; moving that fully out is deferred until the venv is
available to verify the 4 inference call sites.

### 3. Standardizer injection seam

**Decision (Q2, E1):** `Standardizer` is injected into `DataManager` /
`InferenceBase` and passed down to `CustomDataset`, rather than fetched
from a global singleton deep in the data-read path.

**Applied (backward-compatible):**

- `DataManager(..., standardizer=None)` — defaults to singleton
- `InferenceBase(..., standardizer=None)`
- `CustomDataset(..., standardizer=None)`
- `prediction_postprocess(..., standardizer=None)`

`get_standardizer()` remains as the fork-time builder for `DataLoader`
workers; it is no longer reached from inside `__getitem__`.

**Why:** accepts dependencies rather than creating them; the interface
becomes the test surface (a fake standardizer can be injected).

### 4. Split strategies extracted

**Decision (Q6):** The three train/valid/test split methods become
standalone strategy modules; `DatetimeManager` composes them.

**New:** `src/dlamp/managers/split_strategies.py` — `RandomSplit`,
`SequentialSplit`, `HalfMonthSplit`, and `get_split_strategy(name)`.

**After:** `DatetimeManager.random_split` delegates to the strategy;
adding a split method means writing one strategy module, not editing
`DatetimeManager`.

### 5. Data-source dispatch converged

**Decision (Q7):** The three scattered `match data_source` tables
(`gen_data`/`gen_path` in `file_util`, `sanity_check` in
`datetime_manager`) converge into one strategy per source.

**New:** `src/dlamp/data/source_strategy.py` — `NEO171RwrDataSource`,
`CwaRwrDataSource`, `OpEra5DataSource`, `OpE2sDataSource`, and
`get_data_source(name)`.

`file_util.gen_path`/`gen_data` and `datetime_manager.sanity_check` now
delegate. This eliminates the pre-existing drift (e.g. `RWRF_ERA5` only in
`sanity_check`, `OP_E2S` only in `gen_path`).

**Why:** a data source is now a single deep module — one place owns
path + sanity. Four adapters already exist, so the seam is real.

### Deferred

- **Q8 (`DataPipelineConfig` replacing `**kwargs`):** deferred — requires
  the venv to verify `train.py`, `export_onnx.py`, and the inference
  entrypoints after the signature change. The `**kwargs` pipe remains but
  is now bounded by the injected `standardizer` seam.

## Files touched

| File | Change |
| ------ | -------- |
| `src/dlamp/standardizer.py` | identity-absent `standardize` |
| `src/dlamp/managers/split_strategies.py` | new — split strategies |
| `src/dlamp/managers/datetime_manager.py` | delegate split + sanity to strategies |
| `src/dlamp/data/source_strategy.py` | new — data-source strategies |
| `src/dlamp/utils/file_util.py` | delegate `gen_path`/`gen_data` |
| `src/dlamp/managers/data_manager.py` | inject `standardizer` |
| `src/dlamp/datasets/custom_dataset.py` | accept injected `standardizer` |
| `src/dlamp/inference/inference_base.py` | inject `standardizer` |
| `src/dlamp/inference/infer_utils.py` | `prediction_postprocess` accepts `standardizer` |

## Verification

- `uvx ruff check src/dlamp/` — all checks passed
- `uvx radon cc ...` — new modules all complexity A
- `python3 -m py_compile` — all touched files compile
- Full pipeline runtime and arch tests require the project venv (not
  present in this environment); run `uv sync --extra dev` then
  `make check` before merging.
