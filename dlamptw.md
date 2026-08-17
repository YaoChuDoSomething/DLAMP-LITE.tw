This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: docs/architecture/codebase-review-src-dlamp.md, src/dlamp/, config/, train.py, predict.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
config/
  data/
    rwrf_202409.yaml
    rwrf_202412.yaml
    rwrf_202501.yaml
    rwrf_202502.yaml
    rwrf_20250310.yaml
    rwrf_20250611.yaml
    rwrf_20250627.yaml
    rwrf_20250729.yaml
  inference/
    pangu_rwrf_ckpt.yaml
    pangu_rwrf_onnx.yaml
  lightning/
    diffusion_rwrf_202409.yaml
    pangu_rwrf_202409.yaml
    pangu_rwrf_202501.yaml
    pangu_rwrf_202502.yaml
    pangu_rwrf_20250310.yaml
    pangu_rwrf_20250611.yaml
    pangu_rwrf_20250627.yaml
    pangu_rwrf_20250729.yaml
  model/
    diffusion_rwrf_202409.yaml
    pangu_rwrf_202409.yaml
    pangu_rwrf_202412.yaml
    pangu_rwrf_202501.yaml
    pangu_rwrf_202502.yaml
    pangu_rwrf_20250310.yaml
    pangu_rwrf_20250611.yaml
    pangu_rwrf_20250627.yaml
    pangu_rwrf_20250729.yaml
  plot/
    pangu_rwrf.yaml
  data_prep.yaml
  data_stats.yaml
  predict_dscale.yaml
  predict_feedback.yaml
  predict.yaml
  train_diffusion_radar.yaml
  train_diffusion.yaml
  train_pangu.yaml
docs/
  architecture/
    codebase-review-src-dlamp.md
src/
  dlamp/
    analysis/
      __init__.py
      data_manager.py
      forecast_saver.py
      netcdf_meta.py
      plot_meta.py
      plotter.py
      prediction.py
      video_creator.py
    data/
      preproc/
        __init__.py
        cds_downloader.py
        dlamp_regridder.py
      registry/
        __init__.py
        diagnostic_functions.py
        diagnostic_registry.py
      __init__.py
      source_strategy.py
    datasets/
      __init__.py
      custom_dataset.py
    debug/
      boundary_plots.py
    inference/
      __init__.py
      batch_inference_ckpt.py
      batch_inference_onnx.py
      infer_utils.py
      inference_base.py
    managers/
      __init__.py
      data_manager.py
      datetime_manager.py
      split_strategies.py
    models/
      architectures/
        __init__.py
        drop_path.py
        earth_3d_specifics_test.py
        earth_3d_specifics.py
        glide_unet_test.py
        glide_unet.py
        multilayer_perceptron.py
        pangu_model_test.py
        pangu_model.py
        smoothing.py
        unet_test.py
        unet.py
      builders/
        __init__.py
        base_builder.py
        glide_builder.py
        pangu_builder.py
      callbacks/
        __init__.py
        log_diffusion_pred_samples_callback.py
        log_prediction_samples_callback.py
      diffusion_process/
        __init__.py
        ddim_process.py
        ddpm_process.py
      lightning_modules/
        __init__.py
        diffusion_lightning_module.py
        pangu_lightning_module.py
      loss_fn/
        __init__.py
        crps.py
        euclidean.py
      __init__.py
      model_utils.py
    utils/
      __init__.py
      data_compose.py
      data_generator.py
      data_type.py
      file_util.py
      test_data_type.py
      time_util.py
    visual/
      __init__.py
      tw_background.py
      viz_gph.py
      viz_mixing_ratio.py
      viz_omega.py
      viz_pressure.py
      viz_radar.py
      viz_swdown.py
      viz_temp.py
      viz_vor.py
      viz_wind.py
    workflows/
      __init__.py
      data_prep_runner.py
      data_stats_runner.py
      predict_dscale_runner.py
      predict_feedback_runner.py
    __init__.py
    const.py
    export_onnx.py
    generate_const_masks.py
    inference_onnx.py
    py.typed
    runtime_config.py
    standardizer.py
    train.py
    unzip_tgz.py
predict.py
train.py
```

# Files

## File: docs/architecture/codebase-review-src-dlamp.md
```markdown
# Codebase Review — `src/dlamp/`

**Scope:** full-package review of `src/dlamp/` (75 `.py` files, ~12,326 LOC), branch
`ai-ml-workflow-spec`, HEAD `f24ec7b` (incl. uncommitted working-tree changes).
**Method:** two independent axes — **Standards** (repo-documented rules + Fowler smell
baseline) and **Spec** (originating requirement docs). No diff; entire codebase reviewed.
**Standards sources:** `AGENTS.md`, `GEMINI.md`, `CONTEXT.md` (incl. Avoid List),
`docs/agents/domain.md`, `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`.
**Spec sources:** `docs/ai-ml/workflow-spec.md`, `docs/architecture/{dlamp-output-variable-registry,data-type-rewrite-consumers,dlamp-data-training-deepening,mlwp-pipeline-architecture}.md`,
`CONTEXT.md`, `.agents/plans/ai-ml-workflow-spec/`, `.scratch/…/13-mypy-strict-debt.md`.

Tooling-enforced items are excluded (ruff/radon via `make check`, mypy-strict debt tracked
in `.scratch/…/13-mypy-strict-debt.md`). Key claims re-verified against source.

---

## Standards

### Hard — documented-standard violations

| # | Violation | Standard | Evidence |
|---|---|---|---|
| S1 | Test files inside `src/` | CONTEXT.md Avoid List: "Test files must live under `tests/`, never under `src/dlamp/`" | `src/dlamp/utils/test_data_type.py`, `src/dlamp/models/architectures/{earth_3d_specifics,glide_unet,pangu_model,unet}_test.py`. `pangu_model_test.py:12` opens stale `config/model/dlamp_train.yaml`; `glide_unet_test.py:20,26,28` / `unet_test.py:21-22` call `.cuda()` unconditionally |
| S2 | `print` instead of `logging` | GEMINI.md "Logging: standard `logging` (no `print`)" | `analysis/prediction.py:156` (`print("cfg = ", cfg)` in the production workflow); `data/preproc/dlamp_regridder.py` (extensive `[REGRID]/[INFO]/[WARN]/[DONE]/[ERROR]` prints); `data/preproc/cds_downloader.py`; `generate_const_masks.py:65,95-97,105,116,142`; `unzip_tgz.py:61`; `inference_onnx.py:35,67,68` |
| S3 | Missing/misplaced module docstrings | GEMINI.md "Each file starts with a one-paragraph summary" | ~25 files start with `from __future__`/imports: `runtime_config.py`, `standardizer.py`, `utils/{data_type,data_compose,data_generator,file_util,time_util}.py`, `datasets/custom_dataset.py`, `managers/*.py`, `models/model_utils.py`, `pangu_model.py`, `glide_unet.py`, `ddpm_process.py`, both callbacks, both lightning modules, `data/registry/*`, `loss_fn/{crps,euclidean}.py`, `export_onnx.py`, `unzip_tgz.py`, `visual/tw_background.py`, all 8 `visual/viz_*.py`, `debug/boundary_plots.py`, all builders. Misplaced (after imports): `inference_onnx.py:14-16`, `unet.py:8-10`, `drop_path.py:3-5` |
| S4 | Missing type hints on public/private callables | GEMINI.md "complete type annotations" | `cds_downloader.py`, `dlamp_regridder.py`, `diagnostic_registry.load_diagnostics`, `custom_dataset.__getitem__/__len__`, `ddpm_process` (entire class untyped), `base_builder.__init__`, all `visual/viz_*` methods, `model_utils.RunningAverage`, `debug/boundary_plots.py` |
| S5 | Broad `except` / non-specific exceptions | GEMINI.md DoD "No broad `except:`" | `file_util.py:129`, `unzip_tgz.py:38`, `cds_downloader.py`, `dlamp_regridder.py` |
| S6 | `logging.basicConfig` from library code | GEMINI.md (side-effect-free modules) | `standardizer.py:124` (inside a method); `unzip_tgz.py:7-11` import-time side effect writing `unzip.log` into the source dir |
| S7 | Value-like dataclass not frozen | GEMINI.md "frozen=True for value-like objects" | `data_compose.py:15` `DataCompose` (pydantic, mutable) |

### Judgement — baseline smells + latent bugs

- **Dead code (Speculative Generality / unused):** `loss_fn/{crps,euclidean}.py` unreferenced;
  `ddpm_process.py:77,90,94` cosine/quadratic/sigmoid beta schedules (only `linear` used);
  `runtime_config.py:100` `get_runtime_config_error()` stub + `:78` `standardization_json_path` alias;
  `export_onnx.py:62` `save_single_onnx`; `plotter.py:93-94` dispatch keys `temperature`/`column_max_qt`;
  `pangu_lightning_module.py:75-76` weighted-loss branch (builders always pass `None`);
  `generate_const_masks.py:16,68` `gen_TW_*` unused by `main()`.
- **Latent bugs (crash/corruption risk, one-line fixes):**
  - `pangu_lightning_module.py:20-26` — `upper_var_weights_tensor` unbound if weights provided → `NameError`.
  - `time_util.py:35` `if hour:` — `hour==0` falsy → whole-day loop skipped; same zero-falsy at `source_strategy.py:82`.
  - `diagnostic_functions.py` `diag_z_p` RWRF case leaves `nc_key` unbound → `UnboundLocalError`.
  - `debug/boundary_plots.py:68,254` `f"...{{dt...}}..."` literal braces — `dt` never interpolated.
  - `viz_swdown.py:66` GT loop calls `_plot_pressure` (copy-paste); `:108` `/100` "pa→hpa" unit bug.
  - `ddpm_process.py:53,60` `if t == 0` / `if beta_t_hat != 0` on tensors — tensor truthiness.
- **Duplicated Code:** `pangu_builder.build_trainer` vs `glide_builder.build_trainer` (~40 lines incl. wandb project names); 8 `visual/viz_*` classes share `plot_1xn/plot_1x1/plot_mxn`+divider/colorbar boilerplate; `batch_inference_{ckpt,onnx}.py` `infer()` near-identical; `forecast_saver.py:129` vs `:271` Qt `/1000`; `inference_base.py:272-277` vs `:293-298` mask recompute.
- **Repeated Switches / stringly-typed dispatch:** `dlamp_regridder.py` ~20 diag fns repeat the ERA5/ERA5_r/RWRF `match`; `inference_base._boundary_swapping` method-string dispatch + `if method == "None"` sentinel; `standardizer.py:56,111` `"Qt@Hpa" in ...` substring checks.
- **Feature Envy / private reach-in:** `plotter.py` calls `manager._get_wind_components`; `inference_base.py:99,215-216` `data_manager._predict_dataset._init_time_list` / `_get_variables_from_dt`; `managers/data_manager.py` `image_shape` reads `data_gnrt._img_shp`; `log_prediction_samples_callback.py:42-45`; `data_stats_runner.py:88` `standardizer._config`.
- **Mysterious Name:** `glide_builder.py:53,55,60` `regressoin_ckpt_path`; `data_compose.py:49` `retrive_var_level_from_string`; `datetime_manager.py:21` `BC = "[Bottleneck Check]"`; `diffusion_lightning_module.py:43,51` `condtion`/`noist`.
- **Doc/annotation mismatches (docstring lies):** `data_compose.py:81` `dict[str,str]` vs real `dict[str,list[str]]` + "dictoinary"; `inference_base.py:63` `list[datetime|None]` vs `list[datetime]|None`; `infer_utils.py:19,28` `dict[int,str]` vs real `dict[str,int]`; `time_util.py:56,67` "three days" wording ignores `n_days`; `data_generator.py:86` `(c h w)→h w` vs code `(c h) w`; `batch_inference_ckpt.py:47` "ONNX runtime" copy-paste; `diffusion_lightning_module.py:109` "CRPS loss" but MSE; `inference_base.py:133` doc lists `fft_tukey_linear_boundary` branch that doesn't exist.
- **Artifacts/mixed-language:** `plotter.py:253` Chinese `# --- 新增...`; `create_cross_section_figure` docstring in Traditional Chinese; `generate_const_masks.py:33-38` giant commented data table; `forecast_saver.py:113` "prompt states variable = 73"; `# NEW:` comments.
- **Middle Man:** `file_util.py:14` `_get_config()`.
- **Magic numbers:** `plotter.py:545` `skip=11`; `file_util.py:107` SST mean `298.6...`; `export_onnx.py:45` `best_ckpt.split("_")[1]`.

Reference-good files (match GEMINI.md): `workflows/*`, `analysis/{data_manager,prediction,video_creator,netcdf_meta}.py`, `data/source_strategy.py`.

---

## Spec

Spec sources: `docs/ai-ml/workflow-spec.md` §3 (Local Cutting table + mechanism),
`docs/architecture/dlamp-output-variable-registry.md` (canonical CF registry),
`docs/architecture/data-type-rewrite-consumers.md` (migration), `docs/architecture/dlamp-data-training-deepening.md` (Q1–Q8), `docs/architecture/mlwp-pipeline-architecture.md` §6, `CONTEXT.md`.

### (a) Missing / partial requirements

- **§3 data pipeline** — spec: "`dlamp.data.ingestion` → `dlamp.data.preproc` → `dlamp.data.registry`". `src/dlamp/data/` has `preproc/` and `registry/` but **no `ingestion/`**.
- **§3 workflows** — spec: "`dlamp.workflows.train` → `dlamp.workflows.eval` → `dlamp.workflows.execute`" + "unified experiment tracking". `workflows/` has only `data_prep/data_stats/predict_dscale/predict_feedback` runners; no train/eval/execute, no tracking layer.
- **§3 inference** — spec: "`dlamp.inference.engine` → `dlamp.inference.serving`" + "unified `InferenceEngine` interface". Only abstract `InferenceBase` exists; the `infer()` loops in `batch_inference_onnx.py:29` / `batch_inference_ckpt.py:45` remain duplicated.
- **Registry gaps** — `UM_100m`/`VM_100m` (nc_key `U_100m`/`V_100m`, in registry) have **no `DataType` member**; only `Level.Meter100` exists (`data_type.py:63-66`).
- **Q7 partial** — spec: "`sanity_check` … converge into one strategy per source". `datetime_manager.py:209-223` still branches `isinstance(source, NEO171RwrDataSource)` and re-implements the per-file loop; the strategy `.sanity_check()` methods (`source_strategy.py:59,85,110`) are never called.
- **Q3 partial (documented)** — `standardizer.py:36,78-96` still derives variable ordering from config at construction; deepening doc admits this is deferred.

### (b) Not asked for (scope creep)

- `feedback_iters` key in `predict_feedback.yaml` / `pangu_rwrf_*.yaml` / `predict_feedback_runner.py:64-68` is "informational only" — never read by any engine.

### (c) Implemented but wrong

- **`prediction.py:107`** `DataCompose.from_config({"Lat":[…], "Lon":[…], "MASK":["NoRule"]})` → `DataType["MASK"]` raises `KeyError` (member renamed to `MASKLAND`). Kills `PredictionRunner.run()` and all three predict entrypoints. Missing from the consumer-migration table.
- **`standardizer.py:80,91-92`** `_destandardize` inits `new_array = np.zeros_like(array)` and `continue`s on absent stats → outputs zeros, not identity. Q1 spec: "`standardize` and `destandardize` both pass the array through unchanged. Never zeroed, never error." Reintroduces exactly the train/inference disagreement Q1 fixed (the `standardize` side is identity-correct; the inverse is not).
- **`viz_wind.py:143-144`** uses deleted `DataType.U`/`DataType.V` (renamed `U10m`/`V10m`) → `AttributeError`. Missing from the migration table.
- **Enum/registry drift** — `data_type.py:63-66,78` uses names `T2m/U10m/V10m`, shortnames `T/U/V`; registry mandates `TH_2m/UM_10m/VM_10m`, shortnames `TH/UM/VM`, plus `MASKLAND` shortname `LANDMASK` (enum uses `MASKLAND`). `nc_key`s match. Registry is canonical per spec.
- **`diagnostic_functions.py:301-322`** `diag_QTOTAL_p` still sums `QCLOUD+QRAIN+QICE+QSNOW+QGRAUP`; registry: "Qt … never derived from other variables." Read path fixed (`file_util.py:101-104`), but the deriving diagnostic remains live in the plugin.
- **Dead code confirmed by spec:** `plotter.py:578-611` `create_cross_section_figure` reads `self.manager.levels` (nonexistent; only `pressure_levels`) — exactly the bug `mlwp-pipeline-architecture.md` §6 flags.

---

## Improvement plan (ranked)

1. **Unblock the predict pipeline** — `prediction.py:107` `"MASK"`→`"MASKLAND"`. Highest severity (breaks all three predict entrypoints).
2. **Restore Q1 identity semantics in `_destandardize`** — copy-through on absent stats instead of `zeros_like`+`continue`.
3. **Fix `viz_wind.py` `U/V`→`U10m/V10m`** and add missing `UM_100m`/`VM_100m` members (or re-document registry). Then reconcile enum names/shortnames vs the registry doc (decide which is canonical).
4. **Remove in-`src` tests** (`CONTEXT.md`) — move the 4 architecture tests under `tests/`, delete `test_data_type.py` as redundant.
5. **Kill the spec-mandated dead code / dedupe:** delete `loss_fn/`, unused beta schedules, `save_single_onnx`, `get_runtime_config_error`, weighted-loss branch; merge the two `build_trainer`s and the two `infer()` loops into a shared `InferenceEngine`.
6. **`print`→`logging`** across `prediction.py`, `dlamp_regridder.py`, `cds_downloader.py`, `generate_const_masks.py`, `unzip_tgz.py`, `inference_onnx.py`.
7. **Fix the latent one-line bugs:** `pangu_lightning_module` unbound var, `time_util`/`source_strategy` zero-falsy `if hour`, `diag_z_p` `UnboundLocalError`, `boundary_plots` literal braces, `viz_swdown` copy-paste + unit bug.
8. **Docstring/annotation debt:** module docstrings for ~25 files; fix the 10 doc-vs-code mismatches.
9. **Publicize reach-ins:** expose `get_wind_components`, `image_shape`, `init_time_list`, `_get_variables_from_dt` as public API; stop `standardizer._config` / `_get_wind_components` reach-ins.
10. **Resume deferred §3 refactors** (per workflow-spec): `data.ingestion`, `workflows.{train,eval,execute}`, `inference.{engine,serving}`.

**One-line summary:** Standards — 7 hard violations + ~20 judgement smells/latent bugs, worst = tests-in-`src` + `print`-in-production; Spec — 5 missing/partial + 6 wrong implementations, worst = `prediction.py` `"MASK"` `KeyError` (kills predict) + `_destandardize` zeroing (breaks Q1).
```

## File: src/dlamp/data/source_strategy.py
```python
"""Data-source strategies: one module per source owns path and sanity logic.

Converges the three previously scattered ``match data_source`` dispatch
tables (``gen_data``/``gen_path`` in ``file_util`` and ``sanity_check`` in
``datetime_manager``) into a single strategy per data source. Adding a new
data source means writing one strategy module, not editing three sites.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

from ..runtime_config import RuntimeConfig
from ..utils.data_compose import DataCompose


class DataSourceStrategy(Protocol):
    """Resolve paths and sanity checks for one data source."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        """Return the file path for ``target_time`` under this source."""

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        """Return True if the data for ``dt`` is usable (files exist)."""


class NEO171RwrDataSource(DataSourceStrategy):
    """Binary ``.raw`` radar files stored per-hour directories on neo171."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        if data_compose is None:
            raise ValueError("data_compose is required for NEO171_RWRF")
        return (
            config.data_path
            / f"rwf_{target_time.strftime('%Y%m')}"
            / f"{target_time.strftime('%Y%m%d%H%M')}0000"
            / data_compose.basename
        )

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        if data_compose is None:
            return gen_path(dt).exists()
        return gen_path(dt, data_compose).exists()


class CwaRwrDataSource(DataSourceStrategy):
    """WRF-interpolated NetCDF files on the CWA HPC."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        predict_dt = target_time + timedelta(hours=use_Kth_hour_pred) if use_Kth_hour_pred else target_time
        return config.data_path / f"wrfout_d01_{predict_dt.strftime('%Y-%m-%d_%H')}_interp"

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        return gen_path(dt).exists()


class OpEra5DataSource(DataSourceStrategy):
    """ERA5-derived NetCDF files (OP_ERA5 naming)."""

    _filename = "e5dlamp_{ts}.nc"

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        return config.data_path / self._filename.format(ts=target_time.strftime("%Y%m%d_%H%M"))

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        return gen_path(dt).exists()


class OpE2sDataSource(OpEra5DataSource):
    """E2S-derived sfno NetCDF files."""

    _filename = "e2s_sfno_dlamp_{ts}.nc"


def get_data_source(data_source: str) -> DataSourceStrategy:
    """Return the strategy registered for ``data_source``.

    Args:
        data_source: One of ``"NEO171_RWRF"``, ``"CWA_RWRF"``,
            ``"OP_ERA5"``, ``"OP_E2S"``.

    Returns:
        The matching ``DataSourceStrategy``.

    Raises:
        ValueError: If ``data_source`` is not registered.
    """
    strategies: dict[str, DataSourceStrategy] = {
        "NEO171_RWRF": NEO171RwrDataSource(),
        "CWA_RWRF": CwaRwrDataSource(),
        "OP_ERA5": OpEra5DataSource(),
        "OP_E2S": OpE2sDataSource(),
    }
    try:
        return strategies[data_source]
    except KeyError as exc:
        raise ValueError(
            f"Unknown data source: '{data_source}'. "
            f"Available: {', '.join(sorted(strategies))}"
        ) from exc
```

## File: src/dlamp/managers/split_strategies.py
```python
"""Train/valid/test split strategies for the DatetimeManager.

Each strategy owns one way of partitioning an ordered list of initial
times into three disjoint sets. ``DatetimeManager`` composes the chosen
strategy rather than inlining the split logic, so adding a new split
method means writing one strategy module, not editing ``DatetimeManager``.
"""

from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime
from typing import Protocol

import numpy as np


class TimeSplitStrategy(Protocol):
    """Split an ordered list of initial times into train/valid/test.

    Strategies are stateless and return three disjoint set instances.
    """

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        """Return ``(train_time, valid_time, test_time)``."""

    def __call__(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        return self.split(time_list, ratios)


class RandomSplit(TimeSplitStrategy):
    """Shuffle the whole range and split by normalized ratios."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()
        ratios = ratios * len(time_list)

        shuffled = time_list.copy()
        random.seed(1000)
        random.shuffle(shuffled)

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        for category, category_idx in {"train": 0, "valid": 1, "test": 2}.items():
            start_idx = int(np.sum(ratios[:category_idx]))
            end_idx = int(np.sum(ratios[: category_idx + 1]))
            target = {"train": train_time, "valid": valid_time, "test": test_time}[category]
            target.update(shuffled[start_idx:end_idx])
        return train_time, valid_time, test_time


class SequentialSplit(TimeSplitStrategy):
    """Assign times round-robin in fixed chunks of ``max(ratios) * 10``."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()
        ratios = np.round(ratios * 10).astype(int)
        chunk_size = int(ratios.sum())

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        time_array = np.array(time_list)
        for i in range(chunk_size):
            chunk = time_array[i::chunk_size]
            if i < ratios[0]:
                train_time.update(chunk)
            elif i >= chunk_size - ratios[-1]:
                test_time.update(chunk)
            else:
                valid_time.update(chunk)
        return train_time, valid_time, test_time


class HalfMonthSplit(TimeSplitStrategy):
    """Group times by calendar half-month, shuffle groups, then assign."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()

        groups: dict[str, list[datetime]] = defaultdict(list)
        for dt in time_list:
            half = "1st_half" if dt.day <= 15 else "2nd_half"
            groups[f"{dt.strftime('%b')}_{half}"].append(dt)

        group_list = list(groups.values())
        random.seed(1000)
        random.shuffle(group_list)

        num_groups = len(group_list)
        train_end = int(num_groups * ratios[0])
        valid_end = int(num_groups * (ratios[0] + ratios[1]))

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        for i, group in enumerate(group_list):
            if i < train_end:
                train_time.update(group)
            elif i < valid_end:
                valid_time.update(group)
            else:
                test_time.update(group)
        return train_time, valid_time, test_time


def get_split_strategy(split_method: str) -> TimeSplitStrategy:
    """Return the split strategy registered for ``split_method``.

    Args:
        split_method: One of ``"random"``, ``"sequential"``, ``"half_month"``.

    Returns:
        The matching ``TimeSplitStrategy`` instance.

    Raises:
        ValueError: If ``split_method`` is not registered.
    """
    strategies: dict[str, TimeSplitStrategy] = {
        "random": RandomSplit(),
        "sequential": SequentialSplit(),
        "half_month": HalfMonthSplit(),
    }
    try:
        return strategies[split_method]
    except KeyError as exc:
        raise ValueError(
            f"Invalid split_method '{split_method}'. "
            f"Available: {', '.join(sorted(strategies))}"
        ) from exc
```

## File: config/lightning/pangu_rwrf_20250310.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 1
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 1e-4
    weight_decay: 1e-5
lr_schedule:
  name: linear_decay
  args:
    warmup_epochs: 30
    last_epoch: -1
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: null
max_steps: null
min_steps: 1e5 # 100k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
```

## File: config/model/pangu_rwrf_20250310.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 3
segmented_smooth_boundary_width: null
# earth layer
depths: [4, 4, 6]
# earth block
max_drop_path_ratio: 0.3
# earth attn 3d
heads: [8, 16, 32]
embed_dim: 352
dropout_rate: 0
window_size: [4, 7, 7]
```

## File: config/data_prep.yaml
```yaml
hydra:
  run:
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

# Method used to generate constant masks.
# Options:
#   extract_from_nc    — from existing WRF NetCDF (requires DLAMP_DATA_PATH)
#   gen_tw_cn_terrain  — from GeoTIFF raster (assets/terrain_shp/gt30e100n40.tif)
#   gen_tw_only_terrain — from shapefile    (assets/terrain_shp/GIS_terrain.shp)
data_prep:
  method: extract_from_nc

defaults:
  - data: rwrf_20250729
  - _self_
  - override hydra/job_logging: default
```

## File: config/data_stats.yaml
```yaml
hydra:
  run:
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

# Sampling window for z-score statistics computation.
# All four parameters are exposed so they can be overridden via CLI:
#   python data_stats.py stats.start_time="2020-01-01 00:00"
stats:
  start_time: "2021-01-01 00:00"   # inclusive, format: YYYY-MM-DD HH:MM
  end_time: "2022-12-31 00:00"     # inclusive
  sample_size: 100                  # random pixels sampled per grid cell
  num_criteria: 1000                # min samples to keep a variable's stats

defaults:
  - data: rwrf_20250729
  - _self_
  - override hydra/job_logging: default
```

## File: config/predict_dscale.yaml
```yaml
hydra:
  run:
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

# One-way downscaling inference — no boundary feedback.
# bdy_swap_method overridden to null so that the model predicts freely
# within the domain without re-injecting boundary observations.
data:
  use_Kth_hour_pred: null

inference:
  bdy_swap_method: null   # disable boundary re-injection (one-way mode)

lightning:
  sampling_rate: 1
  batch_size: 1  # must be 1 for auto-regression
  workers: 4

defaults:
  - data: rwrf_20250729
  - lightning: pangu_rwrf_20250729
  - model: pangu_rwrf_20250729
  - inference: pangu_rwrf_onnx
  - plot: pangu_rwrf
  - _self_
  - override hydra/job_logging: default
```

## File: config/predict_feedback.yaml
```yaml
hydra:
  run:
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

# Two-way boundary-feedback inference — ground-truth boundary values are
# re-injected at every model time-step to suppress domain-edge errors.
#
# bdy_swap_method MUST be non-null; PredictFeedbackRunner validates this
# and raises ValueError if it is missing or null.
#
# Inherited from inference/pangu_rwrf_onnx.yaml:
#   bdy_swap_method:
#     name: exp_decay    ← blending kernel (options: exp_decay, linear, …)
#     n_of_grid: 10      ← number of boundary grid cells to replace
#
# Override on the CLI with:
#   python predict_feedback.py inference.bdy_swap_method.n_of_grid=16

data:
  use_Kth_hour_pred: null

# feedback_iters is informational: the actual loop length is controlled
# by showcase_length and output_itv in the inference config.
inference:
  feedback_iters: 3

lightning:
  sampling_rate: 1
  batch_size: 1  # must be 1 for auto-regression
  workers: 4

defaults:
  - data: rwrf_20250729
  - lightning: pangu_rwrf_20250729
  - model: pangu_rwrf_20250729
  - inference: pangu_rwrf_onnx   # provides non-null bdy_swap_method by default
  - plot: pangu_rwrf
  - _self_
  - override hydra/job_logging: default
```

## File: src/dlamp/analysis/__init__.py
```python

```

## File: src/dlamp/data/preproc/__init__.py
```python

```

## File: src/dlamp/data/registry/__init__.py
```python

```

## File: src/dlamp/data/__init__.py
```python

```

## File: src/dlamp/inference/__init__.py
```python
from .batch_inference_ckpt import *
from .batch_inference_onnx import *
from .inference_base import *

__all__ = ["BatchInferenceCkpt", "BatchInferenceOnnx"]
```

## File: src/dlamp/managers/__init__.py
```python
from .data_manager import *
from .datetime_manager import *
```

## File: src/dlamp/models/architectures/__init__.py
```python
from .drop_path import *
from .glide_unet import *
from .multilayer_perceptron import *
from .pangu_model import *
from .unet import *
```

## File: src/dlamp/models/architectures/glide_unet_test.py
```python
import unittest

import torch

from .glide_unet import GlideUNet


class GlideUNetTest(unittest.TestCase):
    def test_unet(self):
        batch_size = 16
        channels = 3
        hidden_dim = 128
        ch_mults = (1, 2, 2, 1)
        is_attn = (False, False, False, True)
        n_blocks = 4

        # input
        input_shape = (batch_size, channels, 224, 224)
        x = torch.randn(input_shape)
        x = x.cuda()

        # time step for diffusion
        t = torch.randint(0, 1000, (batch_size,))
        t = t.cuda()

        # condition input
        cond = torch.randn(input_shape)
        cond = cond.cuda()

        # model
        model = GlideUNet(
            image_channels=channels,
            hidden_dim=hidden_dim,
            ch_mults=ch_mults,
            is_attn=is_attn,
            n_blocks=n_blocks,
        )
        model = model.cuda()

        with torch.no_grad():
            y = model(x, t, cond)

        self.assertEqual(x.shape, y.shape)


if __name__ == "__main__":
    # CLI: python -m src.models.architectures.glide_unet_test
    unittest.main(verbosity=2)
```

## File: src/dlamp/models/architectures/multilayer_perceptron.py
```python
import torch
from torch import nn

__all__ = ["MultilayerPerceptron"]


class MultilayerPerceptron(nn.Module):
    def __init__(self, dim: int, dropout_rate: float, reduce_dim: bool) -> None:
        super().__init__()
        oup_dim = dim // 2 if reduce_dim else dim
        self.linear1 = nn.Linear(dim, dim * 4)
        self.linear2 = nn.Linear(dim * 4, oup_dim)
        self.activation = nn.GELU()
        self.drop = nn.Dropout(p=dropout_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.linear1(x)
        x = self.activation(x)
        x = self.drop(x)
        x = self.linear2(x)
        x = self.drop(x)
        return x
```

## File: src/dlamp/models/builders/__init__.py
```python
from .base_builder import *
from .glide_builder import *
from .pangu_builder import *
```

## File: src/dlamp/models/callbacks/__init__.py
```python
from .log_diffusion_pred_samples_callback import *
from .log_prediction_samples_callback import *
```

## File: src/dlamp/models/lightning_modules/__init__.py
```python
from .diffusion_lightning_module import *
from .pangu_lightning_module import *
```

## File: src/dlamp/models/loss_fn/__init__.py
```python
from .crps import *
from .euclidean import *
```

## File: src/dlamp/models/loss_fn/euclidean.py
```python
import torch
from torch import nn


class EuclideanLoss(nn.Module):
    def __init__(self, reduction="mean"):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred, target):
        # pred and target shape: (Batch Size, Channels, Height, Width)
        loss = torch.sqrt(torch.sum((pred - target) ** 2, dim=(1, 2, 3)))
        # loss shape: (Batch Size,)

        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        else:
            return loss
```

## File: src/dlamp/models/__init__.py
```python
from .architectures import *
from .builders import *
from .callbacks import *
from .lightning_modules import *
from .model_utils import *
```

## File: src/dlamp/utils/__init__.py
```python
# only for usage of `from dlamp.utils import *`
__all__ = ["DataCompose", "DataType", "Level", "gen_data", "gen_path"]

# define package members, be careful of circular import
from .data_compose import *
from .data_generator import *
from .data_type import *
from .file_util import *
from .time_util import *
```

## File: src/dlamp/workflows/__init__.py
```python
"""Workflow runner classes for the DLAMP pipeline.

This subpackage provides thin, testable runner objects that implement
the business logic for each Hydra entrypoint.  The entrypoints at the
repository root are intentionally kept small — they perform only Hydra
bootstrapping, singleton initialisation, and delegation to these runners.

Exported runners:
    DataPrepRunner       — constant-mask generation (``data_prep.py``)
    DataStatsRunner      — z-score statistics computation (``data_stats.py``)
    PredictDscaleRunner  — one-way downscaling inference (``predict_dscale.py``)
    PredictFeedbackRunner — two-way boundary-feedback inference
                           (``predict_feedback.py``)
"""

from .data_prep_runner import DataPrepRunner
from .data_stats_runner import DataStatsRunner
from .predict_dscale_runner import PredictDscaleRunner
from .predict_feedback_runner import PredictFeedbackRunner

__all__ = [
    "DataPrepRunner",
    "DataStatsRunner",
    "PredictDscaleRunner",
    "PredictFeedbackRunner",
]
```

## File: src/dlamp/workflows/predict_dscale_runner.py
```python
"""One-way downscaling inference workflow runner for the DLAMP pipeline.

Executes model auto-regression in the forward direction only —
no boundary values from ground-truth are re-injected during the
prediction loop.  This is the simplest inference mode and is equivalent
to the existing ``predict.py`` workflow with
``inference.bdy_swap_method`` set to ``null``.

The runner delegates to ``analysis.PredictionRunner`` (the same class
used by ``predict.py``) and returns its result dict unchanged so that
callers can pipe it through the same saving and plotting helpers.

Raises:
    ValueError: If the configuration is invalid.
    ModuleNotFoundError: If the specified inference engine module cannot
        be imported.
"""

import logging
from typing import Any

from omegaconf import DictConfig

from dlamp.analysis.prediction import PredictionRunner

logger = logging.getLogger(__name__)


class PredictDscaleRunner:
    """Runs the one-way downscaling (no feedback) inference workflow.

    Thin wrapper around ``PredictionRunner`` that forces the boundary-
    swap method to ``None`` for the standard downscaling use-case.
    Boundary override can still be enabled by setting
    ``inference.bdy_swap_method`` in the Hydra config to a non-null
    dict — the runner passes the config through unchanged.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        _predictor (PredictionRunner): The underlying prediction engine.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the PredictDscaleRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  The
                ``inference.bdy_swap_method`` key is expected to be
                ``null`` for pure downscaling.  If it is set to a dict
                it will be forwarded to the auto-regression loop as-is.
        """
        self.cfg = cfg
        self._predictor: PredictionRunner = PredictionRunner(cfg)

    def run(self) -> dict[str, Any]:
        """Executes the one-way downscaling inference.

        Returns:
            dict[str, Any]: Prediction results as returned by
                ``PredictionRunner.run()``, containing:
                - ``output_upper`` (np.ndarray): Upper-air predictions.
                - ``output_surface`` (np.ndarray): Surface predictions.
                - ``lat`` (np.ndarray): Latitude grid.
                - ``lon`` (np.ndarray): Longitude grid.
                - ``mask`` (np.ndarray): Land-sea mask.
                - ``start_time`` (datetime): Forecast start time.
        """
        logger.info("PredictDscaleRunner: starting one-way downscaling inference")
        results = self._predictor.run()
        logger.info("PredictDscaleRunner: inference complete")
        return results
```

## File: src/dlamp/__init__.py
```python
"""DLAMP package initialization.

Provides core module components for DLAMP PyTorch Lightning models.
"""

__version__ = "0.1.0"
```

## File: src/dlamp/py.typed
```

```

## File: config/data/rwrf_20250627.yaml
```yaml
start_time: "2018-01-01 00:00"
end_time: "2025-05-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
grid_spacing:
  ground_truth_m: 2000.0
  forecast_m: 4000.0
add_time_features: True
use_Kth_hour_pred: 0
train_data:
  Z:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  T:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  U:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  V:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  W:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  Qv:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  Qw:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    # - Meter2
  SST:
    - SeaSurface
  PSFC:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/data/rwrf_20250729.yaml
```yaml
start_time: "2010-09-18 18:00"  #"2018-01-01 00:00"
end_time: "2010-09-20 00:00"    #"2025-05-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
  #grid_spacing:
  #ground_truth_m: 2000.0
  #forecast_m: 4000.0
add_time_features: True
use_Kth_hour_pred: 0
train_data:
  Z:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  T:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  U:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  V:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  W:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  Qv:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  Qw:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    # - Meter2
  SST:
    - SeaSurface
  PSFC:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/lightning/pangu_rwrf_20250611.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 3
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 2e-4
    weight_decay: 3e-6
lr_schedule:
  name: cosine
  args:
    warmup_steps: 1000
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: 99999999
max_steps: null
min_steps: 5e6 # 500k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
save_last: True
```

## File: config/lightning/pangu_rwrf_20250627.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 3
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 2e-4
    weight_decay: 5e-6
lr_schedule:
  name: cosine
  args:
    warmup_steps: 1000
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: 99999999
max_steps: null
min_steps: 1e6 # 500k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 12
log_image_every_n_steps: 5e4
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
# resume_from_checkpoint: "checkpoints/Pangu_250716_192219-epoch=124-val_loss_epoch=0.2708.ckpt"
precision: "bf16-mixed"
save_last: True
```

## File: config/lightning/pangu_rwrf_20250729.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 3
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 2e-4
    weight_decay: 5e-6
lr_schedule:
  name: cosine
  args:
    warmup_steps: 1000
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: 99999999
max_steps: null
min_steps: 1e6 # 500k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 12
log_image_every_n_steps: 5e4
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
# resume_from_checkpoint: "checkpoints/Pangu_250716_192219-epoch=124-val_loss_epoch=0.2708.ckpt"
precision: "bf16-mixed"
save_last: True
```

## File: config/model/pangu_rwrf_20250611.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 5
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 2, 6]
# earth block
max_drop_path_ratio: 0.3
# earth attn 3d
heads: [8, 8, 16]
embed_dim: 256
dropout_rate: 0
window_size: [2, 7, 7]
```

## File: config/model/pangu_rwrf_20250627.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 5
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 2, 6]
# earth block
max_drop_path_ratio: 0.3
# earth attn 3d
heads: [8, 8, 16]
embed_dim: 256
dropout_rate: 0
window_size: [2, 7, 7]
```

## File: config/model/pangu_rwrf_20250729.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 4, 4]
smoothing_kernel_size: 5
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 2, 6]
# earth block
max_drop_path_ratio: 0.3
# earth attn 3d
heads: [8, 8, 16]
embed_dim: 256
dropout_rate: 0
window_size: [2, 7, 7]
```

## File: src/dlamp/analysis/data_manager.py
```python
# analysis/data_manager.py
"""Manages access to forecast and ground truth weather data.

This module provides the AnalysisDataManager class, which serves as a
high-level interface for accessing model forecast outputs and corresponding
ground truth data. It disassembles raw NumPy arrays into physical variables
and levels, and computes derived quantities like wind speed and vorticity.

Usage:
    data_manager = AnalysisDataManager(cfg, results)
    # Get F000H data (returns ground truth)
    fc_f000 = data_manager.get_forecast_data(-1, DataType.TK, Level.Hpa500)
    # Get vorticity for the 3rd forecast hour
    vort_f003 = data_manager.get_relative_vorticity(2, Level.Hpa500)
"""

import logging
import re  # NEW: robust pressure parsing with regex
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

import numpy as np
from omegaconf import DictConfig

from dlamp.utils import DataCompose, DataGenerator, DataType, Level

logger = logging.getLogger(__name__)

# --- Physical Constants for Meteorological Calculations ---
R_d = 287.058  # J kg^-1 K^-1, Gas constant for dry air
c_p = 1004.0  # J kg^-1 K^-1, Specific heat of dry air at constant pressure
kappa = R_d / c_p  # Poisson constant, ~0.286
epsilon = 0.622  # Ratio of molar masses of water vapor to dry air
L_v = 2.5e6  # J kg^-1, Latent heat of vaporization


class AnalysisDataManager:
    """Handles disassembly and retrieval of forecast and ground truth data.

    This class takes raw model output, provides methods to access specific
    variables, and calculates derived meteorological fields for analysis
    and plotting. It also handles the special case for F000H by providing
    ground truth data as the initial forecast state.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        results (Dict[str, Any]): The dictionary from PredictionRunner.
        start_time (datetime): The initial time of the forecast run.
        data_generator (DataGenerator): Instance for fetching ground truth.
        data_compositions (List[DataCompose]): Variable-level combinations.
        upper_vars (List[DataType]): Ordered list of upper-air variables.
        surface_vars (List[DataType]): Ordered list of surface variables.
        pressure_levels (List[Level]): Ordered list of pressure levels.
    """

    def __init__(self, cfg: DictConfig, prediction_results: dict[str, Any]):
        """Initializes the AnalysisDataManager.

        Args:
            cfg (DictConfig): The Hydra configuration object.
            prediction_results (Dict[str, Any]): Output from
                PredictionRunner.run(). It must contain 'output_upper',
                'output_surface', 'lat', 'lon', and 'start_time'.
        """
        self.cfg: DictConfig = cfg
        self.results: dict[str, Any] = prediction_results
        self.start_time: datetime = self.results["start_time"]
        self.data_generator: DataGenerator = DataGenerator(cfg.data.data_shape, cfg.data.image_shape)

        self.data_compositions: list[DataCompose] = DataCompose.from_config(cfg.data.train_data)
        self.upper_vars: list[DataType] = DataCompose.get_all_vars(self.data_compositions, only_upper=True)
        self.surface_vars: list[DataType] = DataCompose.get_all_vars(self.data_compositions, only_surface=True)
        self.pressure_levels: list[Level] = DataCompose.get_all_levels(self.data_compositions, only_upper=True)
        self._qw_output_unit_gkg: bool = self.cfg.plot.get("qw_display_unit", "kg/kg").lower() == "g/kg"
        logger.info(
            f"AnalysisDataManager initialized. Qw display unit for plots set to g/kg: {self._qw_output_unit_gkg}"
        )

    def _get_pressure_from_level(self, level: Level) -> float:
        """Extract pressure in Pascals [Pa] from a Level object robustly.

        Args:
            level (Level): e.g., Level.Hpa500 (upper-air constant-pressure level).

        Returns:
            float: Pressure in Pascals [Pa].

        Raises:
            ValueError: If the level is a surface level or pressure cannot be parsed.
        """
        if level.is_surface():
            # This helper is for constant-pressure (upper-air) levels only.
            # Surface pressure must be read from data (e.g., PSFC).
            raise ValueError(f"Cannot extract a fixed pressure from a surface level: {level.name}")
        # Prefer a string payload if available; fall back to str(level)
        text = getattr(level, "value", str(level))
        m = re.search(r"\d+(?:\.\d+)?", str(text))
        if not m:
            raise ValueError(f"Could not parse pressure value from level: {text}")
        pressure_hpa = float(m.group(0))
        return pressure_hpa * 100.0  # hPa -> Pa

    @lru_cache(maxsize=128)  # noqa: B019 - self is long-lived during inference
    def get_forecast_data(self, forecast_step: int, variable: DataType, level: Level) -> np.ndarray:
        """Retrieves a specific forecast variable grid.

        Handles the special case where `forecast_step = -1`, which corresponds
        to the initial state (F000H) and returns the ground truth data.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            variable (DataType): The meteorological variable to retrieve.
            level (Level): The pressure or surface level to retrieve.

        Returns:
            np.ndarray: A 2D NumPy array (height, width) of forecast data.
                Units are standard (e.g., K for temperature, m/s for wind).

        Raises:
            ValueError: If the variable or level is not found in the config.
            IndexError: If the forecast_step is out of bounds.
        """
        if forecast_step == -1:  # F000H case (ground truth)
            return self.get_ground_truth_data(self.start_time, variable, level)

        seq_len: int = self.results["output_upper"].shape[1]
        if not (0 <= forecast_step < seq_len):
            raise IndexError(f"forecast_step {forecast_step} out of range (0..{seq_len - 1}).")

        if level.is_surface():
            try:
                var_idx: int = self.surface_vars.index(variable)
                data: np.ndarray = self.results["output_surface"][0, forecast_step, 0, :, :, var_idx]
            except ValueError:
                valid: str = ", ".join([v.name for v in self.surface_vars])
                raise ValueError(f"Surface variable '{variable.name}' not found. Available: [{valid}]")
        else:
            try:
                var_idx: int = self.upper_vars.index(variable)
                lvl_idx: int = self.pressure_levels.index(level)
                data: np.ndarray = self.results["output_upper"][0, forecast_step, lvl_idx, :, :, var_idx]
            except ValueError:
                valid_v: str = ", ".join([v.name for v in self.upper_vars])
                valid_l: str = ", ".join([l.name for l in self.pressure_levels])
                raise ValueError(
                    f"Upper-air var/level '{variable.name}/{level.name}' "
                    f"not found. Available vars: [{valid_v}], "
                    f"levels: [{valid_l}]"
                )
        return data.astype(np.float32)

    def get_ground_truth_data(self, time: datetime, variable: DataType, level: Level) -> np.ndarray:
        """Retrieves the corresponding ground truth data for a given time.

        Args:
            time (datetime): The timestamp for which to retrieve GT data.
            variable (DataType): The meteorological variable.
            level (Level): The pressure or surface level.

        Returns:
            np.ndarray: A 2D NumPy array of ground truth data.
        """
        dc: DataCompose = DataCompose(var_name=variable, level=level)
        return self.data_generator.yield_data(time, dc).astype(np.float32)

    def get_forecast_time(self, forecast_step: int) -> datetime:
        """Calculates the calendar time for a given forecast step.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).

        Returns:
            datetime: The wall-clock time of the specified forecast step.
        """
        if forecast_step == -1:
            return self.start_time
        time_interval: timedelta = timedelta(**self.cfg.inference.output_itv)
        return self.start_time + (forecast_step + 1) * time_interval

    def _get_wind_components(self, forecast_step: int, level: Level) -> tuple[np.ndarray, np.ndarray]:
        """Helper to get U and V wind components for a forecast step."""
        u: np.ndarray = self.get_forecast_data(forecast_step, DataType.UM, level)
        v: np.ndarray = self.get_forecast_data(forecast_step, DataType.VM, level)
        return u, v

    def _get_gt_wind_components(self, time: datetime, level: Level) -> tuple[np.ndarray, np.ndarray]:
        """Helper to get U and V ground truth wind components for a time."""
        u: np.ndarray = self.get_ground_truth_data(time, DataType.UM, level)
        v: np.ndarray = self.get_ground_truth_data(time, DataType.VM, level)
        return u, v

    def get_wind_speed(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates wind speed from U and V components.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            level (Level): The pressure or surface level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of wind speed in meters per second.
        """
        if is_gt:
            time: datetime = self.get_forecast_time(forecast_step)
            u: np.ndarray
            v: np.ndarray
            u, v = self._get_gt_wind_components(time, level)
        else:
            u: np.ndarray
            v: np.ndarray
            u, v = self._get_wind_components(forecast_step, level)
        return np.sqrt(u**2 + v**2)

    def get_relative_vorticity(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates relative vorticity using a centered finite difference.

        This method uses `np.gradient` with a fixed grid spacing.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            level (Level): The pressure level (must be an upper-air level).
            dx (float): The grid spacing in meters for the data (e.g., 2000.0 for GT, 4000.0 for FC).
            is_gt (bool): If True, uses GT data.

        Returns:
            np.ndarray: 2D grid of relative vorticity in units of s^-1.
        """
        u: np.ndarray
        v: np.ndarray
        if is_gt:
            time: datetime = self.get_forecast_time(forecast_step)
            u, v = self._get_gt_wind_components(time, level)
            dx = self.cfg.plot.grid_spacing.ground_truth_m
            logger.debug(f"GT shape: u={np.shape(u)}, v={np.shape(v)}")
        else:
            u, v = self._get_wind_components(forecast_step, level)
            dx = self.cfg.plot.grid_spacing.forecast_m
            logger.debug(f"FC shape: u={np.shape(u)}, v={np.shape(v)}")

        du_dy: np.ndarray
        dv_dx: np.ndarray
        dv_dx, du_dy = np.gradient(v, dx, axis=1), np.gradient(u, dx, axis=0)
        vorticity: np.ndarray = dv_dx - du_dy
        return vorticity

    def get_column_max_qw(self, forecast_step: int, is_gt: bool = False) -> np.ndarray:
        """Calculates the maximum water content (Qw) in the vertical column.

        Args:
            forecast_step (int): The 0-indexed forecast step (-1 for F000H).
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of the maximum Qw value at each (x, y) point.
                Units are kg/kg.

        Raises:
            ValueError: If no Qw data is defined in the configuration.
        """
        qw_levels: list[Level] = [dc.level for dc in self.data_compositions if dc.var_name == DataType.Qt]
        if not qw_levels:
            raise ValueError("No Qw data found in configuration.")

        all_qw_layers: list[np.ndarray] = []
        time: datetime = self.get_forecast_time(forecast_step)
        for level in qw_levels:
            data: np.ndarray
            if is_gt:
                data = self.get_ground_truth_data(time, DataType.Qt, level)
            else:
                data = self.get_forecast_data(forecast_step, DataType.Qt, level)
            all_qw_layers.append(data)

        return np.max(np.stack(all_qw_layers, axis=0), axis=0)

    def get_potential_temperature(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates potential temperature (Theta).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of potential temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)

        pressure_pa = self._get_pressure_from_level(level)
        p0 = 100000.0  # Pa
        theta = T * (p0 / pressure_pa) ** kappa
        return theta

    def get_saturation_vapor_pressure(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates saturation vapor pressure (es).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, calculates from ground truth data.

        Returns:
            np.ndarray: 2D grid of saturation vapor pressure in Pascals [Pa].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)

        T_c = T - 273.15
        es = 611.2 * np.exp((17.67 * T_c) / (T_c + 243.5))
        return es

    def get_dew_point_temperature(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates dew point temperature (Td) from mixing ratio r (kg/kg).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of dew point temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        pressure_pa = self._get_pressure_from_level(level)
        e = (r * pressure_pa) / (epsilon + r)
        e = np.maximum(e, 1.0)

        val = np.log(e / 611.2)
        Td_c = (243.5 * val) / (17.67 - val)
        Td = Td_c + 273.15
        return Td

    def get_relative_humidity(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates relative humidity (RH) from mixing ratio r (kg/kg).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of relative humidity in percent [%].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        pressure_pa = self._get_pressure_from_level(level)
        e = (r * pressure_pa) / (epsilon + r)
        T_c = T - 273.15
        es = 611.2 * np.exp((17.67 * T_c) / (T_c + 243.5))

        rh = (e / es) * 100.0
        return np.clip(rh, 0, 100)

    def get_equivalent_potential_temperature(self, forecast_step: int, level: Level, is_gt: bool = False) -> np.ndarray:
        """Calculates equivalent potential temperature (Theta-e) using Bolton (1980).

        Args:
            forecast_step (int): The 0-indexed forecast step.
            level (Level): The pressure level.
            is_gt (bool): If True, uses ground truth data.

        Returns:
            np.ndarray: 2D grid of equivalent potential temperature in Kelvin [K].
        """
        time = self.get_forecast_time(forecast_step)
        if is_gt:
            T = self.get_ground_truth_data(time, DataType.TK, level)
            r = self.get_ground_truth_data(time, DataType.Qv, level)
        else:
            T = self.get_forecast_data(forecast_step, DataType.TK, level)
            r = self.get_forecast_data(forecast_step, DataType.Qv, level)

        # 1) Use the existing method to get potential temperature (reduces duplication)
        theta = self.get_potential_temperature(forecast_step, level, is_gt)
        # 2) Get pressure for vapor pressure / dewpoint
        pressure_pa = self._get_pressure_from_level(level)

        e = (r * pressure_pa) / (epsilon + r)
        e = np.maximum(e, 1.0)
        val = np.log(e / 611.2)
        Td_c = (243.5 * val) / (17.67 - val)
        Td = Td_c + 273.15

        Tlcl = 1.0 / (1.0 / (Td - 56.0) + np.log(T / Td) / 800.0) + 56.0

        theta_e = theta * np.exp((L_v * r) / (c_p * Tlcl)) * (T / Tlcl) ** (0.28 * r)
        return theta_e
```

## File: src/dlamp/analysis/forecast_saver.py
```python
# analysis/forecast_saver.py
"""Saves forecast data to NetCDF files in a WRF-compatible format.

This module provides the ForecastSaver class, which takes disassembled
forecast data and saves each time step into a separate NetCDF file that
adheres to WRF naming conventions for dimensions, coordinates, and variables.
It uses metadata defined in `analysis.netcdf_meta`.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import cftime
import numpy as np
import xarray as xr

from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.netcdf_meta import GLOBAL_ATTRIBUTES, VARIABLE_ATTRIBUTES
from dlamp.utils.data_type import DataType, Level

logger = logging.getLogger(__name__)


class ForecastSaver:
    """Serializes forecast results into WRF-style NetCDF files.

    Attributes:
        manager (AnalysisDataManager): The data manager instance.
        output_dir (Path): Directory where NetCDF files will be saved.
    """

    def __init__(
        self,
        manager: AnalysisDataManager,
        output_dir: Path,
        earth2studio_output_dir: Path | None = None,
        exp_code: str = "dlamp",
    ):
        """Initializes the ForecastSaver.

        Args:
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): The target directory for saving WRF-style files.
            earth2studio_output_dir (Optional[Path]): Target directory for
                saving Earth2Studio-ready NetCDF files.
            exp_code (str): An experiment code to use as a prefix for filenames.
        """
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.exp_code: str = exp_code

        self.earth2studio_output_dir: Path | None = earth2studio_output_dir
        if self.earth2studio_output_dir:
            self.earth2studio_output_dir.mkdir(parents=True, exist_ok=True)

    def save_all_forecasts(self) -> None:
        """Saves all forecast steps (F001H onwards) to NetCDF files."""
        num_steps: int = self.manager.results["output_upper"].shape[1]
        logger.info("Saving %d forecast steps to NetCDF.", num_steps)

        for step in range(num_steps):
            self._save_single_step(step)

        logger.info("Saved all forecast steps to %s", self.output_dir)

    def save_earth2studio_forecasts(self) -> None:
        """Saves all forecast steps (F001H onwards) to Earth2Studio-ready NetCDF files."""
        if not self.earth2studio_output_dir:
            logger.warning("Earth2Studio output directory not set. Skipping save.")
            return

        num_steps: int = self.manager.results["output_upper"].shape[1]
        logger.info("Saving %d forecast steps to Earth2Studio-ready NetCDF.", num_steps)

        for step in range(num_steps):
            self._save_earth2studio_format(step)

        logger.info("Saved all Earth2Studio-ready forecast steps to %s", self.earth2studio_output_dir)

    def _save_earth2studio_format(self, forecast_step: int) -> None:
        """Saves a single forecast step to an Earth2Studio-compatible NetCDF file.

        Args:
            forecast_step (int): The 0-indexed forecast step to save.
        """
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        lat: np.ndarray = self.manager.results["lat"]
        lon: np.ndarray = self.manager.results["lon"]
        H, W = lat.shape

        # Determine the full list of variables and their order
        # This needs to be consistent for the 'variable' dimension
        all_variables_with_levels: list[tuple[DataType, Level]] = []
        for level in self.manager.pressure_levels:
            for var in self.manager.upper_vars:
                all_variables_with_levels.append((var, level))
        for var in self.manager.surface_vars:
            # For surface variables, use Level.Surface as a consistent identifier
            all_variables_with_levels.append((var, Level.Surface))

        variable_names: list[str] = []
        for var_type, level_type in all_variables_with_levels:
            # Create a unique string identifier for each variable-level combination
            if level_type.is_surface():
                variable_names.append(f"{var_type.name}_sfc")
            else:
                variable_names.append(f"{var_type.name}_{level_type.nc_key}hPa")

        num_variables = len(variable_names)
        # The prompt states variable = 73. We should log a warning if it doesn't match.
        if num_variables != 73:
            logger.warning(
                f"Number of variables ({num_variables}) does not match "
                "expected Earth2Studio format (73). Proceeding with available variables."
            )

        # Initialize the 4D data array
        initial_data_array = np.zeros((1, num_variables, H, W), dtype=np.float32)

        # Populate the data array
        for idx, (var_type, level_type) in enumerate(all_variables_with_levels):
            data: np.ndarray = self.manager.get_forecast_data(forecast_step, var_type, level_type)
            # Handle Qw unit conversion if necessary (from g/kg to kg/kg)
            # The manager's _qw_output_unit_gkg indicates if Qw was converted to g/kg for plotting.
            # If so, convert it back to kg/kg for the Earth2Studio output.
            if var_type == DataType.Qt:
                data = data / 1000.0

            initial_data_array[0, idx, :, :] = data

        # Calculate time as hours since 0001-01-01 00:00:00.0
        reference_time = cftime.DatetimeGregorian(1, 1, 1, 0, 0, 0)
        forecast_cftime = cftime.DatetimeGregorian(
            forecast_time.year,
            forecast_time.month,
            forecast_time.day,
            forecast_time.hour,
            forecast_time.minute,
            forecast_time.second,
        )
        time_value = (forecast_cftime - reference_time).total_seconds() / 3600.0

        # Create xarray Dataset
        ds = xr.Dataset(
            {
                "initial_data": (
                    ("time", "variable", "lat", "lon"),
                    initial_data_array,
                    {
                        "description": "Initial forecast data",
                        "units": "various (see variable names)",
                    },
                )
            },
            coords={
                "time": (
                    "time",
                    [time_value],
                    {
                        "units": "hours since 0001-01-01 00:00:00.0",
                        "calendar": "proleptic_gregorian",
                    },
                ),
                "variable": ("variable", variable_names),
                "lat": ("lat", lat[:, 0]),  # Assuming lat is (H, W) and we need a 1D array
                "lon": ("lon", lon[0, :]),  # Assuming lon is (H, W) and we need a 1D array
            },
        )

        filename: str = f"earth2studio_{self.exp_code}_{forecast_time.strftime('%Y%m%d_%H%M%S')}.nc"
        output_path: Path = self.earth2studio_output_dir / filename

        encoding: dict[str, dict[str, Any]] = {"initial_data": {"zlib": True, "complevel": 4}}
        ds.to_netcdf(output_path, encoding=encoding)
        logger.info(f"Saved Earth2Studio-ready NetCDF to {output_path}")

    def _save_single_step(self, forecast_step: int) -> None:
        """Saves a single forecast step to a WRF-compatible NetCDF file.

        Args:
            forecast_step (int): The 0-indexed forecast step to save.
        """
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        lat: np.ndarray = self.manager.results["lat"]
        lon: np.ndarray = self.manager.results["lon"]
        mask: np.ndarray = self.manager.results["mask"]
        H: int
        W: int
        H, W = lat.shape
        time_str: str = forecast_time.strftime("%Y-%m-%d_%H:%M:%S")

        coords: dict[str, Any] = {
            "Time": (("Time",), [0]),
            "south_north": (("south_north",), np.arange(H, dtype=np.int32)),
            "west_east": (("west_east",), np.arange(W, dtype=np.int32)),
        }

        data_vars: dict[str, Any] = {
            "Times": (
                ("Time", "DateStrLen"),
                np.array([list(time_str.ljust(19))], dtype="S1"),
            ),
            "XLAT": (("Time", "south_north", "west_east"), lat[None, ...]),
            "XLONG": (("Time", "south_north", "west_east"), lon[None, ...]),
            "LANDMASK": (("Time", "south_north", "west_east"), mask[None, ...]),
        }

        # Per RWRF format, pressure levels should be from high to low (e.g., 1000 -> 50)
        # The manager provides them from low to high, so we reverse them.
        pressure_levels_reversed = self.manager.pressure_levels[::-1]
        pres_levels_val: np.ndarray = np.array(
            [float(lv.nc_key) for lv in pressure_levels_reversed],
            dtype=np.float32,
        )
        data_vars["pres_levels"] = (("pres_bottom_top",), pres_levels_val)

        # Initialize containers for upper-air data
        upper_air_cubes: dict[str, np.ndarray] = {
            var.name: np.full((1, len(pres_levels_val), H, W), np.nan, dtype=np.float32)
            for var in self.manager.upper_vars
        }

        # Map from internal enum names to NetCDF variable keys
        key_map: dict[str, str] = {
            "umet10": "umet10",
            "vmet10": "vmet10",
            "t2m": "T2",
            "q2m": "Q2",
            "psfc": "PSFC",
            "sst": "SST",
            "swdown": "SWDOWN",
            "olr": "OLR",
        }

        for dc in self.manager.data_compositions:
            arr: np.ndarray = self.manager.get_forecast_data(forecast_step, dc.var_name, dc.level)
            # Default key is from the DataType enum's nc_key
            key: str = dc.var_name.nc_key

            # Handle special cases and surface variables
            if dc.var_name == DataType.Qt:
                key = "QTOTAL_p"  # Special key for total water
            elif dc.level.is_surface():
                key = key_map.get(dc.combined_key, dc.combined_key)

            if dc.level.is_surface():
                data_vars[key] = (
                    ("Time", "south_north", "west_east"),
                    arr[None, ...],
                )
            else:
                # Find the index in the reversed list to place the data correctly
                level_idx: int = pressure_levels_reversed.index(dc.level)
                upper_air_cubes[dc.var_name.name][0, level_idx, :, :] = arr

        # Add all completed upper-air cubes to the data_vars.
        # If a standardization path is provided in the config, it's assumed
        # that the de-standardized Qw is in g/kg and must be converted to
        # kg/kg by dividing by 1000. Otherwise, it's assumed to be in kg/kg.
        # adjust_qw_units: bool = (
        #    self.manager.cfg.data.get("standardization_path") is not None
        # )
        for var_name, cube in upper_air_cubes.items():
            var_type: DataType = DataType[var_name]
            key = var_type.nc_key
            data_vars[key] = (
                ("Time", "pres_bottom_top", "south_north", "west_east"),
                cube / 1000 if var_name == "Qt" else cube,
            )

        dataset: xr.Dataset = xr.Dataset(data_vars, coords=coords)
        dataset.attrs.update(GLOBAL_ATTRIBUTES)
        dataset.attrs["FORECAST_VALID_TIME"] = forecast_time.isoformat()

        # Assign variable attributes from the metadata file
        for var_name, var_data in dataset.variables.items():
            if var_name in VARIABLE_ATTRIBUTES:
                var_data.attrs = VARIABLE_ATTRIBUTES[var_name]

        start_time_str: str = self.manager.start_time.strftime("%Y%m%d_%H%M")
        step_plus_one: int = forecast_step + 1
        filename: str = f"{self.exp_code}_{start_time_str}_F{step_plus_one:03d}.nc"
        output_path: Path = self.output_dir / filename

        encoding: dict[str, dict[str, Any]] = {var: {"zlib": True, "complevel": 4} for var in data_vars}
        dataset.to_netcdf(output_path, encoding=encoding)
```

## File: src/dlamp/analysis/netcdf_meta.py
```python
# analysis/netcdf_meta.py
"""Metadata for creating WRF-compatible NetCDF files.

This module provides dictionaries containing attributes (like units and
descriptions) for variables and global properties of the NetCDF files,
ensuring consistency with WRF output standards.
"""

from typing import Any

# Global attributes to be written to the NetCDF file
# A subset of common WRF attributes for reproducibility
GLOBAL_ATTRIBUTES: dict[str, Any] = {
    "TITLE": "DLAMP AI MODEL OUTPUT",
    "MAP_PROJ_CHAR": "Lambert Conformal",
    "MMINLU": "MODIFIED_IGBP_MODIS_NOAH",
    "SIMULATION_INITIALIZATION_TYPE": "REAL-DATA CASE",
    "GRIDTYPE": "A",
}

# Variable-specific attributes (units, description, etc.)
VARIABLE_ATTRIBUTES: dict[str, Any] = {
    "Times": {"description": "model time"},
    "XLAT": {
        "description": "Latitude, South is Negative",
        "units": "degree_north",
    },
    "XLONG": {
        "description": "Longitude, West is Negative",
        "units": "degree_east",
    },
    "pres_levels": {"description": "Constant Pressure Levels", "units": "hPa"},
    "HGT": {
        "description": "Terrain Height",
        "units": "m",
    },
    "LANDMASK": {
        "description": "Land Sea Mask (1=Land and 0=Sea)",
        "units": "1",
    },
    "z_p": {
        "description": "Geopotential Height",
        "units": "m",
    },
    "tk_p": {
        "description": "Air Temperature",
        "units": "K",
    },
    "umet_p": {
        "description": "U-component of Wind Rotated to Earth Coordinates",
        "units": "m s-1",
    },
    "vmet_p": {
        "description": "V-component of Wind Rotated to Earth Coordinates",
        "units": "m s-1",
    },
    "wa_p": {
        "description": "Vertical Velocity",
        "units": "m s-1",
    },
    "QVAPOR_p": {
        "description": "Water Vapor Mixing Ratio",
        "units": "kg kg-1",
    },
    "QWATER_p": {
        "description": "Total Hydrometeors Mixing Ratio (cloud+rain+ice+snow+graupel)",
        "units": "kg kg-1",
    },
    "PSFC": {
        "description": "Surface Pressure",
        "units": "Pa",
    },
    "SLP": {
        "description": "Sea-Level Pressure",
        "units": "hPa",
    },
    "SST": {
        "description": "Sea Surface Temperature",
        "units": "K",
    },
    "RAINNC": {
        "description": "Accumulated Grid Scale Precipitation",
        "units": "mm",
    },
    "PBLH": {
        "description": "Planetary Boundary Layer Height",
        "units": "m",
    },
    "pw": {
        "description": "Precipitable Water",
        "units": "kg m-2",
    },
    "SWDOWN": {
        "description": "Downward Shortwave Radiation Flux at Ground Surface",
        "units": "W m-2",
    },
    "OLR": {
        "description": "Outgoing Longwave Radiation Flux at Top of Atmosphere(TOA)",
        "units": "W m-2",
    },
    "T2": {
        "description": "Air Temperature at 2 Meters Height ",
        "units": "K",
    },
    "Q2": {
        "description": "Water Vapor Mixing Ratio at 2 Meters Height",
        "units": "kg kg-1",
    },
    "umet10": {
        "description": "U-component of Wind Rotated to Earth Coordinates at 10 Meters Height",
        "units": "m s-1",
    },
    "vmet10": {
        "description": "V-component of Wind Rotated to Earth Coordinates at 10 Meters Height",
        "units": "m s-1",
    },
}
```

## File: src/dlamp/analysis/plot_meta.py
```python
# analysis/plot_meta.py
"""Metadata and configurations for generating weather analysis plots.

This module provides dictionary-based configurations that define the content,
layout, and properties of each panel in the analysis figures, separating
the plot design from the plotting logic.
"""

from typing import Any

from dlamp.utils.data_type import Level

# A list of dictionaries, where each dictionary defines one plot panel.
# This structure makes it easy to add, remove, or reorder plots.
ANALYSIS_PLOT_CONFIGS: list[dict[str, Any]] = [
    {
        "title": "500hPa Wind & Height",
        "unit": "m s-1",
        "level": Level.Hpa500,
        "plot_func_key": "wind_speed",
        "cmap": "Spectral_r",
        "vmin": 0,
        "vmax": 60,
    },
    {
        "title": "500hPa Vorticity & Height",
        "unit": "1e-6 s-1",
        "level": Level.Hpa500,
        "plot_func_key": "vorticity",
        "cmap": "YlOrBr",
        "vmin": 0,
        "vmax": 200,
    },
    {
        "title": "850hPa Wind & Height",
        "unit": "m s-1",
        "level": Level.Hpa850,
        "plot_func_key": "wind_speed",
        "cmap": "Spectral_r",
        "vmin": 0,
        "vmax": 60,
    },
    {
        "title": "850hPa Vorticity & Height",
        "unit": "1e-6 s-1",
        "level": Level.Hpa850,
        "plot_func_key": "vorticity",
        "cmap": "YlOrBr",
        "vmin": 0,
        "vmax": 200,
    },
    {
        "title": "925hPa Theta-e & Wind",
        "unit": "K",
        "level": Level.Hpa925,
        "plot_func_key": "theta_e",
        "cmap": "twilight_shifted",
        "vmin": 320,
        "vmax": 360,
    },
    {
        "title": "925hPa Qt & 10m Wind",
        "unit": "g kg-1",
        "level": Level.Hpa925,
        "plot_func_key": "hydrometeors_mixing_ratio",
        "cmap": "managua",
        "vmin": 1e-4,
        "vmax": 4,
        "colorbar_scale": "log",
        "colorbar_gamma": None,
    },
]
```

## File: src/dlamp/analysis/prediction.py
```python
# FILE: analysis/prediction.py
"""Module for running the weather model inference.

This module provides the PredictionRunner class, which encapsulates the
logic for setting up and executing a model inference session based on a
Hydra configuration.
"""

import importlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import hydra
import numpy as np
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.inference import InferenceBase
from dlamp.utils import DataCompose, DataGenerator

logger = logging.getLogger(__name__)


class PredictionRunner:
    """Handles the setup and execution of the model inference process.

    This class reads the configuration, initializes the appropriate
    inference engine (either from a checkpoint or ONNX), runs the
    prediction, and returns the results in memory.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        eval_cases (List[datetime]): A list of timestamps for evaluation.
        infer_machine (InferenceBase): The instantiated inference engine.
    """

    def __init__(self, cfg: DictConfig):
        """Initializes the PredictionRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object that defines
                the model, data, and inference settings.
        """
        self.cfg = cfg
        self.eval_cases = [datetime.strptime(cfg.data.start_time, cfg.data.format).replace(tzinfo=UTC)]
        self.infer_machine: InferenceBase = self._setup_inference_machine()

    def _setup_inference_machine(self) -> InferenceBase:
        """Sets up the inference engine based on the configuration.

        Dynamically imports and instantiates the correct inference class
        (e.g., 'BatchInferenceCkpt' or 'BatchInferenceOnnx').

        Raises:
            ValueError: If the 'infer_type' in the config is not supported.

        Returns:
            InferenceBase: An initialized instance of the inference engine.
        """
        infer_type: str = self.cfg.inference.infer_type
        INFERENCE_CLASSES = {
            "ckpt": ("inference.batch_inference_ckpt", "BatchInferenceCkpt"),
            "onnx": ("inference.batch_inference_onnx", "BatchInferenceOnnx"),
        }

        if infer_type not in INFERENCE_CLASSES:
            raise ValueError(f"Unsupported inference type: {infer_type}")

        module_name, class_name = INFERENCE_CLASSES[infer_type]

        try:
            module = importlib.import_module(module_name)
            infer_class: type[InferenceBase] = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error("Failed to load inference class: %s", e)
            raise

        return infer_class(self.cfg, self.eval_cases)

    def run(self) -> dict[str, Any]:
        """Executes the full inference workflow.

        This method runs the model prediction and then generates the
        corresponding latitude and longitude grids. It returns all results
        as a dictionary, avoiding file I/O for intermediate data.

        Returns:
            Dict[str, Any]: A dictionary containing the prediction results,
                including:
                - 'output_upper' (np.ndarray): Upper-air variables.
                - 'output_surface' (np.ndarray): Surface variables.
                - 'lat' (np.ndarray): Latitude grid.
                - 'lon' (np.ndarray): Longitude grid.
                - 'start_time' (datetime): The forecast start time.
        """
        logger.info("Starting model inference...")
        self.infer_machine.infer(bdy_swap_method=self.cfg.inference.bdy_swap_method)
        logger.info("Inference complete.")

        # Prepare latitude and longitude grids
        data_gnrt: DataGenerator = self.infer_machine.data_manager.data_gnrt
        dc_lat: DataCompose
        dc_lon: DataCompose
        dc_mask: DataCompose
        dc_lat, dc_lon, dc_mask = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"], "MASK": ["NoRule"]})
        start_time: datetime = datetime.strptime(self.cfg.data.start_time, self.cfg.data.format).replace(
            tzinfo=UTC
        )
        lat: np.ndarray = data_gnrt.yield_data(start_time, dc_lat)
        lon: np.ndarray = data_gnrt.yield_data(start_time, dc_lon)
        mask: np.ndarray = data_gnrt.yield_data(start_time, dc_mask)

        return {
            "output_upper": self.infer_machine.output_upper,
            "output_surface": self.infer_machine.output_surface,
            "lat": lat,
            "lon": lon,
            "mask": mask,
            "start_time": start_time,
        }


@hydra.main(
    version_base=None,
    config_path=str(REPO_ROOT / "config"),
    config_name="predict",
)
def main(cfg: DictConfig) -> None:
    """Runs the full prediction, saving, and plotting workflow.

    This is the ``dlamp-predict`` console-script entry point.  It
    performs model inference (``PredictionRunner``), writes WRF-compatible
    NetCDF forecasts, and generates analysis plots.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/predict.yaml``.

    Raises:
        IOError: If there's an error creating output directories or files.
        ValueError: If the configuration is invalid.
        ModuleNotFoundError: If a specified module for inference is not found.
    """
    from dlamp.analysis.data_manager import AnalysisDataManager
    from dlamp.analysis.forecast_saver import ForecastSaver
    from dlamp.analysis.plotter import WeatherPlotter
    from dlamp.runtime_config import RuntimeConfig
    from dlamp.standardizer import get_standardizer

    try:
        OmegaConf.set_struct(cfg, True)
        out_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
        logger.info("Start workflow -> %s", out_dir)
        print("cfg = ", cfg)

        # Build runtime config eagerly (validates model code paths)
        runtime_config = RuntimeConfig.from_env()
        # Construct standardizer to load stats + data_list once
        get_standardizer(runtime_config)
        logger.info("Runtime config and standardizer initialized.")

        # Step 1: Execute the model inference
        predictor: PredictionRunner = PredictionRunner(cfg)
        results = predictor.run()
        logger.info("Model inference complete.")

        # Step 2: Initialize the data manager with prediction results
        adm: AnalysisDataManager = AnalysisDataManager(cfg, results)

        # Step 3: Save all forecast time steps to WRF-compatible NetCDF files
        saver: ForecastSaver = ForecastSaver(adm, out_dir / "netcdf_forecasts")
        saver.save_all_forecasts()
        logger.info("All forecast steps saved to NetCDF files.")

        # Step 4: Generate and save analysis plots for specific time steps
        plotter: WeatherPlotter = WeatherPlotter(cfg, adm, out_dir / "plots")
        # Plot initial state (F000H) and hourly forecasts
        plot_steps: list[int] = [-1] + list(range(cfg.plot.figure_columns))
        logger.info("Generating analysis plots for steps: %s", plot_steps)

        for step in plot_steps:
            try:
                # Ensure step is within the valid forecast range
                num_forecasts: int = results["output_upper"].shape[1]
                if step >= num_forecasts:
                    logger.warning(
                        "Skipping plot for step F%03dH as it exceeds max.",
                        step + 1,
                    )
                    continue

                plotter.create_analysis_figure(step)
            except (ValueError, IndexError):
                step_plus_one: int = step + 1
                step_str: str = "F000H" if step == -1 else f"F{step_plus_one:03d}H"
                logger.exception("Plot for step %s failed", step_str)

        logger.info("Workflow finished successfully.")

    except (OSError, ValueError, ModuleNotFoundError) as e:
        logger.error("Workflow failed due to a critical error: %s", e)
        raise


if __name__ == "__main__":
    main()
```

## File: src/dlamp/analysis/video_creator.py
```python
# analysis/video_creator.py
"""Provides functionality to create MP4 videos from a sequence of images."""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def create_animation(image_paths: list[Path], output_video_path: Path, framerate: int = 1) -> bool:
    """Creates an MP4 video from a list of image files using ffmpeg.

    Args:
        image_paths (List[Path]): A sorted list of paths to the input images.
        output_video_path (Path): The path to save the output MP4 file.
        framerate (int): The frame rate for the video. Defaults to 1.

    Returns:
        bool: True if the video was created successfully, False otherwise.
    """
    if not image_paths:
        logger.warning("No image paths provided to create_animation. Skipping.")
        return False

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        logger.warning("ffmpeg not found. Cannot create video. Please install ffmpeg.")
        return False

    # Sort paths to ensure correct order in the video
    sorted_paths = sorted(image_paths)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmpfile:
        for img_path in sorted_paths:
            # Use resolve() to get an absolute path for ffmpeg
            tmpfile.write(f"file '{img_path.resolve()}'\n")
        temp_list_path = tmpfile.name

    command = [
        ffmpeg_path,
        "-y",  # Overwrite output file if it exists
        "-r",
        str(framerate),
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        temp_list_path,
        "-c:v",
        "libx264",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt",
        "yuv420p",
        str(output_video_path),
    ]

    try:
        logger.info("Creating animation at %s", output_video_path)
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.info("ffmpeg stdout:\n%s", process.stdout)
        logger.info("Animation created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("ffmpeg failed to create video.")
        logger.error("ffmpeg stderr:\n%s", e.stderr)
        return False
    finally:
        # Clean up the temporary file
        Path(temp_list_path).unlink()
```

## File: src/dlamp/data/preproc/cds_downloader.py
```python
import os
from datetime import UTC, datetime, timedelta

import cdsapi
import xarray as xr
import yaml
from cdo import Cdo


class CDSDataDownloader:
    def __init__(self, yaml_path):
        self.cfg = self._load_config(yaml_path)

        self.cfg_time = self.cfg["share"]["time_control"]
        self.start_t = datetime.strptime(self.cfg_time["start"], self.cfg_time["format"]).replace(tzinfo=UTC)
        self.end_t = datetime.strptime(self.cfg_time["end"], self.cfg_time["format"]).replace(tzinfo=UTC)
        self.a_timestep = timedelta(hours=self.cfg_time["base_step_hours"])
        self.total_steps = ((self.end_t - self.start_t) // self.a_timestep) + 1

        self.io = self.cfg["share"]["io_control"]
        self.base_dir = self.io["base_dir"]
        self.grib_dir = os.path.join(self.base_dir, self.io["grib_subdir"])
        self.netcdf_dir = os.path.join(self.base_dir, self.io["netcdf_subdir"])
        self.prefix = self.io["prefix"]
        self.timestr_fmt = self.prefix["timestr_fmt"]
        os.makedirs(self.grib_dir, exist_ok=True)
        os.makedirs(self.netcdf_dir, exist_ok=True)

        self.area = self.cfg["download"]["area"]
        self.area_list = [
            self.area["north"],
            self.area["west"],
            self.area["south"],
            self.area["east"],
        ]

        self.client = cdsapi.Client()
        self.cdo = Cdo(tempdir="./.cdo_tmp")
        self.cdo.debug = True

    def _load_config(self, yaml_path):
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    def create_timeline(self):
        return [self.start_t + t * self.a_timestep for t in range(self.total_steps)]

    def _build_request(self, dataset, variables, curr_time, levels=None):
        req = {
            "product_type": "reanalysis",
            "year": [curr_time.strftime("%Y")],
            "month": [curr_time.strftime("%m")],
            "day": [curr_time.strftime("%d")],
            "time": [curr_time.strftime("%H:%M")],
            "variable": variables,
            "format": "grib",
        }
        if levels:
            req["pressure_level"] = [str(l) for l in levels]
        if self.area_list:
            req["area"] = self.area_list
        return req

    def invertlat_to_netcdf(self, input_grib: str, output_netcdf: str):
        """
        Using xarray to read grib data, and invert latitude and the data depend on, then
        save the data in netcdf format.
        """
        try:
            ds = xr.open_dataset(input_grib, engine="cfgrib")
            for lat_name in ["latitude", "lat"]:
                if lat_name in ds.dims:
                    ds = ds.sortby(lat_name, ascending=True)
                    break

            ds.to_netcdf(output_netcdf, format="netcdf4")
            ds.close()
        except Exception as e:  # noqa: BLE001 - broad error boundary on data conversion
            print(f"[ERROR] GRIB failed converting: {input_grib}\n{e}")

    def process_download(self, curr_time):
        self.pl = self.cfg["download"]["dataset_upper"]
        self.sl = self.cfg["download"]["dataset_surface"]
        # for i in tqdm(range(self.total_steps), desc="Downloading ERA5", unit="step"):
        # curr_time = self.start_t + i * self.a_timestep
        timestamp = curr_time.strftime(self.timestr_fmt)

        pl_grb = os.path.join(self.grib_dir, f"{self.prefix['upper']}_{timestamp}.grib")
        pl_nc = os.path.join(self.netcdf_dir, f"{self.prefix['upper']}_{timestamp}.nc")
        sl_grb = os.path.join(self.grib_dir, f"{self.prefix['surface']}_{timestamp}.grib")
        sl_nc = os.path.join(self.netcdf_dir, f"{self.prefix['surface']}_{timestamp}.nc")

        if not os.path.exists(pl_grb):
            req = self._build_request(self.pl["title"], self.pl["variables"], curr_time, self.pl.get("levels"))
            self.client.retrieve(self.pl["title"], req).download(pl_grb)
        if not os.path.exists(pl_nc):
            # self.invertlat_to_netcdf(input_grib=pl_grb, output_netcdf=pl_nc)
            self.cdo.invertlat(
                input=pl_grb,
                options="-f nc4 --eccodes",
                output=pl_nc,
            )
        if not os.path.exists(sl_grb):
            req = self._build_request(self.sl["title"], self.sl["variables"], curr_time)
            self.client.retrieve(self.sl["title"], req).download(sl_grb)
        if not os.path.exists(sl_nc):
            # self.invertlat_to_netcdf(input_grib=sl_grb, output_netcdf=sl_nc)
            self.cdo.invertlat(
                input=sl_grb,
                options="-f nc4 --eccodes",
                output=sl_nc,
            )
```

## File: src/dlamp/data/preproc/dlamp_regridder.py
```python
import os
from datetime import UTC, datetime, timedelta

import numpy as np
import xarray as xr
import yaml
from scipy.interpolate import griddata

from dlamp.data.registry.diagnostic_registry import load_diagnostics, sort_diagnostics_by_dependencies


class DataRegridder:
    """
    DataRegridder
    │
    ├── __init__(...)
    ├── build_timeline(...)           # flexible time-control
    ├── process_single_time(...)      # basis: time
    ├── read_netcdf_data(...)         # basis: var
    ├── horizontal_interp(...)        # basis: source_var
    ├── diag_*()                      # basis: target_var
    │
    │
    │
    ├── write_output(...)             # basis: dict
    │
    └── main_process()                # A hot pot put everything-together
    """

    def __init__(self, yaml_path):
        # load YAML configure
        self.cfg = self._load_config(yaml_path)

        # time control
        self.cfg_time = self.cfg["share"]["time_control"]
        self.start_t = datetime.strptime(
            self.cfg_time["start"],
            self.cfg_time["format"],
        ).replace(tzinfo=UTC)
        self.end_t = datetime.strptime(
            self.cfg_time["end"],
            self.cfg_time["format"],
        ).replace(tzinfo=UTC)
        self.a_timestep = timedelta(hours=self.cfg_time["base_step_hours"])
        self.total_steps = ((self.end_t - self.start_t) // self.a_timestep) + 1

        # I/O control
        self.cfg_io = self.cfg["share"]["io_control"]
        self.base_dir = self.cfg_io["base_dir"]
        self.grib_dir = os.path.join(self.base_dir, self.cfg_io["grib_subdir"])
        self.netcdf_dir = os.path.join(self.base_dir, self.cfg_io["netcdf_subdir"])
        self.prefix = self.cfg_io["prefix"]
        self.pl_prefix = self.prefix["upper"]
        self.sl_prefix = self.prefix["surface"]
        # self.regrid_prefix = self.prefix["regrid"]
        self.output_prefix = self.prefix["output"]
        self.timestr_fmt = self.prefix["timestr_fmt"]
        os.makedirs(self.grib_dir, exist_ok=True)
        os.makedirs(self.netcdf_dir, exist_ok=True)

        # preload target grids prevent from open file repeatly
        self.regrid = self.cfg["regrid"]
        self.target_nc = self.regrid["target_nc"]
        self.tgtlon = self.regrid["target_lon"]
        self.tgtlat = self.regrid["target_lat"]
        self.tgtpres = self.regrid["target_pres"]
        self.srclon = self.regrid["source_lon"]
        self.srclat = self.regrid["source_lat"]
        self.srcpres = self.regrid["source_pres"]
        self.pres_levels = self.regrid["levels"]
        self.adopted_varlist = self.regrid["adopted_varlist"]
        self.write_regrid = self.regrid["write_regrid"]
        with xr.open_dataset(self.target_nc, engine="netcdf4") as tgtds:
            self.XLONG = tgtds[self.tgtlon].values
            self.XLAT = tgtds[self.tgtlat].values
            self.static = tgtds[self.adopted_varlist]
            # self.outds = tgtds.copy(deep=True, data=data_vars["XLONG", "XLAT", "pres_levels"])

        # diagnostics module
        self.diagnostics = load_diagnostics(yaml_path)
        self.source_dataset = self.cfg["registry"]["source_dataset"]

    def _load_config(self, yaml_path):
        with open(yaml_path, mode="r") as f:
            return yaml.safe_load(f)

    def build_timeline(self):
        return [self.start_t + t * self.a_timestep for t in range(self.total_steps)]

    def gen_io_filename(self, curr_time):
        timestamp = curr_time.strftime(self.timestr_fmt)
        pl_nc = f"{self.netcdf_dir}/{self.pl_prefix}_{timestamp}.nc"
        sl_nc = f"{self.netcdf_dir}/{self.sl_prefix}_{timestamp}.nc"
        # regrid_nc = f"{self.netcdf_dir}/{self.regrid_prefix}_{timestamp}.nc"
        output_nc = f"{self.netcdf_dir}/{self.output_prefix}_{timestamp}.nc"
        # print(pl_nc, "\n", sl_nc, "\n", regrid_nc, "\n", output_nc)
        return pl_nc, sl_nc, output_nc

    def _interpolate_with_fallback(self, points, values, xi):
        """
        Perform linear interpolation with a nearest-neighbor fallback for NaN values.

        Parameters
        ----------
        points : ndarray
            Coordinates of the source data points.
        values : ndarray
            Values of the source data points.
        xi : tuple
            Coordinates of the target grid.

        Returns
        -------
        ndarray
            Interpolated grid.
        """
        # First, try linear interpolation
        grid_linear = griddata(points, values, xi, method="linear")

        # Check if any NaNs were produced
        nan_mask = np.isnan(grid_linear)

        # If there are NaNs, use nearest neighbor to fill them
        if np.any(nan_mask):
            # Perform nearest interpolation
            grid_nearest = griddata(points, values, xi, method="nearest")
            # Fill in the NaNs from the linear result with values from the nearest result
            grid_linear[nan_mask] = grid_nearest[nan_mask]

        return grid_linear

    def interp_horizontal_v2(self, out_dict, curr_time, src_nc):
        """
        Interpolates data from a source grid to a target grid horizontally.
        Fills NaN values resulting from linear interpolation using the 'nearest' method.

        target_lat: "XLAT"
        target_lon: "XLONG"
        target_pres: "pres_levels"
        source_lat: "lat"
        source_lon: "lon"
        source_pres: "plev"

        Parameters
        ----------
        out_dict : dict
            Dictionary to store the output interpolated data.
        curr_time : datetime or similar
            Current time step being processed.
        src_nc : str or path-like
            Path to the source NetCDF file.

        Returns
        -------
        dict
            The updated dictionary with interpolated data.
        """
        dim_upp = ["Time", "pres_bottom_top", "south_north", "west_east"]
        dim_sfc = ["Time", "south_north", "west_east"]

        with xr.open_dataset(src_nc, engine="netcdf4") as ncds:
            lon = ncds[self.srclon].values
            lat = ncds[self.srclat].values
            if np.ndim(lon) == 1 and np.ndim(lat) == 1:
                lons, lats = np.meshgrid(lon, lat)
            else:
                lons, lats = lon, lat

            # Prepare source points for griddata
            points = np.vstack((lons.ravel(), lats.ravel())).T
            # Prepare target points
            xi = (self.XLONG.ravel(), self.XLAT.ravel())
            _, ny, nx = self.XLONG.shape

            for var in ncds:
                # Skip coordinate variables if they appear in the keys
                if var in [self.srclon, self.srclat, "plev", "time"]:
                    continue

                data = np.squeeze(ncds[var].values)
                print(f"[REGRID] {var} => {data.shape}")

                if data.ndim == 3:
                    nl = data.shape[0]
                    data_h = np.empty((nl, ny, nx))
                    for pl in range(nl):
                        # Use the new interpolation function with fallback
                        interp_data = self._interpolate_with_fallback(points, data[pl].ravel(), xi)
                        data_h[pl] = np.reshape(interp_data, (ny, nx))

                    data_h = np.expand_dims(data_h, axis=0)
                    out_dict[var] = (dim_upp, data_h.astype(np.float32))

                elif data.ndim == 2:
                    # Use the new interpolation function with fallback
                    interp_data = self._interpolate_with_fallback(points, data.ravel(), xi)
                    data_h = np.reshape(interp_data, (ny, nx))
                    data_h = np.expand_dims(data_h, axis=0)

                    out_dict[var] = (dim_sfc, data_h.astype(np.float32))

        return out_dict

    def interp_horizontal(self, out_dict, curr_time, src_nc):
        """
        target_lat: "XLAT"
        target_lon: "XLONG"
        target_pres: "pres_levels"
        source_lat: "lat"
        source_lon: "lon"
        source_pres: "plev"
        Parameters
        ----------
        out_dict : TYPE
            DESCRIPTION.
        curr_time : TYPE
            DESCRIPTION.
        src_nc : TYPE
            DESCRIPTION.

        Returns
        -------
        interp_dict : TYPE
            DESCRIPTION.

        """
        dim_upp = ["Time", "pres_bottom_top", "south_north", "west_east"]
        dim_sfc = ["Time", "south_north", "west_east"]

        with xr.open_dataset(src_nc, engine="netcdf4") as ncds:
            lon = ncds[self.srclon].values
            lat = ncds[self.srclat].values
            if np.ndim(lon) == 1 and np.ndim(lat) == 1:
                lons, lats = np.meshgrid(lon, lat)
            else:
                lons, lats = lon, lat

            points = list(zip(lons.ravel(), lats.ravel()))
            xi = (self.XLONG, self.XLAT)
            _, ny, nx = self.XLONG.shape

            for var in ncds:
                data = np.squeeze(ncds[var].values)
                print(f"[REGRID] {var} => {data.shape}")
                if data.ndim == 3:
                    nl = data.shape[0]
                    data_h = np.empty((nl, ny, nx))
                    for pl in range(nl):
                        data_h[pl] = griddata(points, data[pl].ravel(), xi, method="linear")
                        # if np.isnan(data_h[pl]).any():
                        #     mean_mask = np.nanmean(data_h[pl].ravel())
                        #     data_h[pl][np.isnan(data_h[pl])] = mean_mask
                    data_h = np.expand_dims(data_h, axis=0)

                    out_dict[var] = (dim_upp, data_h.astype(np.float32))

                elif data.ndim == 2:
                    data_h = griddata(points, data.ravel(), xi, method="linear")
                    # if np.isnan(data_h).any():
                    #     mean_mask = np.nanmean(data_h.ravel())
                    #     data_h[np.isnan(data_h)] = mean_mask
                    data_h = np.expand_dims(np.reshape(data_h, (ny, nx)), axis=0)

                    out_dict[var] = (dim_sfc, data_h.astype(np.float32))

        return out_dict

    def process_single_time(self, curr_time):
        print(f"[INFO] Processing single time: {curr_time}")
        [pl_nc, sl_nc, output_nc] = self.gen_io_filename(curr_time)

        out_dict = {}
        out2_dict = {}
        for var in self.static.data_vars:  # Iterate over data_vars, not the Dataset itself
            static_data = self.static[var].values
            out_dict[var] = (self.static[var].dims, static_data)  # Use original dimensions
            out2_dict[var] = (self.static[var].dims, static_data, self.static[var].attrs)

        # Ensure NetCDF files exist, otherwise skip this timestep
        if not os.path.exists(pl_nc) and not os.path.exists(sl_nc):
            print(f"[WARN] Missing NetCDF files for {curr_time}")
            return

        # out_dict = {}
        out_coords = {}
        _, ny, nx = np.shape(self.XLONG)
        test_X = np.reshape(self.XLONG, (ny, nx))
        print(np.shape(test_X))
        # out_dict["XLONG"] = (
        #    ["Time", "south_north", "west_east"],
        #    np.expand_dims(np.reshape(self.XLONG,(ny,nx)))
        # )
        # out_dict["XLAT"] = (
        #    ["Time", "south_north", "west_east"], self.XLAT
        # )
        # out_dict["pres_levels"] = (
        #    ["pres_bottom_top"], self.pres_levels
        # )
        out_coords = {
            "Time": ("Time", [np.datetime64(curr_time)]),
            "pres_bottom_top": ("pres_bottom_top", range(len(self.pres_levels))),  # Dynamically get length
            "south_north": ("south_north", range(ny)),
            "west_east": ("west_east", range(nx)),
        }
        out2_coords = out_coords
        out_attrs = {"title": f"Interpolated dataset at {curr_time}"}
        out2_attrs = {"title": f"Diagnosed and interpolated dataset at {curr_time}"}

        # Horizontally interpolate pressure level data
        if os.path.exists(pl_nc):
            print("[REGRID]: ", pl_nc)
            self.interp_horizontal(out_dict, curr_time, pl_nc)

        # Horizontally interpolate surface level data
        if os.path.exists(sl_nc):
            print("[REGRID]: ", sl_nc)
            self.interp_horizontal(out_dict, curr_time, sl_nc)

        # Add static variables to the interpolation dictionary
        # Ensure correct dimensions for static variables;
        # assuming (Time, south_north, west_east) here
        # out2_dict = {}
        # for var in self.static.data_vars: # Iterate over data_vars, not the Dataset itself
        #    static_data = np.squeeze(self.static[var].values)
        #    out_dict[var] = (self.static[var].dims, static_data) # Use original dimensions
        #    out2_dict[var] = (self.static[var].dims, static_data, self.static[var].attrs)

        # _, ny, nx = np.shape(self.XLONG)
        # out_dict["XLONG"] = (
        #    ["Time", "south_north", "west_east"],
        #    np.expand_dims(np.squeeze(self.XLONG), axis=0)
        # )
        # out_dict["XLAT"] = (
        #    ["Time", "south_north", "west_east"],
        #    np.expand_dims(np.squeeze(self.XLAT), axis=0)
        # )
        # out_dict["pres_levels"] = (
        #    ["pres_bottom_top"], self.pres_levels
        # )
        outds = xr.Dataset(data_vars=out_dict, coords=out_coords, attrs=out_attrs)
        out2ds = xr.Dataset(data_vars=out2_dict, coords=out2_coords, attrs=out2_attrs)
        if self.write_regrid:
            outds.to_netcdf(self.regrid_nc, format="NETCDF4")
            print(f"[DONE] Saved interpolated NetCDF for {curr_time}")
        else:
            print(f"[DONE] interpolated NetCDF for {curr_time} without saving the data")

        # --- Diagnostic variable calculation and output ---

        ordered_vars = sort_diagnostics_by_dependencies(self.diagnostics)
        # out2_dict = {}
        # out2_dict["XLONG"] = out_dict["XLONG"]
        # out2_dict["XLAT"] = out_dict["XLAT"]
        # out2_dict["pres_levels"] = out_dict["pres_levels"]

        for var in ordered_vars:
            if var not in self.diagnostics:  # Skip variables that are just dependencies but not defined as outputs
                continue

            info = self.diagnostics[var]
            requires = info["requires"]
            # print("info requires = ", info, requires)
            diag_func = info["function"]

            if all(req in outds.data_vars or req in outds.coords for req in requires):
                print(f"[DIAGNOSE] Calculating diagnostic: {var}")
                try:
                    # === MODIFIED CALL ===
                    # Pass the source dataset type and the current dataset to the diagnostic function
                    diagnostic_dataarray = diag_func(self.source_dataset, outds)
                    # =====================

                    # Add the calculated diagnostic variable to the dataset
                    out2ds[var] = diagnostic_dataarray
                    print(
                        f"[DIAGNOSE] Calculated {var}, shape: {out2ds[var].shape}, mean: {out2ds[var].values.mean():.4f}"
                    )  # Access value after adding
                    # print(f"[DIAGNOSE] Calculated {var}, shape: {out2ds[var].shape}") # Simpler print

                except Exception as e:  # noqa: BLE001 - broad error boundary on diagnostic calc
                    print(f"[ERROR] Failed to calculate diagnostic {var}: {e}")
                    import traceback

                    traceback.print_exc()
            else:
                # Find missing requirements
                missing = [req for req in requires if req not in outds.data_vars and req not in outds.coords]
                print(
                    f"[WARN] Missing required inputs for diagnostic {var}: {missing}. Skipping calculation for this variable."
                )

        # Save once outside the loop
        out2ds.to_netcdf(output_nc, format="NETCDF4")
        print(f"[DONE] Saved diagnostic NetCDF for {curr_time}")

    def main_process(self):
        for curr_time in self.build_timeline():
            self.process_single_time(curr_time)
```

## File: src/dlamp/data/registry/diagnostic_functions.py
```python
import numpy as np
import xarray as xr


def _create_dataarray(
    data: np.ndarray,
    ds: xr.Dataset,
    var_name: str,
    long_name: str,
    units: str,
) -> xr.DataArray:
    """Build an xarray DataArray with standard coordinates and metadata."""

    # setup default coords
    coords = {"Time": ds["Time"]}
    # coords["pres_bottom_top"] = {}
    dims = ["Time"]

    if var_name == "pres_levels":
        dims.append("pres_bottom_top")
        coords["pres_bottom_top"] = ds["pres_bottom_top"]

    elif var_name in ["XLONG_C", "XLAT_C"]:
        dims += ["corner_south_north", "corner_west_east"]
        coords["corner_south_north"] = ("corner_south_north", np.linspace(-450, 450, 451))
        coords["corner_west_east"] = ("corner_west_east", np.linspace(-450, 450, 451))

    elif data.ndim == 3:
        dims += ["pres_bottom_top", "south_north", "west_east"]
        coords.update(
            {
                "pres_bottom_top": ds["pres_bottom_top"],
                "south_north": ds["south_north"],
                "west_east": ds["west_east"],
            }
        )

    elif data.ndim == 2:
        dims += ["south_north", "west_east"]
        coords.update(
            {
                "south_north": ds["south_north"],
                "west_east": ds["west_east"],
            }
        )

    return xr.DataArray(
        np.expand_dims(data, axis=0).astype(np.float32),
        coords=coords,
        dims=dims,
        name=var_name,
        attrs={
            "long_name": long_name,
            "units": units,
            # "dtype": str(data.dtype),
        },
    )


def sat_vapor_pressure_water(T):  # T in Celsius
    return 6.112 * np.exp((17.67 * T) / (T + 243.5))  # hPa


def diag_z_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Geopotential height = geopotential / g

    """
    g = 9.80665  # Standard gravity constant

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["z"].values) / g
            nc_key = "z_p"

        case "ERA5_r":
            data = np.squeeze(ds["z_p"].values) * g
            nc_key = "z"

        case "RWRF":
            data = np.squeeze(ds["z_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Geopotential Height", "m")


def diag_tk_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Air Temperature [K]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["t"].values)

        case "ERA5_r":
            data = np.squeeze(ds["tk_p"].values)

        case "RWRF":
            data = np.squeeze(ds["tk_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "tk_p", "Air Temperature", "K")


def diag_umet_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-component of wind (Earth-rotated)

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["u"].values)
            nc_key = "umet_p"

        case "ERA5_r":
            data = np.squeeze(ds["umet_p"].values)
            nc_key = "u"

        case "RWRF":
            data = np.squeeze(ds["umet_p"].values)
            nc_key = "umet_p"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "U-component of Wind", "m s-1")


def diag_vmet_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-component of wind (Earth-rotated)

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["v"].values)
            nc_key = "vmet_p"

        case "ERA5_r":
            data = np.squeeze(ds["vmet_p"].values)
            nc_key = "v"

        case "RWRF":
            data = np.squeeze(ds["vmet_p"].values)
            nc_key = "vmet_p"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "V-component of Wind", "m s-1")


def diag_QVAPOR_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific humidity to water vapor mixing ratio

    """

    match source_dataset:
        case "ERA5":
            if "q" in ds:
                q = np.squeeze(ds["q"].values)
                data = q / (1 - q)
            elif "r" in ds and "t" in ds and "pres_levels" in ds:
                # Convert relative humidity to mixing ratio
                rh = np.squeeze(ds["r"].values) / 100.0  # convert to fraction
                t = np.squeeze(ds["t"].values)  # temperature in Kelvin
                p = np.squeeze(ds["pres_levels"].values) * 100  # pressure in Pa

                # Convert temperature to Celsius for vapor pressure calculation
                t_celsius = t - 273.15

                # Saturation vapor pressure (hPa)
                es = sat_vapor_pressure_water(t_celsius)

                # Actual vapor pressure (hPa)
                e = rh * es

                # Mixing ratio
                data = (0.622 * e) / (p / 100.0 - e)  # p/100.0 to convert Pa to hPa
            else:
                data = np.nan

        case "RWRF":
            data = np.squeeze(ds["QVAPOR_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QVAPOR_p", "Water Vapor Mixing Ratio", "kg kg-1")


def diag_QRAIN_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific rain water content to rain water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["crwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QRAIN_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QRAIN_p", "Rain Water Mixing Ratio", "kg kg-1")


def diag_QCLOUD_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific cloud liquid water content to cloud water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["clwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QCLOUD_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QCLOUD_p", "Cloud Water Mixing Ratio", "kg kg-1")


def diag_QSNOW_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific snow water content to snow water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["cswc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QSNOW_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QSNOW_p", "Snow Water Mixing Ratio", "kg kg-1")


def diag_QICE_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific cloud ice content to cloud ice mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["ciwc"].values)
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QICE_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QICE_p", "Cloud Ice Mixing Ratio", "kg kg-1")


def diag_QGRAUP_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Specific graupel water content to graupel water mixing ratio

    """

    match source_dataset:
        case "ERA5":
            q = np.squeeze(ds["q"].values) * 0
            data = q / (1 - q)

        case "RWRF":
            data = np.squeeze(ds["QGRAUP_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "QGRAUP_p", "Graupel Water Mixing Ratio", "kg kg-1")


def diag_QTOTAL_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Total hydrometeors mixing ratio

    """

    match source_dataset:
        case "ERA5":
            qlist = ["clwc", "crwc", "ciwc", "cswc"]
            # Convert each specific humidity to mixing ratio first, then sum them up.
            mixing_ratios = [np.squeeze(ds[q].values) / (1 - np.squeeze(ds[q].values)) for q in qlist]
            data = sum(mixing_ratios)
            nc_key = "QTOTAL_p"

        case "RWRF":
            qlist = ["QCLOUD_p", "QRAIN_p", "QICE_p", "QSNOW_p", "QGRAUP_p"]
            data = sum(np.squeeze(ds[q].values) for q in qlist)
            nc_key = "QTOTAL_p"
        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Total Hydrometeors Mixing Ratio", "kg kg-1")


def diag_wa_p(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    omega [Pa s-1] to w [m s-1]

    """
    Rd = 287.058  # Dry air gas constant J/(kg K)
    g = 9.80665  # Standard gravity constant

    match source_dataset:
        case "ERA5":
            omega = np.squeeze(ds["w"].values)
            tmk = np.squeeze(ds["t"].values)
            plev = np.squeeze(ds["pres_levels"].values * 100)  # pressure in Pa

            if "q" in ds:
                q = np.squeeze(ds["q"].values)
                qvp = q / (1 - q)
            elif "r" in ds and "t" in ds and "pres_levels" in ds:
                # Convert relative humidity to mixing ratio
                rh = np.squeeze(ds["r"].values) / 100.0  # convert to fraction
                t_celsius = tmk - 273.15  # temperature in Celsius

                # Saturation vapor pressure (hPa)
                es = sat_vapor_pressure_water(t_celsius)

                # Actual vapor pressure (hPa)
                e = rh * es

                # Mixing ratio
                qvp = (0.622 * e) / (plev / 100.0 - e)  # plev/100.0 to convert Pa to hPa
            else:
                qvp = np.zeros_like(tmk)  # Default to 0 if no humidity data

            t_virt = tmk * (1 + 0.61 * qvp)

            prs = np.zeros(np.shape(tmk))
            for pl in range(len(plev)):
                prs[pl] = plev[pl]

            data = -1 * omega * Rd * t_virt / prs / g

        case "RWRF":
            data = np.squeeze(ds["wa_p"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "wa_p", "Vertical Velocity", "m s-1")


def diag_T2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Air Temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["2t"].values)

        case "RWRF":
            data = np.squeeze(ds["T2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "T2", "2m Temperature", "K")


def diag_Q2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    water vapor mixing ratio at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            td2 = np.squeeze(ds["2d"].values)
            sp = np.squeeze(ds["sp"].values)
            e = sat_vapor_pressure_water(td2 - 273.15) * 100  # [Pa]
            data = (0.622 * e) / (sp - e)

        case "RWRF":
            data = np.squeeze(ds["Q2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "Q2", "2m Mixing Ratio", "kg kg-1")


def diag_rh2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    relative humidity at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            td2 = np.squeeze(ds["2d"].values)
            t2 = np.squeeze(ds["2t"].values)
            e = sat_vapor_pressure_water(td2 - 273.15) * 100  # [Pa]
            esat = sat_vapor_pressure_water(t2 - 273.15) * 100  # [Pa]
            data = e / esat * 100

        case "RWRF":
            data = np.squeeze(ds["rh2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "rh2", "2m Relative Humidity", "%")


def diag_td2(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["2d"].values)

        case "RWRF":
            data = np.squeeze(ds["td2"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "td2", "2m Dew Point Temperature", "K")


def diag_umet10(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-wind at 10 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["10u"].values)

        case "RWRF":
            data = np.squeeze(ds["umet10"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "umet10", "10m U-component of Wind", "m s-1")


def diag_vmet10(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-wind at 10 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["10v"].values)

        case "RWRF":
            data = np.squeeze(ds["vmet10"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "vmet10", "10m V-component of Wind", "m s-1")


def diag_umet100(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    U-wind at 100 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["100u"].values)
            nc_key = "umet100"

        case "ERA5_r":
            data = np.squeeze(ds["umet100"].values)
            nc_key = "u100m"

        case "RWRF":
            data = np.squeeze(ds["umet100"].values)
            nc_key = "umet100"

        case _:
            data = np.nan
            nc_key = "umet100"

    return _create_dataarray(data, ds, nc_key, "100m U-component of Wind", "m s-1")


def diag_vmet100(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    V-wind at 100 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["100v"].values)
            nc_key = "vmet100"

        case "ERA5_r":
            data = np.squeeze(ds["vmet100"].values)
            nc_key = "v100m"

        case "RWRF":
            data = np.squeeze(ds["vmet100"].values)
            nc_key = "vmet100"

        case _:
            data = np.nan
            nc_key = "vmet100"

    return _create_dataarray(data, ds, nc_key, "100m V-component of Wind", "m s-1")


def diag_slp(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    sea-level pressure at surface [hPa]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["msl"].values) / 100.0

        case "ERA5_r":
            data = np.squeeze(ds["slp"].values) * 100.0

        case "RWRF":
            data = np.squeeze(ds["slp"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "slp", "Sea Level Pressure", "hPa")


def diag_SST(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    sea surface temperature

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["sst"].values)
            nc_key = "SST"
            # sst[np.isnan(sst)] = np.nanmean(sst.ravel())
            # data = sst

        case "ERA5_r":
            data = np.squeeze(ds["SST"].values)
            nc_key = "sst"

        case "RWRF":
            data = np.squeeze(ds["SST"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Sea Surface Temperature", "K")


def diag_PSFC(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    surface pressure [Pa]

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["sp"].values)
            nc_key = "PSFC"

        case "ERA5_r":
            data = np.squeeze(ds["PSFC"].values)
            nc_key = "sp"

        case "RWRF":
            data = np.squeeze(ds["PSFC"].values)
            nc_key = "PSFC"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Surface Pressure", "Pa")


def diag_pw(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["tcwv"].values)
            nc_key = "pw"

        case "ERA5_r":
            data = np.squeeze(ds["pw"].values)
            nc_key = "tcwv"

        case "RWRF":
            data = np.squeeze(ds["pw"].values)
            nc_key = "pw"

        case _:
            data = np.nan

    return _create_dataarray(data, ds, nc_key, "Precipitable Water", "kg m-2")


def diag_PBLH(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    dew-point temperature at 2 m height above surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["blh"].values)

        case "RWRF":
            data = np.squeeze(ds["PBLH"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "PBLH", "Planetary Boundary Layer Height", "m")


def diag_RAINNC(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Total Precipitation

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["tp"].values)

        case "RWRF":
            data = np.squeeze(ds["RAINNC"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "RAINNC", "Total Precipitation", "m")


def diag_SWDOWN(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Downward shortwave radiation at surface

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["ssrd"].values) / 3600

        case "RWRF":
            data = np.squeeze(ds["SWDOWN"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "SWDOWN", "Surface Shortwave Downward Radiation", "W m-2")


def diag_OLR(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Outward longwave radiation at TOA

    """

    match source_dataset:
        case "ERA5":
            data = np.squeeze(ds["ttr"].values) / 3600

        case "RWRF":
            data = np.squeeze(ds["OLR"].values)

        case _:
            data = np.nan

    return _create_dataarray(data, ds, "OLR", "Outgoing Longwave Radiation", "W m-2")


def diag_REFL(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Emulated Radar Reflectivity

    """

    match source_dataset:
        case "ERA5":
            tmk = np.squeeze(ds["t"].values)
            qvp = np.squeeze(ds["q"].values) / (1 - np.squeeze(ds["q"].values))
            qra = np.squeeze(ds["crwc"].values / (1 - ds["crwc"].values))
            qsn = np.squeeze(ds["cswc"].values / (1 - ds["cswc"].values))
            qgr = np.zeros(np.shape(tmk))
            prs = np.zeros(np.shape(tmk))
            plev = np.squeeze(ds["pres_levels"].values)
            for pl in range(len(plev)):
                prs[pl, :, :] = plev[pl] * 100

        case "RWRF":
            tmk = np.squeeze(ds["tk_p"].values)
            qvp = np.squeeze(ds["QVAPOR_p"].values)
            qra = np.squeeze(ds["QRAIN_p"].values)
            qsn = np.squeeze(ds["QSNOW_p"].values)
            qgr = np.squeeze(ds["QGRAUP_p"].values)
            prs = np.zeros(np.shape(tmk))
            plev = np.squeeze(ds["pres_levels"].values)
            for pl in range(len(plev)):
                prs[pl, :, :] = plev[pl] * 100.0

        case _:
            template_shape = ds["t" if "t" in ds else "tk_p"].values.shape
            data = np.full(np.squeeze(template_shape), np.nan)
            return _create_dataarray(data, ds, "REFL", "Emulated Radar Reflectivity", "dBZ")

    sn0 = 1
    ivarint = 1
    qvp = np.maximum(qvp, 0)
    qra = np.maximum(qra, 0)
    qsn = np.maximum(qsn, 0)
    qgr = np.maximum(qgr, 0)

    if sn0 == 1:
        mask = tmk < 273.15
        qsn[mask] = qra[mask]
        qra[mask] = 0

    virtual_t = tmk * (1 + 0.61 * qvp)

    rhoair = prs / (287.04 * virtual_t)  # prs_val.values 假設可以自動廣播

    factor_r = 720 * 1e18 * (1 / (np.pi * 1000)) ** 1.75
    factor_s = factor_r * (0.224 * (100 / 1000) ** 2)
    factor_g = factor_r * (0.224 * (400 / 1000) ** 2)

    z_e = (
        factor_r * (rhoair * qra) ** 1.75 / (8e6 if ivarint == 0 else 1e10) ** 0.75
        + factor_s * (rhoair * qsn) ** 1.75 / (2e7 if ivarint == 0 else 2e8) ** 0.75
        + factor_g * (rhoair * qgr) ** 1.75 / (4e6 if ivarint == 0 else 5e7) ** 0.75
    )

    data = 10 * np.log10(np.maximum(z_e, 0.001))

    return _create_dataarray(data, ds, "REFL", "Emulated Radar Reflectivity", "dBZ")


def diag_MAX_REFL(source_dataset: str, ds: xr.Dataset) -> xr.DataArray:
    """
    Emulated Column Maximum Radar Reflectivity
    """
    REFL = diag_REFL(source_dataset, ds)
    # The dimensions of REFL.values are (Time, pres_bottom_top, south_north, west_east)
    # We take the maximum over the pressure level axis (axis=1)
    _, nl, ny, nx = np.shape(REFL.values)

    data = np.max(np.reshape(REFL.values, (nl, ny, nx)), axis=0)

    return _create_dataarray(data, ds, "MAX_REFL", "Emulated Column Maximum Radar Reflectivity", "dBZ")
```

## File: src/dlamp/data/registry/diagnostic_registry.py
```python
import importlib

import yaml


def load_diagnostics(yaml_path):
    with open(yaml_path, "r") as f:
        cfg = yaml.safe_load(f)

    reg_cfg = cfg["registry"]["varname"]  # .get("varname", "")
    diagnostics = {}

    for name, item in reg_cfg.items():
        func_name = item["function"]
        module = importlib.import_module("dlamp.data.registry.diagnostic_functions")
        func = getattr(module, func_name)
        diagnostics[name] = {
            "requires": item["requires"],
            "function": func,
        }
    return diagnostics


def sort_diagnostics_by_dependencies(diagnostics):
    sorted_list = []
    visited = set()

    def visit(var):
        if var in visited:
            return
        for dep in diagnostics[var]["requires"]:
            if dep in diagnostics:
                visit(dep)
        sorted_list.append(var)
        visited.add(var)

    for var in diagnostics:
        visit(var)

    return sorted_list
```

## File: src/dlamp/datasets/__init__.py
```python
"""Public exports for the datasets subpackage."""

from .custom_dataset import CustomDataset

__all__ = ["CustomDataset"]
```

## File: src/dlamp/datasets/custom_dataset.py
```python
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset

from ..standardizer import Standardizer, get_standardizer
from ..utils import DataCompose, DataGenerator, Level, TimeUtil


class CustomDataset(Dataset):
    def __init__(
        self,
        inp_len: int,
        oup_len: int,
        oup_itv: dict[str, int],
        data_generator: DataGenerator,
        sampling_rate: int,
        init_time_list: list[datetime],
        data_list: list[DataCompose],
        add_time_features: bool,
        use_Kth_hour_pred: int | None,
        is_train_or_valid: bool,
        standardizer: Standardizer | None = None,
    ):
        super().__init__()
        self._ilen = inp_len
        self._olen = oup_len
        self._oitv = timedelta(**oup_itv)
        self._data_gnrt = data_generator
        self._sr = sampling_rate
        self._init_time_list = init_time_list
        self._data_list = data_list
        self.add_time_features = add_time_features
        self.use_Kth_hour_pred = use_Kth_hour_pred
        self._is_train_or_valid = is_train_or_valid
        self._standardizer = standardizer or get_standardizer()

    def __len__(self):
        """
        Returns the length of the `_init_time_list` attribute, which represents
        the number of items in the dataset.
        """
        return len(self._init_time_list) // self._sr if self._is_train_or_valid else len(self._init_time_list)

    def __getitem__(self, index):
        """
        Retrieves input and output data based on the given index.

        Parameters:
            index (int): The index of the item to retrieve.

        Returns:
            tuple: A tuple containing the input and output data.
        """
        if self._is_train_or_valid:
            index *= self._sr
        input_time = self._init_time_list[index]
        input = self._get_variables_from_dt(input_time, is_input=True)

        output_time = input_time + self._oitv
        output = self._get_variables_from_dt(output_time, is_input=False)

        return input, output

    def _get_variables_from_dt(self, dt: datetime, is_input: bool) -> dict[str, np.ndarray]:
        """
        Retrieves data from a given datetime object.

        Parameters:
            dt (datetime): The datetime object to retrieve variables from.
            is_input: If True, it's possible to prepare the datetime features.

        Returns:
            dict: A dictionary containing the variables retrieved from the datetime object.
                The dictionary has the following structure:
                {
                    'upper_air': numpy.ndarray (z, h, w, c),
                    'surface': numpy.ndarray (z, h, w, c)
                }
                Each key in the dictionary corresponds to levels of variables, and the values
                are numpy arrays containing the variables stacked along the specified axis.
        """
        pre_output = defaultdict(list)
        # via traversing data_list, the levels/vars are in the the same order as the
        # order in `config/data/data_config.yaml`
        data_dict = self._data_gnrt.yield_data(dt, self._data_list, use_Kth_hour_pred=self.use_Kth_hour_pred)
        for var_level_str, data in data_dict.items():
            data = self._standardizer.standardize(var_level_str, data)
            _, level = DataCompose.retrive_var_level_from_string(var_level_str)
            if level.is_surface():
                pre_output[Level.Surface].append(data)
            else:
                pre_output[level].append(data)

        # concatenate by variable, group by level
        output = defaultdict(list)
        for level, value in pre_output.items():
            value = np.stack(value, axis=-1)  # (h, w, c)

            if level.is_surface():
                output["surface"].append(value)
            else:
                output["upper_air"].append(value)

        # concatenate by level
        # Warning: LightningModule doesn't support defaultdict as input/output
        final = {}
        for key, value in output.items():
            stack_data = np.stack(value, axis=0)  # (lv, h, w, c)

            if is_input and key == "surface" and self.add_time_features:
                # add DoY and ToD (1, h, w, c+4)
                time_features = TimeUtil.create_time_features(dt, stack_data.shape[1:3])
                stack_data = np.concatenate([stack_data, time_features[None]], axis=-1)

            final[key] = stack_data  # {'upper_air': (lv, h, w, c), ...}

        return final

    def get_internal_index_from_dt(self, dt: datetime) -> int:
        """
        Given a datetime, this function returns the index.

        If `_is_train` is True, the function returns the index directly.
        Otherwise, it returns the index divided by `_sr`.

        Parameters:
            dt (datetime): The datetime object to find the index for.

        Returns:
            int: The index of the datetime object in the `_init_time_list` attribute.
        """
        idx = self._init_time_list.index(dt)
        return idx // self._sr if self._is_train_or_valid else idx

    def average_pooling(self, data: np.ndarray, kernel_size: int = 9, stride: int = 1) -> np.ndarray:
        """
        Applies average pooling to the input data.

        Args:
            data (np.ndarray): The input data to be pooled with shape (lv, h, w, c).
            kernel_size (int, optional): The kernel size for average pooling. Defaults to 9.
            stride (int, optional): The stride for average pooling. Defaults to 1.

        Returns:
            np.ndarray: The pooled data.
        """
        # Convert to PyTorch tensor
        tensor_data = torch.from_numpy(data).float()

        # Reshape to (lv*c, 1, h, w) for avg_pool2d
        lv, h, w, c = tensor_data.shape
        tensor_data = tensor_data.permute(0, 3, 1, 2).contiguous().reshape(lv * c, 1, h, w)

        # Apply average pooling
        pooled_data = F.avg_pool2d(
            tensor_data,
            kernel_size=kernel_size,
            stride=stride,
            padding=kernel_size // 2,
            count_include_pad=False,
        )

        # Reshape back to (lv, h, w, c)
        pooled_data = torch.reshape(pooled_data, (lv, c, h, w)).permute(0, 2, 3, 1).contiguous()

        return pooled_data.numpy()
```

## File: src/dlamp/debug/boundary_plots.py
```python
import os
from datetime import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def plot_bdy_blending_verification(
    pd_data: np.ndarray,
    gt_data: np.ndarray,
    fft_blended_initial: np.ndarray,
    final_data: np.ndarray,
    pd_mask: np.ndarray,
    gt_mask: np.ndarray,
    level_idx: int,
    channel_idx: int,
    dt: datetime,
    method: str,
    save_dir: str = "output/debug_plot",
):
    """Plots the results of boundary blending for verification."""
    l, c = level_idx, channel_idx
    plt.ioff()
    plt.close("all")
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    plt.tight_layout(pad=3.0)
    vmin = min(
        pd_data[0, l, :, :, c].min(),
        gt_data[l, :, :, c].min(),
        fft_blended_initial[l, :, :, c].min(),
        final_data[0, l, :, :, c].min(),
    )
    vmax = max(
        pd_data[0, l, :, :, c].max(),
        gt_data[l, :, :, c].max(),
        fft_blended_initial[l, :, :, c].max(),
        final_data[0, l, :, :, c].max(),
    )

    im = axes[0, 0].imshow(pd_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 0].set_title(f"Original PD Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 0])

    im = axes[0, 1].imshow(gt_data[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 1].set_title(f"Original GT Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 1])

    im = axes[0, 2].imshow(fft_blended_initial[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 2].set_title(f"FFT Blended Initial (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 2])

    pd_mask_stats = f"Max: {pd_mask.max():.2f}, Mean: {pd_mask.mean():.2f}, Min: {pd_mask.min():.2f}"
    im = axes[1, 0].imshow(pd_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 0].set_title(f"Linear Blend PD Mask\n{pd_mask_stats}")
    fig.colorbar(im, ax=axes[1, 0])

    gt_mask_stats = f"Max: {gt_mask.max():.2f}, Mean: {gt_mask.mean():.2f}, Min: {gt_mask.min():.2f}"
    im = axes[1, 1].imshow(gt_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 1].set_title(f"Linear Blend GT Mask\n{gt_mask_stats}")
    fig.colorbar(im, ax=axes[1, 1])

    im = axes[1, 2].imshow(final_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[1, 2].set_title(f"Final Blended (FFT + Linear) (L{l} C{c})")
    fig.colorbar(im, ax=axes[1, 2])

    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"debug_{{dt.strftime('%Y%m%d%H')}}_{method}_L{l}_C{c}.png")
    plt.savefig(save_path)
    plt.close(fig)


def plot_fft_blending_debug(
    pd_slice: np.ndarray,
    gt_slice: np.ndarray,
    fft_pd_slice: np.ndarray,
    fft_gt_slice: np.ndarray,
    lpf_mask: np.ndarray,
    hpf_mask: np.ndarray,
    blended_spatial_slice: np.ndarray,
    level_idx: int,
    channel_idx: int,
    dt: datetime,
    method: str,
    save_dir: str = "output/debug_plot",
):
    """Plots FFT blending debug information."""
    from scipy.fft import ifft2, ifftshift

    l, c = level_idx, channel_idx
    plt.ioff()
    plt.close("all")
    fig_fft, axes_fft = plt.subplots(4, 4, figsize=(24, 24))
    fig_fft.suptitle(f"FFT Blending Debug (L{l}, C{c}, Method: {method}) @ {dt}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- Pre-calculate all components for the grid ---
    # Spatial components
    pd_low_freq_spatial = np.real(ifft2(ifftshift(fft_pd_slice * lpf_mask)))
    pd_high_freq_spatial = np.real(ifft2(ifftshift(fft_pd_slice * hpf_mask)))
    gt_low_freq_spatial = np.real(ifft2(ifftshift(fft_gt_slice * lpf_mask)))
    gt_high_freq_spatial = np.real(ifft2(ifftshift(fft_gt_slice * hpf_mask)))

    # Difference components
    diff_spatial = pd_slice - gt_slice
    diff_freq = np.abs(fft_pd_slice) - np.abs(fft_gt_slice)
    diff_low_freq = pd_low_freq_spatial - gt_low_freq_spatial
    diff_high_freq = pd_high_freq_spatial - gt_high_freq_spatial

    # --- Setup shared color normalization & wavenumber coordinates ---
    # For spatial plots
    spatial_data_list = [
        pd_slice,
        gt_slice,
        pd_low_freq_spatial,
        pd_high_freq_spatial,
        gt_low_freq_spatial,
        gt_high_freq_spatial,
        blended_spatial_slice,
    ]
    vmin_spatial = min(d.min() for d in spatial_data_list)
    vmax_spatial = max(d.max() for d in spatial_data_list)

    # For frequency plots
    vmax_spec = max(np.max(np.abs(fft_pd_slice)), np.max(np.abs(fft_gt_slice)))
    norm_spec = mcolors.LogNorm(vmin=1e-3, vmax=vmax_spec)
    freq_cmap = "plasma"  # Consistent colormap for frequency domain

    # Wavenumber coordinates
    h, w = pd_slice.shape
    k_x_coords = np.arange(w) - (w // 2)
    k_y_coords = np.arange(h) - (h // 2)
    wavenumber_extent = [
        k_x_coords.min(),
        k_x_coords.max(),
        k_y_coords.min(),
        k_y_coords.max(),
    ]

    # For difference plots
    def get_centered_norm(data_array):
        vmax_abs = np.max(np.abs(data_array))
        return mcolors.CenteredNorm(vcenter=0, halfrange=vmax_abs)

    # --- Plotting Grid ---
    # Row 0: Masks and Final Result
    im = axes_fft[0, 0].imshow(blended_spatial_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[0, 0].set_title("[0,0] Final Blended Spatial")
    fig_fft.colorbar(im, ax=axes_fft[0, 0])

    mid_y = lpf_mask.shape[0] // 2
    axes_fft[0, 1].plot(k_x_coords, lpf_mask[mid_y, :], label="LPF")
    axes_fft[0, 1].plot(k_x_coords, hpf_mask[mid_y, :], label="HPF")
    axes_fft[0, 1].set_title("[0,1] LPF/HPF Cross Section")
    axes_fft[0, 1].set_xlabel("Wavenumber k_x")
    axes_fft[0, 1].legend()
    axes_fft[0, 1].grid(True)

    im = axes_fft[0, 2].imshow(
        lpf_mask,
        cmap=freq_cmap,
        vmin=0,
        vmax=1,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[0, 2].set_title("[0,2] LPF Mask (Wavenumber)")
    axes_fft[0, 2].set_xlabel("Wavenumber k_x")
    axes_fft[0, 2].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[0, 2])

    im = axes_fft[0, 3].imshow(
        hpf_mask,
        cmap=freq_cmap,
        vmin=0,
        vmax=1,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[0, 3].set_title("[0,3] HPF Mask (Wavenumber)")
    axes_fft[0, 3].set_xlabel("Wavenumber k_x")
    axes_fft[0, 3].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[0, 3])

    # Row 1: Predicted Data Analysis
    im = axes_fft[1, 0].imshow(pd_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 0].set_title("[1,0] PD Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 0])

    im = axes_fft[1, 1].imshow(
        np.abs(fft_pd_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[1, 1].set_title("[1,1] PD Spectrum (Wavenumber)")
    axes_fft[1, 1].set_xlabel("Wavenumber k_x")
    axes_fft[1, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[1, 1])

    im = axes_fft[1, 2].imshow(pd_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 2].set_title("[1,2] PD Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 2])

    im = axes_fft[1, 3].imshow(pd_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 3].set_title("[1,3] PD High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 3])

    # Row 2: Ground Truth Analysis
    im = axes_fft[2, 0].imshow(gt_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 0].set_title("[2,0] GT Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 0])

    im = axes_fft[2, 1].imshow(
        np.abs(fft_gt_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[2, 1].set_title("[2,1] GT Spectrum (Wavenumber)")
    axes_fft[2, 1].set_xlabel("Wavenumber k_x")
    axes_fft[2, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[2, 1])

    im = axes_fft[2, 2].imshow(gt_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 2].set_title("[2,2] GT Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 2])

    im = axes_fft[2, 3].imshow(gt_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 3].set_title("[2,3] GT High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 3])

    # Row 3: Difference Analysis
    im = axes_fft[3, 0].imshow(diff_spatial, cmap="coolwarm", norm=get_centered_norm(diff_spatial))
    axes_fft[3, 0].set_title("[3,0] Diff Spatial (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 0])

    im = axes_fft[3, 1].imshow(diff_freq, cmap="coolwarm", norm=get_centered_norm(diff_freq))
    axes_fft[3, 1].set_title("[3,1] Diff Spectrum (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 1])

    im = axes_fft[3, 2].imshow(diff_low_freq, cmap="coolwarm", norm=get_centered_norm(diff_low_freq))
    axes_fft[3, 2].set_title("[3,2] Diff Low-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 2])

    im = axes_fft[3, 3].imshow(diff_high_freq, cmap="coolwarm", norm=get_centered_norm(diff_high_freq))
    axes_fft[3, 3].set_title("[3,3] Diff High-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 3])

    # Save the figure
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"debug_fft_{{dt.strftime('%Y%m%d%H')}}_{method}_L{l}_C{c}.png")
    plt.savefig(save_path)
    plt.close(fig_fft)
```

## File: src/dlamp/inference/batch_inference_ckpt.py
```python
import logging
from datetime import UTC, datetime, timedelta

import numpy as np
import torch
from omegaconf import DictConfig
from tqdm import trange

from dlamp.models.lightning_modules import PanguLightningModule
from dlamp.models.model_utils import get_builder
from dlamp.utils import TimeUtil

from .infer_utils import prediction_postprocess
from .inference_base import InferenceBase

log = logging.getLogger(__name__)


class BatchInferenceCkpt(InferenceBase):
    def __init__(self, cfg: DictConfig, eval_cases: list[datetime] | None = None):
        """
        This class can only inference by checkpoint.
        """
        super().__init__(cfg, eval_cases)

    def _setup(self):
        model_builder = get_builder(self.cfg.model.model_name)(
            "predict",
            self.data_list,
            image_shape=self.data_manager.image_shape,
            add_time_features=self.cfg.data.add_time_features,
            **self.cfg.model,
            **self.cfg.lightning,
        )

        self.pl_module = PanguLightningModule.load_from_checkpoint(
            checkpoint_path=self.cfg.inference.best_ckpt,
            test_dataloader=None,
            backbone_model=model_builder._backbone_model(),
        )

        self.pl_module = self.pl_module.cuda()
        self.pl_module.eval()

    def infer(self, bdy_swap_method: dict | None = None):
        """
        Perform batch inference using ONNX runtime.

        This method iterates through the predict dataloader and stores
        intermediat results. The predictions are then post-processed
        and stored as attributes of the class.

        The method performs the following steps:
        1. Initializes data loader and calculates iteration parameters.
        2. Iterates through batches, performing inference for each time step.
        3. Stores intermediate results at specified intervals.
        4. Post-processes the collected results.
        5. Stores the final predictions as class attributes.

        Note:
            The number of iterations and storage interval are determined by
            `self.output_itv` and `self.showcase_length` respectively.
        """
        data_loader = self.data_manager.predict_dataloader()
        interval = self.output_itv // self.data_itv
        predict_iters = (self.showcase_length - 1) * interval

        ret = []
        for batch_id, (input, target) in enumerate(data_loader):
            inp_upper = input["upper_air"].cuda()
            inp_surface = input["surface"].cuda()

            # auto-regression
            tmp_upper, tmp_sfc = [], []
            for step in trange(predict_iters, desc=f"Infer batch {batch_id}"):
                with torch.inference_mode():
                    inp_upper, inp_surface = self.pl_module(inp_upper, inp_surface)
                inp_upper = inp_upper.detach().cpu().numpy()
                inp_surface = inp_surface.detach().cpu().numpy()

                if (step + 1) % interval == 0:
                    tmp_upper.append(inp_upper.copy())
                    tmp_sfc.append(inp_surface.copy())

                curr_time = self.init_time[batch_id] + timedelta(hours=step + 1)
                if self.cfg.data.add_time_features:
                    time_features = TimeUtil.create_time_features(curr_time, inp_surface.shape[2:4])  # (H, W, 4)
                    time_features = np.expand_dims(time_features, axis=(0, 1))
                    inp_surface = np.concatenate((inp_surface, time_features), axis=-1)

                if bdy_swap_method:
                    inp_upper = self._boundary_swapping(
                        inp_upper,
                        curr_time,
                        bdy_swap_method["name"],
                        bdy_swap_method["n_of_grid"],
                    )
                    inp_surface = self._boundary_swapping(
                        inp_surface,
                        curr_time,
                        bdy_swap_method["name"],
                        bdy_swap_method["n_of_grid"],
                    )

                inp_upper = torch.from_numpy(inp_upper).cuda()
                inp_surface = torch.from_numpy(inp_surface).cuda()

            # post-process 1, shape = (1, lv, H, W, c) or (Seq, lv, H, W, c)
            tmp_upper = np.concatenate(tmp_upper, axis=0)
            tmp_sfc = np.concatenate(tmp_sfc, axis=0)
            ret.append(
                (
                    input["upper_air"].cpu().numpy(),
                    input["surface"].cpu().numpy(),
                    target["upper_air"].cpu().numpy(),
                    target["surface"].cpu().numpy(),
                    tmp_upper,
                    tmp_sfc,
                )
            )

        # post-process 2, shape = (B, lv, H, W , c) or (B, Seq, lv, H, W, c)
        mapping = PanguLightningModule.get_product_mapping()
        predictions = prediction_postprocess(ret, mapping)
        for product_type, tensor in predictions.items():
            setattr(self, product_type, tensor)

        log.info(f"Batch inference finished at {datetime.now(UTC)}")
```

## File: src/dlamp/inference/batch_inference_onnx.py
```python
import logging
from datetime import UTC, datetime, timedelta

import numpy as np
from omegaconf import DictConfig
from tqdm import trange

from dlamp.models.lightning_modules import PanguLightningModule
from dlamp.utils import TimeUtil

from .infer_utils import init_ort_instance, prediction_postprocess
from .inference_base import InferenceBase

log = logging.getLogger(__name__)


class BatchInferenceOnnx(InferenceBase):
    def __init__(self, cfg: DictConfig, eval_cases: list[datetime] | None = None):
        """
        This class can only inference by onnx runtime.
        """
        super().__init__(cfg, eval_cases)

    def _setup(self):
        self.ort_sess = init_ort_instance(gpu_id=self.cfg.inference.gpu_id, onnx_path=self.cfg.inference.onnx_path)

        log.info(f"onnx runtime session is ready on GPU {self.cfg.inference.gpu_id}")

    def infer(self, bdy_swap_method: dict | None = None):
        """
        Perform batch inference using ONNX runtime.

        This method iterates through the predict dataloader and stores
        intermediat results. The predictions are then post-processed
        and stored as attributes of the class.

        The method performs the following steps:
        1. Initializes data loader and calculates iteration parameters.
        2. Iterates through batches, performing inference for each time step.
        3. Stores intermediate results at specified intervals.
        4. Post-processes the collected results.
        5. Stores the final predictions as class attributes.

        Note:
            The number of iterations and storage interval are determined by
            `self.output_itv` and `self.showcase_length` respectively.
        """
        data_loader = self.data_manager.predict_dataloader()
        interval = self.output_itv // self.data_itv
        predict_iters = (self.showcase_length - 1) * interval

        ret = []
        for batch_id, (input, target) in enumerate(data_loader):
            inp_upper = input["upper_air"].cpu().numpy()
            inp_surface = input["surface"].cpu().numpy()

            # auto-regression
            tmp_upper, tmp_sfc = [], []
            for step in trange(predict_iters, desc=f"Infer batch {batch_id}"):
                ort_inputs = {
                    self.ort_sess.get_inputs()[0].name: inp_upper,
                    self.ort_sess.get_inputs()[1].name: inp_surface,
                }
                inp_upper, inp_surface = self.ort_sess.run(None, ort_inputs)

                # if (step + 1) % interval == 0:
                #    tmp_upper.append(inp_upper.copy())
                #    tmp_sfc.append(inp_surface.copy())

                curr_time = self.init_time[batch_id] + timedelta(hours=step + 1)
                if self.cfg.data.add_time_features:
                    time_features = TimeUtil.create_time_features(curr_time, inp_surface.shape[2:4])  # (H, W, 4)
                    time_features = np.expand_dims(time_features, axis=(0, 1))
                    inp_surface = np.concatenate((inp_surface, time_features), axis=-1)

                if bdy_swap_method:
                    inp_upper = self._boundary_swapping(
                        inp_upper,
                        curr_time,
                        bdy_swap_method["name"],
                        bdy_swap_method["n_of_grid"],
                    )
                    inp_surface = self._boundary_swapping(
                        inp_surface,
                        curr_time,
                        bdy_swap_method["name"],
                        bdy_swap_method["n_of_grid"],
                    )

                if (step + 1) % interval == 0:
                    tmp_upper.append(inp_upper.copy())
                    tmp_sfc.append(inp_surface.copy())

            # post-process 1, shape = (1, lv, H, W, c) or (Seq, lv, H, W, c)
            tmp_upper = np.concatenate(tmp_upper, axis=0)
            tmp_sfc = np.concatenate(tmp_sfc, axis=0)
            ret.append(
                (
                    input["upper_air"].cpu().numpy(),
                    input["surface"].cpu().numpy(),
                    target["upper_air"].cpu().numpy(),
                    target["surface"].cpu().numpy(),
                    tmp_upper,
                    tmp_sfc,
                )
            )

        # post-process 2, shape = (B, lv, H, W , c) or (B, Seq, lv, H, W, c)
        mapping = PanguLightningModule.get_product_mapping()
        predictions = prediction_postprocess(ret, mapping)
        for product_type, tensor in predictions.items():
            setattr(self, product_type, tensor)

        log.info(f"Batch inference finished at {datetime.now(UTC)}")
```

## File: src/dlamp/inference/inference_base.py
```python
import abc
import warnings
from datetime import datetime, timedelta

import numpy as np
from omegaconf import DictConfig
from scipy.fft import fft2, fftshift, ifft2, ifftshift
from scipy.ndimage import distance_transform_cdt
from tqdm import trange

from dlamp.datasets import CustomDataset
from dlamp.debug.boundary_plots import (
    plot_bdy_blending_verification,
    plot_fft_blending_debug,
)
from dlamp.managers import DataManager, DatetimeManager
from dlamp.standardizer import Standardizer, get_standardizer
from dlamp.utils import DataCompose, DataGenerator, DataType, Level


class InferenceBase(metaclass=abc.ABCMeta):
    def __init__(
        self,
        cfg: DictConfig,
        eval_cases: list[datetime] | None = None,
        standardizer: Standardizer | None = None,
    ):
        # args
        self.cfg = cfg
        self.eval_cases = eval_cases

        # useful properties
        self.data_list = DataCompose.from_config(self.cfg.data.train_data)
        self.data_itv = timedelta(**self.cfg.data.time_interval)
        self.output_itv = timedelta(**self.cfg.inference.output_itv)
        self.showcase_length = self.cfg.plot.figure_columns
        self.pressure_lv: list[Level] = DataCompose.get_all_levels(self.data_list, only_upper=True)
        self.upper_vars: list[DataType] = DataCompose.get_all_vars(self.data_list, only_upper=True)
        self.surface_vars: list[DataType] = DataCompose.get_all_vars(self.data_list, only_surface=True)

        # data manager
        self.init_time_list = self.build_init_time_list()
        self.data_manager = DataManager(
            self.data_list,
            **self.cfg.data,
            **self.cfg.lightning,
            init_time_list=self.init_time_list,
            standardizer=standardizer or get_standardizer(),
        )
        self.data_manager.setup("predict")

        # custom setup
        self._setup()

    def build_init_time_list(self) -> list[datetime] | None:
        """
        Builds a list of initial time for evaluation.

        This function make sure all the initial time are valid during entire showcase length.
        And also make sure their forecast time exists.

        Returns:
            list[datetime | None]: A sorted list of initial times for evaluation.

        Raises:
            ValueError: If the sanity check fails for the initial time or forecast time.

        """
        if self.eval_cases is None:
            warnings.warn(
                "No custom eval cases are provided, using default EVAL_CASES defined in `src.const`.",
                UserWarning,
            )
            return None

        init_time_list = set()
        for eval_case in self.eval_cases:
            for num in range(self.showcase_length):
                fcst_time = eval_case + self.output_itv * num

                if not DatetimeManager.sanity_check(fcst_time, self.data_list):
                    raise ValueError(
                        f"Sanity check failed for fcst time: {fcst_time}, "
                        f"please choose another day instead {eval_case}."
                    )

            init_time_list.add(eval_case)
        return sorted(init_time_list)

    @property
    def init_time(self) -> list[datetime]:
        """
        Since `self.init_time_list` is not always available, this function returns default init times
        used by CustomDataset from `self.data_manager` or `self.init_time_list`
        """
        return (
            self.init_time_list
            if self.init_time_list is not None
            else self.data_manager._predict_dataset._init_time_list
        )

    @abc.abstractmethod
    def _setup(self):
        """
        Prepare all necessary objects for inference when calling `__init__`.
        """
        return NotImplemented

    @abc.abstractmethod
    def infer(self):
        """
        Inference process.
        """
        return NotImplemented

    def _boundary_swapping(
        self,
        data: np.ndarray,
        dt: datetime,
        method: str,
        bdy_grid: int = 8,
        fft_k_critical: int = 16,
        fft_transition_ratio: float = 0.5,
    ) -> np.ndarray:
        """
        Swaps the boundary values of the predicted data with actual values
        from the dataset.

        Args:
            data (np.ndarray): Input data array with shape (batch, level,
                width, height, channel). Batch must be 1.
            dt (datetime): The datetime for which to get the actual values.
            method (str): "exp_decay", "linear", "override",
                "fft_tukey_linear_boundary", "None".
                - "override": Replace boundary with actual values.
                - "linear": Linearly blend boundary values.
                - "exp_decay": Exponentially blend boundary values.
                - "fft_tukey_linear_boundary": First applies a frequency-domain blending,
                                               then performs a "linear" spatial blending
                                               on the boundaries of the FFT-blended result.
                - "None": No boundary swapping.
            bdy_grid (int, optional): Number of pixels to swap for spatial methods. Defaults to 8.
                                      Used for "linear", "exp_decay", "override", and the linear
                                      part of "fft_tukey_linear_boundary".
            fft_k_critical (int, optional): The critical wavenumber (radius in pixels from the
                                            frequency spectrum center) for the FFT-based Tukey filter.
                                            This defines where the filter starts to transition.
                                            Defaults to 16.
            fft_transition_ratio (float, optional): The ratio of the transition width to `fft_k_critical`
                                                    for the FFT-based Tukey filter. E.g., 0.5 means
                                                    the transition width is 0.5 * `fft_k_critical`.
                                                    Defaults to 0.5.

        Returns:
            np.ndarray: Data array with boundary values swapped, same shape as input
                (batch, level, width, height, channel).

        Raises:
            ValueError: If batch size is not 1 or an unknown method is specified.
        """

        # --- Helper function for FFT filter mask generation (nested for self-containment) ---
        def _create_scale_filter_masks(shape, k_critical, transition_width_ratio):
            """
            Creates radially symmetric smooth low-pass and high-pass filter masks
            using a Tukey Window concept for smooth transition in the frequency domain.
            """
            h, w = shape

            # Create a meshgrid representing pixel distances from the center of the frequency spectrum.
            k_x = np.arange(w) - (w // 2)
            k_y = np.arange(h) - (h // 2)
            K_X, K_Y = np.meshgrid(k_x, k_y)

            radius_map = np.sqrt(K_X**2 + K_Y**2)

            # Calculate the inner and outer radii for the Tukey window's transition band
            transition_width = k_critical * transition_width_ratio
            r_inner = k_critical - transition_width / 2
            r_outer = k_critical + transition_width / 2

            r_inner = max(0.0, float(r_inner))  # Ensure non-negative
            max_possible_radius = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
            r_outer = min(float(max_possible_radius), float(r_outer))  # Cap at max possible frequency

            low_pass_mask = np.zeros(shape, dtype=np.float32)

            low_pass_mask[radius_map <= r_inner] = 1.0  # Fully pass region

            # Transition region (Tukey window application)
            transition_indices = (radius_map > r_inner) & (radius_map < r_outer)
            if np.any(transition_indices) and (r_outer - r_inner) > 1e-9:  # Avoid division by zero
                normalized_distance = (radius_map[transition_indices] - r_inner) / (r_outer - r_inner)
                low_pass_mask[transition_indices] = 0.5 * (1 + np.cos(np.pi * normalized_distance))

            high_pass_mask = 1.0 - low_pass_mask

            return low_pass_mask, high_pass_mask

        # --- End of FFT filter helper function ---

        # --- Read debug settings from the config object ---
        plot_cfg = self.cfg.plot.get("test_bdy", {})
        plot_verification = plot_cfg.get("plot_verification", True)
        plot_fft_debug = plot_cfg.get("plot_fft_debug", True)
        debug_level_idx = plot_cfg.get("debug_level_idx", 0)
        debug_channel_idx = plot_cfg.get("debug_channel_idx", 1)

        batch, level, width, height, channel = data.shape
        if batch != 1:
            raise ValueError(f"Only 1 eval case at a time, but got {batch}")

        pd_data = np.copy(data)  # Make a copy of the input predicted data

        dataset: CustomDataset = self.data_manager._predict_dataset
        data_dict = dataset._get_variables_from_dt(dt, is_input=True)
        gt_data = data_dict["surface"] if level == 1 else data_dict["upper_air"]

        if gt_data.shape != pd_data[0].shape:
            warnings.warn(
                f"Shape mismatch between ground truth {gt_data.shape} and "
                f"prediction {pd_data[0].shape}. Boundary swapping may fail "
                f"and data will not be modified for this call."
            )
            return data  # Return original data if shapes don't match

        # --- Spatial Blending Methods ---
        # if method in ["override", "linear", "exp_decay"]:
        gt_mask = np.zeros((width, height), dtype=np.float32)

        if method == "override":
            gt_mask[:bdy_grid, :] = 1.0
            gt_mask[-bdy_grid:, :] = 1.0
            gt_mask[:, :bdy_grid] = 1.0
            gt_mask[:, -bdy_grid:] = 1.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "linear":
            interior_mask = np.ones((width, height), dtype=bool)
            interior_mask[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = dist_from_interior / bdy_grid
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "exp_decay":
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True  # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "fft_tukey":
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True  # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            fft_blended_initial = np.zeros_like(pd_data[0], dtype=np.float32)
            lpf_mask, hpf_mask = _create_scale_filter_masks((width, height), fft_k_critical, fft_transition_ratio)

            pd_fft = np.zeros(pd_data.shape)
            for lv in range(level):
                for ch in range(channel):
                    pd_slice = pd_data[0, lv, :, :, ch]
                    gt_slice = gt_data[lv, :, :, ch]
                    lwn_pd_slice = np.real(ifft2(ifftshift(np.real(fftshift(fft2(pd_slice))) * lpf_mask)))
                    lwn_gt_slice = np.real(ifft2(ifftshift(np.real(fftshift(fft2(gt_slice))) * lpf_mask)))
                    hwn_pd_slice = np.real(ifft2(ifftshift(np.real(fftshift(fft2(pd_slice))) * hpf_mask)))

                    pd_fft[0, lv, :, :, ch] = (lwn_gt_slice * gt_mask) + (lwn_pd_slice * (1 - gt_mask)) + hwn_pd_slice

            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True  # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_fft[0] * pd_mask_b) + (gt_data * gt_mask_b)

        # --- FFT-based Blending Methods (Pure or Combined) ---
        elif method == "fft_tukey0":
            fft_blended_initial = np.zeros_like(pd_data[0], dtype=np.float32)

            lpf_mask, hpf_mask = _create_scale_filter_masks((width, height), fft_k_critical, fft_transition_ratio)

            l = debug_level_idx
            c = debug_channel_idx

            for l_idx in range(level):
                for c_idx in range(channel):
                    pd_slice = pd_data[0, l_idx, :, :, c_idx]
                    gt_slice = gt_data[l_idx, :, :, c_idx]

                    fft_pd_slice = fftshift(fft2(pd_slice))  # pd_data in wavenumber domain
                    fft_gt_slice = fftshift(fft2(gt_slice))  # gt_data in wavenumber domain

                    combined_fft_slice = (fft_gt_slice * lpf_mask) + (fft_pd_slice * hpf_mask)

                    blended_spatial_slice = np.real(ifft2(ifftshift(combined_fft_slice)))
                    fft_blended_initial[l_idx, :, :, c_idx] = blended_spatial_slice

                    if plot_fft_debug and l_idx == l and c_idx == c:
                        plot_fft_blending_debug(
                            pd_slice=pd_slice,
                            gt_slice=gt_slice,
                            fft_pd_slice=fft_pd_slice,
                            fft_gt_slice=fft_gt_slice,
                            lpf_mask=lpf_mask,
                            hpf_mask=hpf_mask,
                            blended_spatial_slice=blended_spatial_slice,
                            level_idx=l,
                            channel_idx=c,
                            dt=dt,
                            method=method,
                        )

            gt_mask_linear = np.zeros((width, height), dtype=np.float32)
            interior_mask_linear = np.ones((width, height), dtype=bool)
            interior_mask_linear[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior_linear = distance_transform_cdt(interior_mask_linear, metric="chessboard")
            gt_mask_linear = dist_from_interior_linear / bdy_grid
            gt_mask_linear = np.clip(gt_mask_linear, 0.0, 1.0)
            gt_mask_linear[gt_mask_linear < 0.01] = 0.0

            pd_mask_linear = 1.0 - gt_mask_linear

            pd_mask_b_linear = pd_mask_linear.reshape(1, width, height, 1)
            gt_mask_b_linear = gt_mask_linear.reshape(1, width, height, 1)

            data[0] = (fft_blended_initial * pd_mask_b_linear) + (gt_data * gt_mask_b_linear)

            if plot_verification:
                plot_bdy_blending_verification(
                    pd_data=pd_data,
                    gt_data=gt_data,
                    fft_blended_initial=fft_blended_initial,
                    final_data=data,
                    pd_mask=pd_mask_linear,
                    gt_mask=gt_mask_linear,
                    level_idx=debug_level_idx,
                    channel_idx=debug_channel_idx,
                    dt=dt,
                    method=method,
                )

        elif method == "None":
            pass

        else:
            raise ValueError(
                f"Unknown Method: {method}. Supported methods are: 'override', 'linear', 'exp_decay', 'fft_tukey_linear_boundary', 'None'."
            )

        return data

    def get_figure_materials(self, case_dt: datetime, data_compose: DataCompose):
        """Get ground truth and prediction data for plotting figures.

        Args:
            case_dt (datetime): The initial datetime to get data for
            data_compose (DataCompose): Configuration specifying the variable and level to retrieve

        Returns:
            tuple[np.ndarray, np.ndarray]: data with shape (showcase_length, H, W)
        """
        input_data = self.get_infer_results_from_dt(case_dt, "input", data_compose)
        output_data = self.get_infer_results_from_dt(case_dt, "output", data_compose)

        # (showcase_length, H, W)
        output_plot_data = np.concatenate((input_data, output_data), axis=0)

        # prepare ground truth data
        data_gnrt: DataGenerator = self.data_manager.data_gnrt
        gt_data = []
        for i in trange(self.showcase_length, desc=f"Get {data_compose} ground truth"):
            curr_time = case_dt + i * self.output_itv
            gt_data.append(data_gnrt.yield_data(curr_time, data_compose))  # (H, W)
        gt_data = np.stack(gt_data, axis=0)  # (showcase_length, H, W)

        return gt_data, output_plot_data

    def get_infer_results_from_dt(self, dt: datetime, phase: str, data_compose: DataCompose) -> np.ndarray:
        """Get inference input/output data for a specific datetime and variable.

        Args:
            dt (datetime): The datetime to get data for.
            phase (str): Either "input" or "output" to specify which data to retrieve.
                The shape of input data is (time, level, height, width, channel).
                The shape of output data is (time, seq_len, level, height, width, channel).
            data_compose (DataCompose): Configuration specifying the variable and level.

        Returns:
            np.ndarray: The requested data array. The output shape are all the same:
                (seq_len, height, width), for input phase, seq_len is 1.

        Raises:
            AssertionError: If phase is not "input" or "output"
            ValueError: If the requested variable or level is not found
        """
        assert phase in ["input", "output"], f"invalid phase: {phase}"
        time_idx = self.init_time.index(dt)
        if data_compose.level.is_surface():
            data = getattr(self, f"{phase}_surface")
            var_idx = self.surface_vars.index(data_compose.var_name)
            return data[time_idx, :, :, :, var_idx] if phase == "input" else data[time_idx, :, 0, :, :, var_idx]
        else:
            data = getattr(self, f"{phase}_upper")
            level_idx = self.pressure_lv.index(data_compose.level)
            var_idx = self.upper_vars.index(data_compose.var_name)
            return (
                data[time_idx, level_idx : level_idx + 1, :, :, var_idx]
                if phase == "input"
                else data[time_idx, :, level_idx, :, :, var_idx]
            )
```

## File: src/dlamp/managers/data_manager.py
```python
import logging
from datetime import datetime

import lightning as L
from torch.utils.data import DataLoader

from ..datasets import CustomDataset
from ..standardizer import Standardizer, get_standardizer
from ..utils import DataCompose, DataGenerator
from .datetime_manager import DatetimeManager

log = logging.getLogger(__name__)


class DataManager(L.LightningDataModule):
    def __init__(
        self,
        data_list: list[DataCompose],
        init_time_list: list[datetime] | None = None,
        standardizer: Standardizer | None = None,
        **kwargs,
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["data_list", "init_time_list", "train_data"])

        # internal property
        self.data_list = data_list
        self.init_time_list = init_time_list
        self._standardizer = standardizer or get_standardizer()
        self._train_dataset = None
        self._valid_dataset = None
        self._test_dataset = None
        self._predict_dataset = None

        # assistants
        self.dtm = DatetimeManager(
            kwargs["start_time"],
            kwargs["end_time"],
            kwargs["format"],
            kwargs["time_interval"],
        )
        self.data_gnrt = DataGenerator(
            kwargs["data_shape"],
            kwargs["image_shape"],
        )

        # flags
        self._already_called: dict[str, bool] = {}
        for stage in ("fit", "validate", "test", "predict"):
            self._already_called[stage] = False

    def setup(self, stage: str):
        """
        Sets up the data for the specified stage.

        This function is called from every process across all the nodes and GPUs.

        Parameters:
            stage (str): The stage for which the data needs to be set up.
                Possible values are "fit", "validate", "test", or "predict".

        Returns:
            None

        Raises:
            NotImplementedError: If the stage is "predict".
            ValueError: If the stage is invalid.
        """
        if self._already_called[stage]:
            log.warning(f'Stage "{stage}" has already been called. Skipping...')
            return

        use_Kth_hour = getattr(self.hparams, "use_Kth_hour_pred", None)
        if not self.dtm.is_done:
            self.dtm.build_initial_time_list(self.data_list, use_Kth_hour).random_split(
                **self.hparams.split_config
            ).build_eval_cases().swap_eval_cases_from_train_valid()
            self.dtm.is_done = True

        match stage:
            case "fit":
                self._train_dataset = self._setup("train")
                self._valid_dataset = self._setup("valid")
            case "validate":
                self._valid_dataset = self._setup("valid")
            case "test":
                self._test_dataset = self._setup("test")
            case "predict":
                self._predict_dataset = self._setup("predict")
            case _:
                log.error(f"Invalid stage: {stage}")
                raise ValueError(f"Invalid stage: {stage}")

        self._already_called[stage] = True
        self.info_log(f'Stage "{stage}" setup done')
        self.info_log(f"Total data collected: {len(self.dtm.time_list)}, Sampling Rate: {self.hparams.sampling_rate}")
        self.info_log(
            f"Training Data Size: {len(self.dtm.train_time) // self.hparams.sampling_rate}, "
            f"Validating Data Size: {len(self.dtm.valid_time) // self.hparams.sampling_rate}, "
            f"Testing Data Size: {len(self.dtm.test_time) // self.hparams.sampling_rate}"
        )
        self.info_log(
            f"Data Shape: {self.hparams.data_shape}, "
            f"Image Shape: {self.image_shape}, "
            f"Batch Size: {self.hparams.batch_size}"
        )

    def _setup(self, stage: str):
        """
        Sets up the `torch.utils.data.Dataset` for the specified stage.

        Parameters:
            stage (str): The stage for which the data needs to be set up.
                Possible values are "train", "valid", "test", or "predict".

        Returns:
            CustomDataset: The subclass of `torch.utils.data.Dataset`.
        """
        ordered_time = (
            sorted(self.init_time_list)
            if stage in ["test", "predict"] and self.init_time_list is not None
            else getattr(self.dtm, f"ordered_{stage}_time")
        )

        return CustomDataset(
            self.hparams.input_len,
            self.hparams.output_len,
            getattr(self.hparams, "output_itv", {"hours": 1}),
            self.data_gnrt,
            self.hparams.sampling_rate,
            ordered_time,
            self.data_list,
            self.hparams.add_time_features,
            getattr(self.hparams, "use_Kth_hour_pred", None),
            is_train_or_valid=stage in ["train", "valid"],
            standardizer=self._standardizer,
        )

    def train_dataloader(self):
        """
        sampler and shuffle can not exist at the same time
        """
        return DataLoader(
            dataset=self._train_dataset,
            shuffle=True,
            batch_size=self.hparams.batch_size,
            num_workers=self.hparams.workers,
            drop_last=False,
        )

    def val_dataloader(self):
        """
        sampler and shuffle can not exist at the same time
        """
        return DataLoader(
            dataset=self._valid_dataset,
            shuffle=False,
            batch_size=self.hparams.batch_size,
            num_workers=self.hparams.workers,
            drop_last=False,
        )

    def test_dataloader(self):
        """
        sampler and shuffle can not exist at the same time
        """
        return DataLoader(
            dataset=self._test_dataset,
            shuffle=False,
            batch_size=self.hparams.batch_size,
            num_workers=self.hparams.workers,
            drop_last=False,
        )

    def predict_dataloader(self):
        """
        sampler and shuffle can not exist at the same time
        """
        return DataLoader(
            dataset=self._predict_dataset,
            shuffle=False,
            batch_size=self.hparams.batch_size,
            num_workers=self.hparams.workers,
            drop_last=False,
        )

    def info_log(self, content: str):
        """
        Logs the given content with the class name prefixed.
        """
        log.info(f"[{self.__class__.__name__}] {content}")

    @property
    def image_shape(self):
        """
        The shape of the input image.

        Returns:
            tuple[int, int]: The shape of the input image in (H, W).
        """
        return self.data_gnrt._img_shp
```

## File: src/dlamp/managers/datetime_manager.py
```python
from __future__ import annotations

import logging
import random
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from ..const import BLACKLIST_PATH, EVAL_CASES
from ..data.source_strategy import NEO171RwrDataSource, get_data_source
from ..runtime_config import get_runtime_config
from ..utils import DataCompose, TimeUtil, gen_path
from .split_strategies import get_split_strategy

log = logging.getLogger(__name__)


class DatetimeManager:
    BC = "[Bottleneck Check]"

    def __init__(
        self,
        start_time: str,
        end_time: str,
        format: str,
        interval: dict[str, int],
    ):
        self.start_time = datetime.strptime(start_time, format).replace(tzinfo=UTC)
        self.end_time = datetime.strptime(end_time, format).replace(tzinfo=UTC)
        self.interval = timedelta(**interval)
        self.format = format

        # internal property
        self.time_list: list[datetime] = []
        self.train_time: set[datetime] = set()
        self.valid_time: set[datetime] = set()
        self.test_time: set[datetime] = set()
        self.eval_cases: set[datetime] = set()
        self._done = False

    def build_initial_time_list(self, data_list: list[DataCompose], use_Kth_hour_pred: int | None) -> DatetimeManager:
        if not Path(BLACKLIST_PATH).exists():
            self._build_init_time_list(data_list, use_Kth_hour_pred, save_output=True)
        else:
            self._quick_build_init_time_list()
        return self

    def _build_init_time_list(
        self,
        data_list: list[DataCompose],
        use_Kth_hour_pred: int | None,
        save_output: bool,
    ) -> None:
        """
        Builds initial time list based on the start time and end time. Eliminates datetime which
        does not meet the sanity check for both current time and next time.

        Args:
            data_list (list[DataCompose]): The list of DataCompose objects.
            use_Kth_hour_pred (int | None): Use Kth hour prediciton to generate the file path
                if not None. Else, use the oringal inital time.
            save_output (bool): Whether to save the blacklist of initial time to a file.

        Returns:
            None
        """
        s = time.time()
        remove = []
        skip_current: bool = False
        num_time = int((self.end_time - self.start_time) / self.interval) + 1
        pbar = tqdm(total=num_time, desc="Building initial time list...")

        current_time = self.start_time
        pbar.update(1)
        while current_time < self.end_time:
            next_time = current_time + self.interval

            if not self.sanity_check(next_time, data_list, use_Kth_hour_pred):
                remove.extend([current_time, next_time])
                current_time += 2 * self.interval
                skip_current = False
                pbar.update(2)
                continue

            # skip checking current time if `skip_current = True`
            if not skip_current and not self.sanity_check(current_time, data_list, use_Kth_hour_pred):
                remove.append(current_time)
                current_time += self.interval
                skip_current = True
                pbar.update(1)
                continue

            self.time_list.append(current_time)
            current_time += self.interval
            skip_current = True
            pbar.update(1)
        pbar.close()

        if save_output:
            with open(BLACKLIST_PATH, "w") as f:
                f.writelines(dt.strftime(self.format) + "\n" for dt in remove)

        log.info(f"Removed {len(remove)} datetimes during data sanity check.")
        log.debug(f"{self.BC} Built initial time list in {time.time() - s:.5f} sec.")

    def _quick_build_init_time_list(self) -> None:
        """
        Builds the initial time list based on the start and end times. Datetimes that are in the
        blacklist are excluded from the time list.
        """
        s = time.time()

        blacklist = []
        with open(BLACKLIST_PATH, "r") as f:
            for line in f:
                dt = datetime.strptime(line.strip(), self.format).replace(tzinfo=UTC)
                blacklist.append(dt)

        num_time = int((self.end_time - self.start_time) / self.interval) + 1
        with tqdm(total=num_time) as pbar:
            pbar.set_description("Building initial time list...")
            current_time = self.start_time
            pbar.update(1)
            while current_time < self.end_time:
                if current_time not in blacklist:
                    self.time_list.append(current_time)
                current_time += self.interval
                pbar.update(1)

        log.info(f"Removed {len(blacklist)} datetimes during data sanity check.")
        log.debug(f"{self.BC} Built initial time list in {time.time() - s:.5f} sec.")

    def random_split(self, ratios: list[float | int], split_method: str = "random") -> DatetimeManager:
        """
        Split the time list into train, validation and test sets based on specified ratios and method.

        Args:
            ratios (list[float | int]): List of 3 numbers specifying the ratio split between
                train, validation and test sets. Will be normalized to sum to 1.
            split_method (str, optional): Method to use for splitting. Options are:
                - "random": Randomly shuffle and split based on ratios
                - "sequential": Split sequentially in chunks based on ratios
                - "half_month": Split by half-month periods, e.g. 1/1-1/15, 1/16-1/30.
                Defaults to "random".

        Returns:
            DatetimeManager: Returns self for method chaining.
        """
        s = time.time()
        assert len(ratios) == 3, f"ratios should be [train_r, valid_r, test_r], but {ratios}"

        strategy = get_split_strategy(split_method)
        self.train_time, self.valid_time, self.test_time = strategy.split(self.time_list, ratios)

        log.debug(f"{self.BC} Split data in {time.time() - s:.5f} sec.")
        log.debug(f"train_time size (original): {len(self.train_time)}")
        log.debug(f"valid_time size (original): {len(self.valid_time)}")
        log.debug(f"test_time size (original): {len(self.test_time)}")
        return self

    def build_eval_cases(self) -> DatetimeManager:
        """
        Builds the evaluation cases from `src.const.EVAL_CASES`. Note that all evaluation cases
        must have existed in the initial time list. These cases are blacklisted from the training set.

        Returns:
            DatetimeManager: The updated DatetimeManager object with the evaluation cases removed.
        """
        days_map = {
            "one_day": 1,
            "three_days": 3,
            "five_days": 5,
            "seven_days": 7,
        }

        s = time.time()
        for key, value in EVAL_CASES.items():
            n_days = days_map.get(key)

            if n_days is None:
                raise RuntimeError(f"Invalid days: {key}")

            for dt in value:
                self.eval_cases |= set(TimeUtil.N_days_time_list(dt.year, dt.month, dt.day, self.interval, n_days))

        self.eval_cases &= set(self.time_list)
        log.debug(f"{self.BC} Built eval case list in {time.time() - s:.5f} sec.")
        log.debug(f"eval case list size: {len(self.eval_cases)}")
        return self

    @staticmethod
    def sanity_check(
        dt: datetime,
        data_list: list[DataCompose],
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        """
        Parameters:
            dt (datetime): The target parent directory to check.
            data_list (list[DataCompose]): A list of DataCompose objects representing the data.
            use_Kth_hour_pred (int | None): Use Kth hour prediciton to generate the file path
                if not None. Else, use the oringal inital time.

        Returns:
            bool: True if all target data files exist, False otherwise.
        """
        config = get_runtime_config()
        source = get_data_source(config.data_source)
        if isinstance(source, NEO171RwrDataSource):
            data_filename_generator = (gen_path(dt, data) for data in data_list)
            while True:
                try:
                    data_filename = next(data_filename_generator)
                    if not data_filename.exists():
                        return False
                except StopIteration:
                    return True
        else:
            # CWA/ERA5 prepared data is self-consistent in every NetCDF file,
            # so only the file existence is checked here.
            return source.gen_path(dt, config, use_Kth_hour_pred=use_Kth_hour_pred).exists()

    def swap_eval_cases_from_train_valid(self) -> DatetimeManager:
        """
        Swaps evaluation cases from the train and valid sets.

        Returns:
            DatetimeManager: The updated DatetimeManager object after swapping the evaluation cases.
        """
        no_swap: bool = len(self.test_time) == 0

        def fn(name: str) -> None:
            dataset = getattr(self, f"{name}_time")
            clashes = dataset & self.eval_cases

            for dt in clashes:
                dataset.remove(dt)
                self.test_time.add(dt)

                if no_swap:
                    continue
                while True:
                    swap_dt = random.choice(list(self.test_time))
                    if swap_dt not in self.eval_cases:
                        self.test_time.remove(swap_dt)
                        dataset.add(swap_dt)
                        break

            log.info(f"Swapped {len(clashes)} eval cases from {name} to test.")

        s = time.time()
        fn("train")
        fn("valid")
        log.debug(f"{self.BC} Swapped eval cases in {time.time() - s:.5f} sec.")
        return self

    @property
    def ordered_train_time(self) -> list[datetime]:
        return sorted(self.train_time)

    @property
    def ordered_valid_time(self) -> list[datetime]:
        return sorted(self.valid_time)

    @property
    def ordered_test_time(self) -> list[datetime]:
        return sorted(self.test_time)

    @property
    def ordered_predict_time(self) -> list[datetime]:
        return sorted(self.eval_cases)

    @property
    def is_done(self) -> bool:
        return self._done

    @is_done.setter
    def is_done(self, new_value: bool) -> None:
        self._done = new_value
```

## File: src/dlamp/models/architectures/drop_path.py
```python
from torch import nn

"""
Copy from timm.models.layers
"""

__all__ = ["DropPath"]


def drop_path(x, drop_prob: float = 0.0, training: bool = False, scale_by_keep: bool = True):
    """Drop paths (Stochastic Depth) per sample (when applied in main path of residual blocks).

    This is the same as the DropConnect impl I created for EfficientNet, etc networks, however,
    the original name is misleading as 'Drop Connect' is a different form of dropout in a separate paper...
    See discussion: https://github.com/tensorflow/tpu/issues/494#issuecomment-532968956 ... I've opted for
    changing the layer and argument names to 'drop path' rather than mix DropConnect as a layer name and use
    'survival rate' as the argument.

    """
    if drop_prob == 0.0 or not training:
        return x
    keep_prob = 1 - drop_prob
    shape = (x.shape[0],) + (1,) * (x.ndim - 1)
    random_tensor = x.new_empty(shape).bernoulli_(keep_prob)
    if keep_prob > 0.0 and scale_by_keep:
        random_tensor.div_(keep_prob)
    return x * random_tensor


class DropPath(nn.Module):
    """Drop paths (Stochastic Depth) per sample  (when applied in main path of residual blocks)."""

    def __init__(self, drop_prob: float = 0.0, scale_by_keep: bool = True):
        super().__init__()
        self.drop_prob = drop_prob
        self.scale_by_keep = scale_by_keep

    def forward(self, x):
        return drop_path(x, self.drop_prob, self.training, self.scale_by_keep)

    def extra_repr(self):
        return f"drop_prob={round(self.drop_prob, 3):0.3f}"
```

## File: src/dlamp/models/architectures/earth_3d_specifics_test.py
```python
import unittest
from math import prod
from typing import ClassVar

import numpy as np
import torch

from ..model_utils import window_partition_3d
from .earth_3d_specifics import (
    EarthAttention3D,
    EarthSpecificBlock,
    EarthSpecificLayer,
)


class EarthAttention3DTest(unittest.TestCase):
    input_shape: ClassVar[list[int]] = [8, 140, 180]
    dim = 192
    heads = 6
    dropout_rate = 0.15
    window_size: ClassVar[list[int]] = [2, 4, 4]

    def test_earth_specific_bias(self):
        earth_attn_3d = EarthAttention3D(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
        )

        total_movement = (
            earth_attn_3d.win_Z**2  # absolute movement in Z-axis
            * earth_attn_3d.win_H**2  # absolute movement in H-axis
            * (2 * earth_attn_3d.win_W - 1)  # relative movement in W-axis
        )

        self.assertEqual(len({x.item() for x in earth_attn_3d.position_index}), total_movement)

    def test_earth_attn_output_shape(self):

        earth_attn_3d = EarthAttention3D(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
        )

        # input_tensor: shape of (B, img_Z, img_H, img_W, C)
        input_tensor = torch.randn([1] + self.input_shape + [self.dim])
        input_window = window_partition_3d(input_tensor, self.window_size, combine_img_dim=True)
        orig_shape = input_window.shape
        output_window = earth_attn_3d(input_window)
        self.assertEqual(output_window.shape, orig_shape)


class EarthSpecificBlockTest(unittest.TestCase):
    input_shape: ClassVar[list[int]] = [8, 140, 180]
    dim = 192
    heads = 6
    drop_path_ratio = 0.1
    dropout_rate = 0.15
    window_size: ClassVar[list[int]] = [2, 4, 4]

    def test_earth_specific_block_output_shape(self):
        for is_rolling in [True, False]:
            earth_specific_block = EarthSpecificBlock(
                input_shape=self.input_shape,
                dim=self.dim,
                heads=self.heads,
                drop_path_ratio=self.drop_path_ratio,
                dropout_rate=self.dropout_rate,
                window_size=self.window_size,
                is_rolling=is_rolling,
            )

            # input_tensor: shape of (B, img_Z*img_H*img_W, C)
            input_tensor = torch.randn([1] + [prod(self.input_shape)] + [self.dim])
            output_tensor = earth_specific_block(input_tensor)
            self.assertEqual(output_tensor.shape, input_tensor.shape)

    def test_wrong_input_shape(self):
        with self.assertRaises(AssertionError):
            EarthSpecificBlock(
                input_shape=[8, 141, 181],
                dim=self.dim,
                heads=self.heads,
                drop_path_ratio=self.drop_path_ratio,
                dropout_rate=self.dropout_rate,
                window_size=self.window_size,
                is_rolling=False,
            )


class EarthSpecificLayerTest(unittest.TestCase):
    input_shape: ClassVar[list[int]] = [8, 140, 180]
    dim = 192
    heads = 6
    depth = 2
    drop_path_ratio_list = np.linspace(0, 0.2, depth)
    dropout_rate = 0.15
    window_size: ClassVar[list[int]] = [2, 4, 4]

    def test_earth_specific_layer_output_shape(self):
        earth_specific_layer = EarthSpecificLayer(
            input_shape=self.input_shape,
            dim=self.dim,
            heads=self.heads,
            depth=self.depth,
            drop_path_ratio_list=self.drop_path_ratio_list,
            dropout_rate=self.dropout_rate,
            window_size=self.window_size,
        )

        # input_tensor: shape of (B, img_Z*img_H*img_W, C)
        input_tensor = torch.randn([1] + [prod(self.input_shape)] + [self.dim])
        output_tensor = earth_specific_layer(input_tensor)
        self.assertEqual(output_tensor.shape, input_tensor.shape)


if __name__ == "__main__":
    # CLI: python -m src.models.architectures.earth_3d_specifics_test
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    loader.testMethodPrefix = "test_"  # prefix for test methods

    suite.addTests(loader.loadTestsFromTestCase(EarthAttention3DTest))
    suite.addTests(loader.loadTestsFromTestCase(EarthSpecificBlockTest))
    suite.addTests(loader.loadTestsFromTestCase(EarthSpecificLayerTest))

    ### add single test by loader
    # suite.addTest(loader.loadTestsFromName(f"{__name__}.EarthAttention3DTest.test_earth_specific_bias"))

    ### add single test by TestCase
    # suite.addTest(EarthAttention3DTest("test_attn_output_shape"))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
```

## File: src/dlamp/models/architectures/earth_3d_specifics.py
```python
import torch
from einops import rearrange, repeat
from torch import nn

from ..model_utils import (
    crop_pad_3d,
    is_divisible_elementwise,
    pad_3d,
    window_partition_3d,
    window_reverse_3d,
)
from .drop_path import DropPath
from .multilayer_perceptron import MultilayerPerceptron


class EarthSpecificLayer(nn.Module):
    def __init__(
        self,
        input_shape: tuple[int],
        dim: int,
        heads: int,
        depth: int,
        drop_path_ratio_list: list[float],
        dropout_rate: float,
        window_size: tuple[int],
        skip_concat: bool = False,
    ) -> None:
        """
        Basic layer of the network.

        Args:
            input_shape (tuple[int]): The shape of the input tensor (inp_Z, inp_H, inp_W).
            dim (int): The dimension of the input tensor after patch embedding.
            heads (int): The number of heads in the multi-head attention layer.
            depth (int): The number of blocks in this layer.
            drop_path_ratio_list (list[float]): The drop path ratio for each block.
            dropout_rate (float): The dropout rate.
            window_size (tuple[int]): The window size with shape (win_Z, win_H, win_W).
            skip_concat (bool, optional): Whether the input x is concatenated with the skip
                connection tensors. Defaults to False.

        Raises:
            AssertionError: If the length of drop_path_ratio_list is not equal to depth.

        Returns:
            None
        """
        assert len(drop_path_ratio_list) == depth, "length of drop_path_ratio_list should be equal to depth"
        super().__init__()

        self.depth = depth
        self.blocks = nn.ModuleList(
            EarthSpecificBlock(
                input_shape=input_shape,
                dim=dim,
                heads=heads,
                drop_path_ratio=drop_path_ratio_list[i],
                dropout_rate=dropout_rate,
                window_size=window_size,
                is_rolling=(i % 2 == 1),
                reduce_dim=(i == 0 and skip_concat),
            )
            for i in range(depth)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Tensor of shape (batch_size, inp_Z*inp_H*inp_W, dim).
        Returns:
            torch.Tensor: Tensor of shape (batch_size, inp_Z*inp_H*inp_W, dim).
        """
        for i in range(self.depth):
            x = self.blocks[i](x)
        return x


class EarthSpecificBlock(nn.Module):
    def __init__(
        self,
        input_shape: tuple[int],
        dim: int,
        heads: int,
        drop_path_ratio: float,
        dropout_rate: float,
        window_size: tuple[int],
        is_rolling: bool,
        reduce_dim: bool,
    ) -> None:
        """
        3D transformer block with Earth-Specific bias and window attention,
        see https://github.com/microsoft/Swin-Transformer for the official implementation of 2D window attention.
        The major difference is that we expand the dimensions to 3 and replace the relative position bias with Earth-Specific bias.

        Args:
            input_shape (tuple[int]): The shape of the input tensor whose dimensions are (inp_Z, inp_H, inp_W). The input
                tensor represents a 3D image after patch embedding.
            dim (int): The dimension of the input tensor.
            heads (int): The number of attention heads.
            drop_path_ratio (float): The ratio of the drop path.
            dropout_rate (float): The dropout rate.
            window_size (tuple[int]): The size of the window whose dimensions are (win_Z, win_H, win_W).
            is_rolling (bool): Whether to use shifted window attention.
            reduce_dim (bool): Whether to divide the dimension by 2 due to the concatenation of the skip connection.

        Returns:
            None
        """
        assert is_divisible_elementwise(input_shape, window_size), (
            f"Input shape must be divisible by window_size {window_size}, but {input_shape} "
            "cannot be divided by it. \nIn the future, undivisible input shape is accepted only "
            "when `self.pad` and `self.crop` are implemented. One must take the padding mask "
            "into consideration when generating the attention mask. e.g. if not roll: pad_mask; "
            "if roll: pad_mask + attn_mask."
        )
        super().__init__()

        inp_dim = dim * 2 if reduce_dim else dim
        self.drop_path = DropPath(drop_prob=drop_path_ratio)
        self.norm1 = nn.LayerNorm(inp_dim)
        self.norm2 = nn.LayerNorm(dim)
        self.MLP = MultilayerPerceptron(inp_dim, 0, reduce_dim)
        self.attention = EarthAttention3D(
            dim=inp_dim,
            input_shape=input_shape,
            heads=heads,
            dropout_rate=dropout_rate,
            window_size=window_size,
        )

        self.is_rolling = is_rolling
        self.input_shape = input_shape
        self.window_size = window_size
        self.pad = pad_3d(input_shape, window_size)
        self.crop = crop_pad_3d(input_shape, window_size)
        if is_rolling:
            mask = self._gen_3d_attn_mask(input_shape, window_size)
            self.register_buffer("attn_mask", mask)
        self.reduce_dim = reduce_dim

    def _gen_3d_attn_mask(
        self,
        input_shape: tuple[int, int, int],
        window_size: tuple[int, int, int],
    ) -> torch.Tensor:
        """
        Generates a 3D attention mask tensor based on the given image shape and window size.

        see https://github.com/microsoft/Swin-Transformer for the official implementation of 2D window attention.

        Args:
            input_shape (tuple[int, int, int]): The shape of the image tensor (inp_Z, inp_H, inp_W).
            window_size (tuple[int, int, int]): The size of the sliding window (win_Z, win_H, win_W).

        Returns:
            torch.Tensor: The 3D attention mask tensor with shape (num_windows, win_Z*win_H*win_W, win_Z*win_H*win_W)
        """
        shift_size = tuple(i // 2 for i in window_size)
        img_mask = torch.zeros(1, input_shape[0], input_shape[1], input_shape[2], 1)
        z_slices = (
            slice(0, -window_size[0]),
            slice(-window_size[0], -shift_size[0]),
            slice(-shift_size[0], None),
        )
        h_slices = (
            slice(0, -window_size[1]),
            slice(-window_size[1], -shift_size[1]),
            slice(-shift_size[1], None),
        )
        w_slices = (
            slice(0, -window_size[2]),
            slice(-window_size[2], -shift_size[2]),
            slice(-shift_size[2], None),
        )
        cnt = 0
        for z in z_slices:
            for h in h_slices:
                for w in w_slices:
                    img_mask[:, z, h, w, :] = cnt
                    cnt += 1
        mask_windows = window_partition_3d(img_mask, window_size)
        mask_windows = mask_windows.reshape(-1, window_size[0] * window_size[1] * window_size[2])
        attn_mask = mask_windows.unsqueeze(1) - mask_windows.unsqueeze(2)
        attn_mask = attn_mask.masked_fill(attn_mask != 0, (-100.0))
        attn_mask = attn_mask.masked_fill(attn_mask == 0, 0.0)

        return attn_mask

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        Returns:
            torch.Tensor: Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        """
        shortcut = x
        inp_Z, inp_H, inp_W = self.input_shape
        x = rearrange(x, "b (z h w) c -> b z h w c", z=inp_Z, h=inp_H, w=inp_W)

        # backward shift
        if self.is_rolling:
            x = x.roll(shifts=[-i // 2 for i in self.window_size], dims=(1, 2, 3))

        # x: shape of (B * num_windows, win_Z*win_H*win_W, dim)
        x = window_partition_3d(x, self.window_size, combine_img_dim=True)

        # Apply 3D window attention with Earth-Specific bias
        x = self.attention(x, getattr(self, "attn_mask", None))

        # x: shape of (B, inp_Z, inp_H, inp_W, dim)
        x = window_reverse_3d(x, self.window_size, self.input_shape, from_combine_dim=True)

        # forward shift
        if self.is_rolling:
            x = x.roll(shifts=[i // 2 for i in self.window_size], dims=(1, 2, 3))

        x = rearrange(x, "b z h w c -> b (z h w) c")
        x = shortcut + self.drop_path(self.norm1(x))
        residual = self.drop_path(self.norm2(self.MLP(x)))
        x = residual if self.reduce_dim else x + residual
        return x


class EarthAttention3D(nn.Module):
    def __init__(
        self,
        input_shape: tuple[int],
        dim: int,
        heads: int,
        dropout_rate: float,
        window_size: tuple[int],
    ) -> None:
        """
        3D window attention with the Earth-Specific bias,
        see https://github.com/microsoft/Swin-Transformer for the official implementation of 2D window attention.

        Args:
            input_shape (tuple[int]): The shape of the input tensor whose dimensions are (inp_Z, inp_H, inp_W).
                The input tensor represents a 3D image after patch embedding.
            dim (int): The dimension of the input tensor.
            heads (int): The number of attention heads.
            dropout_rate (float): The dropout rate.
            window_size (tuple[int]): The size of the window whose dimensions are (win_Z, win_H, win_W).

        Returns:
            None
        """
        assert is_divisible_elementwise([dim], [heads]), f"dim {dim} must be divisible by heads {heads}"
        super().__init__()

        self.linear1 = nn.Linear(dim, dim * 3, bias=True)
        self.linear2 = nn.Linear(dim, dim)
        self.softmax = nn.Softmax(dim=-1)
        self.dropout = nn.Dropout(dropout_rate)
        self.window_size = window_size
        self.num_head = heads
        self.dim = dim
        self.scale = (dim // heads) ** 0.5

        self.win_Z, self.win_H, self.win_W = window_size
        self.num_Z, self.num_H, self.num_W = map(lambda x, y: x // y, input_shape, window_size)

        # Record the number of different windows of the entire domain
        self.type_of_windows = self.num_Z * self.num_H

        # For each window, we will construct a set of parameters according to the paper
        self.earth_specific_bias = torch.empty(
            size=(
                (2 * self.win_W - 1) * self.win_H**2 * self.win_Z**2,
                self.type_of_windows,
                heads,
            ),
            dtype=torch.float32,
        )
        self.earth_specific_bias = nn.Parameter(self.earth_specific_bias)
        self.earth_specific_bias = nn.init.trunc_normal_(self.earth_specific_bias, std=0.02)

        self.register_buffer("position_index", self._construct_index())

    def _construct_index(self) -> torch.Tensor:
        """This function construct the position index to reuse symmetrical parameters of the position bias"""
        coords_zi = torch.arange(self.win_Z)
        coords_zj = -torch.arange(self.win_Z) * self.win_Z
        coords_hi = torch.arange(self.win_H)
        coords_hj = -torch.arange(self.win_H) * self.win_H
        coords_w = torch.arange(self.win_W)

        # Change the order of the index to calculate the index in total
        coords_1 = torch.stack(torch.meshgrid(coords_zi, coords_hi, coords_w, indexing="ij"), dim=0)
        coords_2 = torch.stack(torch.meshgrid(coords_zj, coords_hj, coords_w, indexing="ij"), dim=0)
        coords_flatten_1 = torch.flatten(coords_1, start_dim=1)
        coords_flatten_2 = torch.flatten(coords_2, start_dim=1)
        coords = coords_flatten_1[:, :, None] - coords_flatten_2[:, None, :]
        coords = rearrange(coords, "d1 d2 d3 -> d2 d3 d1")

        # Shift the index for each dimension to start from 0 and non-repetitive
        coords[:, :, 2] += self.win_W - 1
        coords[:, :, 1] *= 2 * self.win_W - 1
        coords[:, :, 0] *= (2 * self.win_W - 1) * self.win_H**2

        position_index = coords.sum(-1)
        position_index = position_index.flatten()
        return position_index

    def forward(self, x: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Tensor of shape (B*num_windows, win_Z*win_H*win_W, dim)
                where num_windows = num_Z*num_H*num_W.
            mask (torch.Tensor): Tensor of shape (num_windows, win_Z*win_H*win_W, win_Z*win_H*win_W).
        Returns:
            torch.Tensor: Tensor of shape (B*num_windows, win_Z*win_H*win_W, dim).
                where num_windows = num_Z*num_H*num_W.
        """
        orig_shape = x.shape
        x = self.linear1(x)  # (B*num_windows, win_Z*win_H*win_W, dim*3)
        query, key, value = rearrange(
            x, "b zhw (qkv n_h d) -> qkv b n_h zhw d", qkv=3, n_h=self.num_head
        )  # [3](B*num_windows, num_head, win_Z*win_H*win_W, dim//num_head)
        attention = (query @ key.transpose(-2, -1)) / self.scale

        # EarthSpecificBias: shape of ((win_Z*win_H*win_W)^2, type_of_windows, num_head)
        EarthSpecificBias = self.earth_specific_bias[self.position_index]

        # EarthSpecificBias: shape of (type_of_windows, num_head, win_Z*win_H*win_W, win_Z*win_H*win_W)
        EarthSpecificBias = rearrange(
            EarthSpecificBias,
            "(zhw1 zhw2) t_w n_h-> t_w n_h zhw1 zhw2",
            zhw1=self.win_Z * self.win_H * self.win_W,
        )

        # Repeat the learnable bias to the same shape as the attention matrix
        # EarthSpecificBias: shape of (B*num_windows, num_head, win_Z*win_H*win_W, win_Z*win_H*win_W)
        EarthSpecificBias = repeat(
            EarthSpecificBias,
            "t_w n_h zhw1 zhw2 ->  (f t_w) n_h zhw1 zhw2",
            f=orig_shape[0] // self.type_of_windows,
        )

        attention += EarthSpecificBias

        if mask is not None:
            mask = repeat(
                mask,
                "n_w zhw1 zhw2 -> (batch n_w) zhw1 zhw2",
                batch=orig_shape[0] // (self.type_of_windows * self.num_W),
            )
            attention += mask[::, None]

        attention = self.softmax(attention)
        attention = self.dropout(attention)
        x = (attention @ value).transpose(1, 2).reshape(orig_shape)
        x = self.linear2(x)
        x = self.dropout(x)
        return x
```

## File: src/dlamp/models/architectures/glide_unet.py
```python
import torch
from torch import Tensor, nn

from .unet import AttentionBlock, ResidualBlock, Swish, TimeEmbedding

__all__ = ["GlideUNet"]


class DownBlock(nn.Module):
    """
    ### Down block
    This combines `ResidualBlock` and `AttentionBlock`. These are used in the first half of U-Net at each resolution.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        time_channels: int,
        has_attn: bool,
        orig_channels: int,
    ):
        super().__init__()
        self.has_attn = has_attn
        self.res = ResidualBlock(in_channels, out_channels, time_channels)
        if has_attn:
            self.attn = AttentionBlock(out_channels)
            self.cond_proj = nn.Conv2d(orig_channels, out_channels, kernel_size=(1, 1))
        else:
            self.attn = nn.Identity()

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor):
        # return `cond` so the behavior is the same as Downsample
        x = self.res(x, t)
        if self.has_attn:
            cond_transform = self.cond_proj(cond)
            x += cond_transform
        x = self.attn(x)
        return x, cond


class UpBlock(nn.Module):
    """
    ### Up block
    This combines `ResidualBlock` and `AttentionBlock`. These are used in the second half of U-Net at each resolution.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        time_channels: int,
        has_attn: bool,
        orig_channels: int,
    ):
        super().__init__()
        # The input has `in_channels + out_channels` because we concatenate the output of the same resolution
        # from the first half of the U-Net
        self.has_attn = has_attn
        self.res = ResidualBlock(in_channels + out_channels, out_channels, time_channels)
        if has_attn:
            self.attn = AttentionBlock(out_channels)
            self.cond_proj = nn.Conv2d(orig_channels, out_channels, kernel_size=(1, 1))
        else:
            self.attn = nn.Identity()

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor):
        x = self.res(x, t)
        if self.has_attn:
            cond_transform = self.cond_proj(cond)
            x += cond_transform
        x = self.attn(x)
        return x, cond


class MiddleBlock(nn.Module):
    """
    ### Middle block
    It combines a `ResidualBlock`, `AttentionBlock`, followed by another `ResidualBlock`.
    This block is applied at the lowest resolution of the U-Net.
    """

    def __init__(self, n_channels: int, time_channels: int, orig_channels: int):
        super().__init__()
        self.res1 = ResidualBlock(n_channels, n_channels, time_channels)
        self.attn = AttentionBlock(n_channels)
        self.res2 = ResidualBlock(n_channels, n_channels, time_channels)
        self.cond_proj = nn.Conv2d(orig_channels, n_channels, kernel_size=(1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor):
        x = self.res1(x, t)
        cond_transform = self.cond_proj(cond)
        x += cond_transform
        x = self.attn(x)
        x = self.res2(x, t)
        return x


class Downsample(nn.Module):
    """
    ### Scale down the feature map by $\frac{1}{2} \times$
    """

    def __init__(self, n_channels: int, orig_channels: int):
        super().__init__()
        self.conv_x = nn.Conv2d(n_channels, n_channels, (3, 3), (2, 2), (1, 1))
        self.conv_cond = nn.Conv2d(orig_channels, orig_channels, (3, 3), (2, 2), (1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor):
        # `t` is not used, but it's kept in the arguments because for the attention layer function signature
        # to match with `ResidualBlock`.
        _ = t
        x = self.conv_x(x)
        cond = self.conv_cond(cond)
        return x, cond


class Upsample(nn.Module):
    """
    ### Scale up the feature map by $2 \times$
    """

    def __init__(self, n_channels, orig_channels):
        super().__init__()
        self.conv_x = nn.ConvTranspose2d(n_channels, n_channels, (4, 4), (2, 2), (1, 1))

        # If you are using attention(cond information) not only at the last layer,
        # you need to turn on `self.conv_cond` and cond = self.conv_cond(cond) to
        # upsample the cond.

        # self.conv_cond = nn.ConvTranspose2d(orig_channels, orig_channels, (4, 4), (2, 2), (1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor):
        # `t` is not used, but it's kept in the arguments because for the attention layer function signature
        # to match with `ResidualBlock`.
        _ = t
        _ = cond
        # cond = self.conv_cond(cond)
        x = self.conv_x(x)
        return x, cond


class GlideUNet(nn.Module):
    def __init__(
        self,
        image_channels: int,
        hidden_dim: int,
        ch_mults: tuple[int, ...] | list[int] = (1, 2, 2, 4),
        is_attn: tuple[bool, ...] | list[int] = (False, False, True, True),
        n_blocks: int = 2,
    ):
        """
        * `image_channels` is the number of channels in the image. $3$ for RGB.
        * `hidden_dim` is number of channels in the initial feature map that we transform the image into
        * `ch_mults` is the list of channel numbers at each resolution. The number of channels is `ch_mults[i] * n_channels`
        * `is_attn` is a list of booleans that indicate whether to use attention at each resolution
        * `n_blocks` is the number of `UpDownBlocks` at each resolution
        """
        super().__init__()

        # Number of resolutions
        n_resolutions = len(ch_mults)

        # Project image into feature map
        self.image_proj = nn.Conv2d(image_channels, hidden_dim, kernel_size=(3, 3), padding=(1, 1))

        # Time embedding layer. Time embedding has `n_channels * 4` channels
        time_channels = hidden_dim * 4
        self.time_emb = TimeEmbedding(time_channels)

        # #### First half of U-Net - decreasing resolution
        down = []
        # Number of channels
        out_channels = in_channels = hidden_dim
        # For each resolution
        for i in range(n_resolutions):
            # Number of output channels at this resolution
            out_channels = in_channels * ch_mults[i]
            # Add `n_blocks`
            for _ in range(n_blocks):
                down.append(DownBlock(in_channels, out_channels, time_channels, is_attn[i], hidden_dim))
                in_channels = out_channels
            # Down sample at all resolutions except the last
            if i < n_resolutions - 1:
                down.append(Downsample(in_channels, hidden_dim))

        # Combine the set of modules
        self.down = nn.ModuleList(down)

        # Middle block
        self.middle = MiddleBlock(out_channels, time_channels, hidden_dim)

        # #### Second half of U-Net - increasing resolution
        up = []
        # Number of channels
        in_channels = out_channels
        # For each resolution
        for i in reversed(range(n_resolutions)):
            # `n_blocks` at the same resolution
            for _ in range(n_blocks):
                up.append(UpBlock(in_channels, out_channels, time_channels, is_attn[i], hidden_dim))
            # Final block to reduce the number of channels
            out_channels = in_channels // ch_mults[i]
            up.append(UpBlock(in_channels, out_channels, time_channels, is_attn[i], hidden_dim))
            in_channels = out_channels
            # Up sample at all resolutions except last
            if i > 0:
                up.append(Upsample(in_channels, hidden_dim))

        # Combine the set of modules
        self.up = nn.ModuleList(up)

        # Final normalization and convolution layer
        self.norm = nn.GroupNorm(8, hidden_dim)
        self.act = Swish()
        self.final = nn.Conv2d(in_channels, image_channels, kernel_size=(3, 3), padding=(1, 1))

    def forward(self, x: Tensor, t: Tensor, cond: Tensor) -> Tensor:
        """
        * `x` has shape `[batch_size, in_channels, height, width]`
        * `t` has shape `[batch_size]`
        * `cond` has shape `[batch_size, in_channels, height, width]`
        """

        # Get time-step embeddings
        t = self.time_emb(t)

        # Get image projection
        x = self.image_proj(x)
        cond = self.image_proj(cond)

        # Add condition at the beginning
        x += cond

        # `h` will store outputs at each resolution for skip connection
        h = [x]
        # First half of U-Net
        for m in self.down:
            x, cond = m(x, t, cond)
            h.append(x)

        # Middle (bottom)
        x = self.middle(x, t, cond)

        # Second half of U-Net
        for m in self.up:
            if not isinstance(m, Upsample):
                # Get the skip connection from first half of U-Net and concatenate
                s = h.pop()
                x = torch.cat((x, s), dim=1)
            x, cond = m(x, t, cond)

        # Final normalization and convolution
        return self.final(self.act(self.norm(x)))
```

## File: src/dlamp/models/architectures/pangu_model_test.py
```python
import unittest
from copy import deepcopy
from typing import ClassVar

import torch
import yaml

from dlamp.models import PanguModel


class PanguModelTest(unittest.TestCase):
    with open("config/model/dlamp_train.yaml", "r") as file:
        model_config = yaml.safe_load(file)

    TEST_CASE: ClassVar[dict] = deepcopy(model_config)
    TEST_CASE["image_shape"] = [224, 224]  # noqa: RUF012
    TEST_CASE["upper_levels"] = 6
    TEST_CASE["upper_channels"] = 4
    TEST_CASE["surface_channels"] = 1
    TEST_CASE.pop("model_name")

    def test_pangu_output_shape(self):
        device = torch.device(0) if torch.cuda.is_available() else torch.device("cpu")
        model = PanguModel(**self.TEST_CASE).to(device)

        # input_tensor: shape of (B, img_Z, img_H, img_W, Ch)
        x_upper = torch.randn((16, 6, 224, 224, 4)).to(device)
        x_surface = torch.randn((16, 1, 224, 224, 1)).to(device)

        with torch.no_grad():
            y_upper, y_surface = model(x_upper, x_surface)

        self.assertEqual(x_upper.shape, y_upper.shape)
        self.assertEqual(x_surface.shape, y_surface.shape)


if __name__ == "__main__":
    # CLI: python -m src.models.architectures.pangu_model_test
    unittest.main(verbosity=2)
```

## File: src/dlamp/models/architectures/pangu_model.py
```python
import logging
from math import ceil
from pathlib import Path

import numpy as np
import torch
from einops import rearrange, repeat
from sklearn.preprocessing import MinMaxScaler
from torch import nn

from ...const import LAND_SEA_MASK_PATH, TOPOGRAPHY_MASK_PATH
from ..model_utils import (
    crop_pad_2d,
    crop_pad_3d,
    is_divisible_elementwise,
    pad_2d,
    pad_3d,
)
from .earth_3d_specifics import EarthSpecificLayer
from .smoothing import SegmentedSmoothingV2

__all__ = ["PanguModel"]

log = logging.getLogger(__name__)


class PanguModel(nn.Module):
    """
    Implementing https://github.com/198808xc/Pangu-Weather
    """

    def __init__(
        self,
        image_shape: tuple[int, int],
        patch_size: tuple[int, int, int],
        window_size: tuple[int, int, int],
        upper_levels: int,
        upper_channels: int,
        surface_input_channels: int,
        surface_output_channels: int,
        embed_dim: int,
        heads: list[int],
        depths: list[int],
        max_drop_path_ratio: float,
        dropout_rate: float,
        smoothing_kernel_size: int | None = None,
        segmented_smooth_boundary_width: int | None = None,
    ) -> None:
        assert len(heads) == len(depths)
        super().__init__()

        self.hierarchy = len(depths)
        image_shape = [upper_levels] + image_shape
        inp_Z, inp_H, inp_W = [ceil(x / y) for x, y in zip(image_shape, patch_size)]
        inp_Z += 1  # surface
        drop_path_list = np.linspace(0, max_drop_path_ratio, sum(depths)).tolist()
        embed_dim = [(2**i) * embed_dim for i in range(self.hierarchy)]

        if smoothing_kernel_size is None:
            self.smoothing_layer = Identity()
        else:
            assert smoothing_kernel_size % 2 == 1
            if segmented_smooth_boundary_width:
                smoothing_func = SegmentedSmoothingV2(
                    kernel_size=smoothing_kernel_size,
                    boundary_width=segmented_smooth_boundary_width,
                )
            else:
                smoothing_func = nn.AvgPool3d(
                    kernel_size=(1, smoothing_kernel_size, smoothing_kernel_size),
                    stride=(1, 1, 1),
                    padding=(0, smoothing_kernel_size // 2, smoothing_kernel_size // 2),
                    count_include_pad=False,
                )

            self.smoothing_layer = SmoothingBlock(smoothing_func=smoothing_func)

        # ===== Left Side of Unet =====#
        self.patch_embed = PatchEmbedding(
            img_shape=image_shape,
            patch_size=patch_size,
            upper_channels=upper_channels,
            surface_channels=surface_input_channels,
            dim=embed_dim[0],
        )

        for i, depth in enumerate(depths):
            slice_range = slice(sum(depths[:i]), sum(depths[: i + 1]))
            self.__setattr__(
                f"layer{i + 1}",
                EarthSpecificLayer(
                    input_shape=(inp_Z, ceil(inp_H / (2**i)), ceil(inp_W / (2**i))),
                    dim=embed_dim[i],
                    heads=heads[i],
                    depth=depth,
                    drop_path_ratio_list=drop_path_list[slice_range],
                    dropout_rate=dropout_rate,
                    window_size=window_size,
                ),
            )

            if i < self.hierarchy - 1:
                self.__setattr__(
                    f"downsample{i + 1}",
                    DownSample(
                        inp_shape=(inp_Z, ceil(inp_H / (2**i)), ceil(inp_W / (2**i))),
                        dim=embed_dim[i],
                    ),
                )

        # ===== Right Side of Unet =====#
        self.patch_recover = PatchRecovery(
            img_shape=image_shape,
            inp_shape=(inp_Z, inp_H, inp_W),
            patch_size=patch_size,
            upper_channels=upper_channels,
            surface_channels=surface_output_channels,
            dim=embed_dim[0],
        )

        for i, depth in enumerate(reversed(depths), start=1):
            j = self.hierarchy - i  # reversed index
            slice_range = slice(sum(depths[:j]), sum(depths[: j + 1]))
            self.__setattr__(
                f"layer{i + self.hierarchy}",
                EarthSpecificLayer(
                    input_shape=(inp_Z, ceil(inp_H / (2**j)), ceil(inp_W / (2**j))),
                    dim=embed_dim[j],
                    heads=heads[j],
                    depth=depth,
                    drop_path_ratio_list=drop_path_list[slice_range],
                    dropout_rate=dropout_rate,
                    window_size=window_size,
                    skip_concat=(i != 1),
                ),
            )

            if i < self.hierarchy:
                self.__setattr__(
                    f"upsample{i + self.hierarchy}",
                    UpSample(
                        inp_shape=(inp_Z, ceil(inp_H / (2**j)), ceil(inp_W / (2**j))),
                        dim=embed_dim[j],
                    ),
                )

    def forward(self, input_upper: torch.Tensor, input_surface: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Unet structure.

        Args:
            input_upper (torch.Tensor): Tensor of shape (B, img_Z, img_H, img_W, Ch_upper).
            input_surface (torch.Tensor): Tensor of shape (B, 1, img_H, img_W, Ch_surface).
        Returns:
            tuple[torch.Tensor, torch.Tensor]: Tuple of upper-air data and surface data.
        """
        # Initial embedding
        input_upper, input_surface = self.smoothing_layer(input_upper, input_surface)
        x = self.patch_embed(input_upper, input_surface)
        skip = x

        # Store skip connections
        skip_connections = []

        # Encoder (left side)
        for i in range(self.hierarchy - 1):
            x = getattr(self, f"layer{i + 1}")(x)
            skip_connections.append(x)
            x = getattr(self, f"downsample{i + 1}")(x)

        # Bottleneck
        x = getattr(self, f"layer{self.hierarchy}")(x)

        # Decoder (right side)
        for i in range(self.hierarchy - 1):
            layer_idx = self.hierarchy + i + 1
            x = getattr(self, f"layer{layer_idx}")(x)
            x = getattr(self, f"upsample{layer_idx}")(x)
            x = torch.cat([skip_connections.pop(), x], dim=-1)

        # Final layer
        x = getattr(self, f"layer{2 * self.hierarchy}")(x)

        # Recovery and smoothing
        x += skip
        output_upper, output_surface = self.patch_recover(x)
        output_upper, output_surface = self.smoothing_layer(output_upper, output_surface)
        return output_upper, output_surface


class Identity(nn.Module):
    """
    Identity layer. Replace smoothing layer when smoothing_kernel_size is None.
    """

    def forward(self, x_upper: torch.Tensor, x_surface: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        return x_upper, x_surface


class SmoothingBlock(nn.Module):
    def __init__(
        self,
        smoothing_func: nn.Module,
    ) -> None:
        """
        Smooths horizontal dimensions of the upper and surface data with average pooling
        """
        super().__init__()
        self.smoothing_func = smoothing_func

    def forward(self, x_upper: torch.Tensor, x_surface: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x_upper = rearrange(x_upper, "b z h w c -> b c z h w")
        x_surface = rearrange(x_surface, "b 1 h w c -> b c 1 h w")

        x_upper = self.smoothing_func(x_upper)
        x_surface = self.smoothing_func(x_surface)

        x_upper = rearrange(x_upper, "b c z h w -> b z h w c")
        x_surface = rearrange(x_surface, "b c 1 h w -> b 1 h w c")
        return x_upper, x_surface


class PatchEmbedding(nn.Module):
    def __init__(
        self,
        img_shape: tuple[int, int, int],
        patch_size: tuple[int, int, int],
        upper_channels: int,
        surface_channels: int,
        dim: int,
    ) -> None:
        """
        Convert input fields to patches and linearly embed them.

        Args:
            img_shape (tuple[int, int, int]): The shape of unpatched data which is (img_Z, img_H, img_W).
            patch_size (tuple[int, int, int]): Size of the patch (pat_Z, pat_H, pat_W).
            upper_channels (int): The number of channels in the upper_air data.
            surface_channels (int): The number of channels in the surface data.
            dim (int): The dimension of the embedded output.

        Raises:
            NotImplementedError: If constant masks are provided.

        Returns:
            None
        """
        super().__init__()

        if Path(LAND_SEA_MASK_PATH).exists() and Path(TOPOGRAPHY_MASK_PATH).exists():
            land_mask = torch.from_numpy(np.load(LAND_SEA_MASK_PATH).astype(np.float32))
            topography_mask = torch.from_numpy(np.load(TOPOGRAPHY_MASK_PATH).astype(np.float32))
            # Scale and shift to the range of [0, 1]
            scaler = MinMaxScaler().fit(topography_mask.reshape(-1, 1))
            scale = scaler.scale_.astype(np.float32)
            min = scaler.min_.astype(np.float32)
            topography_mask = topography_mask * scale + min
            additional_channels = 2
        else:
            land_mask, topography_mask = None, None
            additional_channels = 0
        self.register_buffer("land_mask", land_mask)
        self.register_buffer("topography_mask", topography_mask)

        # Use convolution to partition data into cubes
        self.conv_upper = nn.Conv3d(
            in_channels=upper_channels,
            out_channels=dim,
            kernel_size=patch_size,
            stride=patch_size,
        )

        self.conv_surface = nn.Conv2d(
            in_channels=surface_channels + additional_channels,
            out_channels=dim,
            kernel_size=patch_size[1:],
            stride=patch_size[1:],
        )

        if not is_divisible_elementwise(img_shape, patch_size):
            log.warning(f"Input shape {img_shape} is not divisible by patch shape {patch_size}, padding is applied.")
        self.upper_pad = pad_3d(img_shape, patch_size)
        self.surface_pad = pad_2d(img_shape[1:], patch_size[1:])

    def forward(self, input_upper: torch.Tensor, input_surface: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_upper (torch.Tensor): Tensor of shape (B, img_Z, img_H, img_W, Ch_upper).
            input_surface (torch.Tensor): Tensor of shape (B, 1, img_H, img_W, Ch_surface).
        Returns:
            torch.Tensor: Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        """
        if self.land_mask is not None and self.topography_mask is not None:
            batch_size = input_surface.shape[0]
            input_surface = torch.cat(
                [
                    input_surface,
                    repeat(self.land_mask, "h w -> b 1 h w 1", b=batch_size),
                    repeat(self.topography_mask, "h w -> b 1 h w 1", b=batch_size),
                ],
                dim=-1,
            )

        # Pad the input to make it divisible by patch_size
        input_upper = self.upper_pad(rearrange(input_upper, "b z h w c -> b c z h w"))
        input_surface = self.surface_pad(rearrange(input_surface, "b z h w c -> (b z) c h w"))

        # shape: (B, dim, inp_Z-1, inp_H, inp_W)
        embedding_upper = self.conv_upper(input_upper)
        # shape: (B, dim, inp_H, inp_W)
        embedding_surface = self.conv_surface(input_surface)
        # shape: (B, dim, inp_Z, inp_H, inp_W)
        x = torch.cat([embedding_upper, embedding_surface[:, :, None]], dim=2)
        # shape: (B, inp_Z*inp_H*inp_W, dim)
        x = rearrange(x, "b c z h w -> b (z h w) c")

        return x


class PatchRecovery(nn.Module):
    def __init__(
        self,
        img_shape: tuple[int, int, int],
        inp_shape: tuple[int, int, int],
        patch_size: tuple[int, int, int],
        upper_channels: int,
        surface_channels: int,
        dim: int,
    ) -> None:
        """
        Recover the output fields from patches.

        Args:
            img_shape (tuple[int, int, int]): The shape of the unpatched image (img_Z, img_H, img_W).
            inp_shape (tuple[int, int, int]): The shape of the patched input tensor (inp_Z, inp_H, inp_W).
            patch_size (tuple[int, int, int]): The size of the patches (patch_Z, patch_H, patch_W).
            upper_channels (int): The number of channels in the upper_air data.
            surface_channels (int): The number of channels in the surface data.
            dim (int): The dimension of the patched input tensor.

        Returns:
            None
        """
        super().__init__()
        # Hear we use two transposed convolutions to recover data
        self.conv_upper = nn.ConvTranspose3d(
            in_channels=dim,
            out_channels=upper_channels,
            kernel_size=patch_size,
            stride=patch_size,
        )
        self.conv_surface = nn.ConvTranspose2d(
            in_channels=dim,
            out_channels=surface_channels,
            kernel_size=patch_size[1:],
            stride=patch_size[1:],
        )
        self.inp_shape = inp_shape
        self.upper_crop = crop_pad_3d(img_shape, patch_size)
        self.surface_crop = crop_pad_2d(img_shape[1:], patch_size[1:])

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x (torch.Tensor): Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        Returns:
            tuple[torch.Tensor, torch.Tensor]: Tuple of upper-air data (B, img_Z, img_H, img_W, Ch_upper)
                and surface data (B, 1, img_H, img_W, Ch_surface)
        """
        inp_Z, inp_H, inp_W = self.inp_shape
        x = rearrange(x, "b (z h w) c -> b c z h w", z=inp_Z, h=inp_H, w=inp_W).contiguous()

        # Deconvolve to original size
        output_upper = self.conv_upper(x[:, :, :-1, :, :])
        output_surface = self.conv_surface(x[:, :, -1, :, :])

        # Crop the output to remove zero-paddings
        output_upper = output_upper[:, :, self.upper_crop[0], self.upper_crop[1], self.upper_crop[2]]
        output_surface = output_surface[:, :, self.surface_crop[0], self.surface_crop[1]]

        # shape: (B, img_Z, img_H, img_W, Ch)
        output_upper = rearrange(output_upper, "b c z h w -> b z h w c")
        output_surface = rearrange(output_surface, "b c h w -> b 1 h w c")
        return output_upper, output_surface


class DownSample(nn.Module):
    def __init__(self, inp_shape: tuple[int, int, int], dim: int):
        """
        Implementation of `SwinPatchMerging`. Reduces the lateral resolution by a factor of 2.

        Args:
            inp_shape (tuple[int, int, int]): Shape of the input tensor (inp_Z, inp_H, inp_W).
            dim (int): Number of input channels.
        """
        super().__init__()
        self.inp_shape = inp_shape
        self.linear = nn.Linear(4 * dim, 2 * dim, bias=False)
        self.norm = nn.LayerNorm(4 * dim)

        # Pad to make H and W divisible by 2
        self.pad = pad_2d((inp_shape[1], inp_shape[2]), (2, 2))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        Returns:
            torch.Tensor: Tensor of shape (B, inp_Z*inp_H/2*inp_W/2, 2*dim).
        """
        x = rearrange(
            x,
            "b (z h w) c -> b c z h w",
            z=self.inp_shape[0],
            h=self.inp_shape[1],
            w=self.inp_shape[2],
        )
        x = self.pad(x)
        x = rearrange(
            x,
            "b c z (hh n1) (ww n2) -> b (z hh ww) (n1 n2 c)",
            n1=2,
            n2=2,
        )
        x = self.linear(self.norm(x))
        return x


class UpSample(nn.Module):
    def __init__(self, inp_shape: tuple[int, int, int], dim: int):
        """
        Increases the lateral resolution by a factor of 2.

        Args:
            inp_shape (tuple[int, int, int]): Shape of the input tensor (inp_Z, inp_H, inp_W).
            dim (int): Number of input channels BEFORE the upsampling.
        """
        super().__init__()
        self.linear1 = nn.Linear(dim, 2 * dim, bias=False)
        self.linear2 = nn.Linear(dim // 2, dim // 2, bias=False)
        self.norm = nn.LayerNorm(dim // 2)
        self.inp_shape = inp_shape

        # Calculate output shape dimensions
        out_H = inp_shape[1] * 2
        out_W = inp_shape[2] * 2

        # Rollback to the original resolution without padding
        self.crop = crop_pad_2d((out_H, out_W), (2, 2))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): Tensor of shape (B, inp_Z*inp_H*inp_W, dim).
        Returns:
            torch.Tensor: Tensor of shape (B, inp_Z*inp_H*2*inp_W*2, dim/2).
        """
        x = self.linear1(x)
        x = rearrange(
            x,
            "b (z hh ww) (n1 n2 c) -> b z (hh n1) (ww n2) c",
            z=self.inp_shape[0],
            hh=self.inp_shape[1],
            ww=self.inp_shape[2],
            n1=2,
            n2=2,
        )
        x = x[:, :, self.crop[0], self.crop[1], :]
        x = rearrange(x, "b z h w c -> b (z h w) c")
        x = self.linear2(self.norm(x))
        return x
```

## File: src/dlamp/models/architectures/smoothing.py
```python
import torch
from torch import nn


class SegmentedSmoothing(nn.Module):
    def __init__(self, kernel_size: int, boundary_width: int):
        """
        Smooths last 2 dimensions of the input tensor with average
        pooling, but the boundary and interior regions are smoothed
        separately.
        """
        super().__init__()
        assert kernel_size % 2 == 1, "Kernel size must be odd"
        self.kernel_size = kernel_size
        self.half_kernel = kernel_size // 2
        self.boundary_width = boundary_width

    def _in_boundary(self, i: int, j: int, x_w: int, x_h: int) -> bool:
        return (
            i < self.boundary_width
            or i >= x_w - self.boundary_width
            or j < self.boundary_width
            or j >= x_h - self.boundary_width
        )

    def _smooth(self, x: torch.Tensor, w_idx: int, h_idx: int) -> torch.Tensor:
        x_w = x.shape[-2]
        x_h = x.shape[-1]
        x_elem_out = torch.zeros(x.shape[:-2], device=x.device, dtype=x.dtype)

        in_h_0, in_h_1 = max(0, w_idx - self.half_kernel), min(x_w, w_idx + self.half_kernel + 1)
        in_w_0, in_w_1 = max(0, h_idx - self.half_kernel), min(x_h, h_idx + self.half_kernel + 1)
        divide_factor = 0
        for i in range(in_h_0, in_h_1):
            for j in range(in_w_0, in_w_1):
                if self._in_boundary(i, j, x_w, x_h) == self._in_boundary(w_idx, h_idx, x_w, x_h):
                    x_elem_out += x[..., i, j]
                    divide_factor += 1
        x_elem_out /= divide_factor
        return x_elem_out

    def forward(self, x_in: torch.Tensor) -> torch.Tensor:
        x_w, x_h = x_in.shape[-2:]
        x_out = torch.zeros_like(x_in)
        for i in range(x_w):
            for j in range(x_h):
                x_out[..., i, j] = self._smooth(x_in, i, j)
        return x_out


class SegmentedSmoothingV2(nn.Module):
    def __init__(self, kernel_size: int, boundary_width: int):
        """
        Smooths last 2 dimensions of the input tensor with average
        pooling, but the boundary and interior regions are smoothed
        separately.
        """
        super().__init__()
        assert kernel_size % 2 == 1, "Kernel size must be odd"
        self.kernel_size = kernel_size
        self.boundary_width = boundary_width

        self.avg_pool = nn.AvgPool3d(
            kernel_size=(1, kernel_size, kernel_size),
            stride=(1, 1, 1),
            padding=(0, kernel_size // 2, kernel_size // 2),
            count_include_pad=False,
        )
        self.sum_pool = nn.AvgPool3d(
            kernel_size=(1, kernel_size, kernel_size),
            stride=(1, 1, 1),
            padding=(0, kernel_size // 2, kernel_size // 2),
            divisor_override=1,
        )

        interior_slice = slice(boundary_width, -boundary_width)
        self.interior_idx = (..., interior_slice, interior_slice)

    def forward(self, x_in: torch.Tensor) -> torch.Tensor:
        interior_mask = torch.zeros_like(x_in, device=x_in.device, dtype=torch.bool)
        interior_mask[self.interior_idx] = True

        x_out = torch.zeros_like(x_in, device=x_in.device, dtype=x_in.dtype)
        # Smooth interior
        x_out[self.interior_idx] = self.avg_pool(x_in[self.interior_idx])
        # Smooth boundary
        x_boundary_sum = self.sum_pool(x_in * (~interior_mask).float())
        x_boundary_count = self.sum_pool((~interior_mask).float())
        x_out = torch.where(~interior_mask, x_boundary_sum / x_boundary_count, x_out)

        return x_out
```

## File: src/dlamp/models/architectures/unet_test.py
```python
import unittest
from typing import ClassVar

import torch

from .unet import AttentionBlock, Downsample, ResidualBlock, UNet, Upsample


class UnetTest(unittest.TestCase):
    def test_unet(self):
        batch_size = 16
        channels = 3
        hidden_dim = 128
        ch_mults = (1, 2, 2, 1)
        is_attn = (False, False, False, True)
        n_blocks = 8
        steps = 300

        # input
        input_shape = (batch_size, channels, 224, 224)
        x = torch.randn(input_shape).cuda()
        t = torch.randint(0, steps, (batch_size,), dtype=torch.long).cuda()

        # model
        model = UNet(
            image_channels=channels,
            n_channels=hidden_dim,
            ch_mults=ch_mults,
            is_attn=is_attn,
            n_blocks=n_blocks,
        )
        model = model.cuda()

        with torch.no_grad():
            y = model(x, t)

        self.assertEqual(x.shape, y.shape)


class DownsampleTest(unittest.TestCase):
    def test_downsample(self):
        channels = 3

        # input
        x = torch.randn((16, channels, 128, 128)).cuda()
        t = torch.randn((16, channels)).cuda()

        # model
        downsample = Downsample(channels)
        downsample = downsample.cuda()

        with torch.no_grad():
            y = downsample(x, t)

        self.assertEqual(x.size(-2) / 2, y.size(-2))
        self.assertEqual(x.size(-1) / 2, y.size(-1))


class UpsampleTest(unittest.TestCase):
    def test_upsample(self):
        channels = 3

        # input
        x = torch.randn((16, channels, 128, 128)).cuda()
        t = torch.randn((16, channels)).cuda()

        # model
        upsample = Upsample(channels)
        upsample = upsample.cuda()

        with torch.no_grad():
            y = upsample(x, t)

        self.assertEqual(x.size(-2) * 2, y.size(-2))
        self.assertEqual(x.size(-1) * 2, y.size(-1))


class ResidualBlockTest(unittest.TestCase):
    batch_size = 16
    H = 224
    W = 480
    test_case_0: ClassVar[dict] = {
        "in_channels": 128,
        "out_channels": 256,
        "time_channels": 64,
    }
    test_case_1: ClassVar[dict] = {
        "in_channels": 128,
        "out_channels": 64,
        "time_channels": 32,
    }

    def test_residual_block(self):
        for i in range(2):
            test_case = self.test_case_0 if i == 0 else self.test_case_1
            in_channels = test_case["in_channels"]
            out_channels = test_case["out_channels"]
            time_channels = test_case["time_channels"]

            # input
            x = torch.randn((self.batch_size, in_channels, self.H, self.W))
            x = x.cuda()
            t = torch.randn((16, time_channels)).cuda()

            # model
            residual_block = ResidualBlock(in_channels, out_channels, time_channels)
            residual_block = residual_block.cuda()

            with torch.no_grad():
                y = residual_block(x, t)

            self.assertEqual(y.shape, torch.Size([self.batch_size, out_channels, self.H, self.W]))


class AttentionBlockTest(unittest.TestCase):
    def test_attention_block(self):
        in_channels = 128
        attn_num_heads = 8
        time_channels = 32

        # input
        x = torch.randn((16, in_channels, 32, 32))
        x = x.cuda()
        t = torch.randn((16, time_channels)).cuda()

        # model
        attention_block = AttentionBlock(in_channels, attn_num_heads)
        attention_block = attention_block.cuda()

        with torch.no_grad():
            y = attention_block(x, t)

        self.assertEqual(x.shape, y.shape)


if __name__ == "__main__":
    # CLI: python -m src.models.architectures.unet_test
    unittest.main(verbosity=2)
```

## File: src/dlamp/models/architectures/unet.py
```python
import math

import torch
from torch import nn

__all__ = ["UNet"]

"""
copy from https://colab.research.google.com/drive/1NFxjNI-UIR7Ku0KERmv7Yb_586vHQW43?usp=sharing#scrollTo=aHwkcmvkRLH0
"""


# A fancy activation function
class Swish(nn.Module):
    r"""
    ### Swish actiavation function
    $$x \cdot \sigma(x)$$
    """

    def forward(self, x):
        return x * torch.sigmoid(x)


# The time embedding
class TimeEmbedding(nn.Module):
    """
    ### Embeddings for $t$
    """

    def __init__(self, n_channels: int):
        """
        * `n_channels` is the number of dimensions in the embedding
        """
        super().__init__()
        self.n_channels = n_channels
        # First linear layer
        self.lin1 = nn.Linear(self.n_channels // 4, self.n_channels)
        # Activation
        self.act = Swish()
        # Second linear layer
        self.lin2 = nn.Linear(self.n_channels, self.n_channels)

    def forward(self, t: torch.Tensor):
        # Create sinusoidal position embeddings
        # [same as those from the transformer](../../transformers/positional_encoding.html)
        #
        # \begin{align}
        # PE^{(1)}_{t,i} &= sin\Bigg(\frac{t}{10000^{\frac{i}{d - 1}}}\Bigg) \\
        # PE^{(2)}_{t,i} &= cos\Bigg(\frac{t}{10000^{\frac{i}{d - 1}}}\Bigg)
        # \end{align}
        #
        # where $d$ is `half_dim`
        half_dim = self.n_channels // 8
        emb = math.log(10_000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=t.device) * -emb)
        emb = t[:, None] * emb[None, :]
        emb = torch.cat((emb.sin(), emb.cos()), dim=1)

        # Transform with the MLP
        emb = self.act(self.lin1(emb))
        emb = self.lin2(emb)

        return emb


# Residual blocks include 'skip' connections
class ResidualBlock(nn.Module):
    """
    ### Residual block
    A residual block has two convolution layers with group normalization.
    Each resolution is processed with two residual blocks.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        time_channels: int,
        n_groups: int = 32,
    ):
        """
        * `in_channels` is the number of input channels
        * `out_channels` is the number of input channels
        * `time_channels` is the number channels in the time step ($t$) embeddings
        * `n_groups` is the number of groups for [group normalization](../../normalization/group_norm/index.html)
        """
        super().__init__()
        # Group normalization and the first convolution layer
        self.norm1 = nn.GroupNorm(n_groups, in_channels)
        self.act1 = Swish()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=(3, 3), padding=(1, 1))

        # Group normalization and the second convolution layer
        self.norm2 = nn.GroupNorm(n_groups, out_channels)
        self.act2 = Swish()
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=(3, 3), padding=(1, 1))

        # If the number of input channels is not equal to the number of output channels we have to
        # project the shortcut connection
        if in_channels != out_channels:
            self.shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=(1, 1))
        else:
            self.shortcut = nn.Identity()

        # Linear layer for time embeddings
        self.time_emb = nn.Linear(time_channels, out_channels)

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        """
        * `x` has shape `[batch_size, in_channels, height, width]`
        * `t` has shape `[batch_size, time_channels]`
        """
        # First convolution layer
        h = self.conv1(self.act1(self.norm1(x)))
        # Add time embeddings
        h += self.time_emb(t)[:, :, None, None]
        # Second convolution layer
        h = self.conv2(self.act2(self.norm2(h)))

        # Add the shortcut connection and return
        return h + self.shortcut(x)


class AttentionBlock(nn.Module):
    """
    ### Attention block
    This is similar to [transformer multi-head attention](../../transformers/mha.html).
    """

    def __init__(self, n_channels: int, n_heads: int = 1, d_k: int | None = None):
        """
        * `n_channels` is the number of channels in the input
        * `n_heads` is the number of heads in multi-head attention
        * `d_k` is the number of dimensions in each head
        * `n_groups` is the number of groups for [group normalization](../../normalization/group_norm/index.html)
        """
        super().__init__()

        # Default `d_k`
        if d_k is None:
            d_k = n_channels // n_heads
        # Projections for query, key and values
        self.projection = nn.Linear(n_channels, n_heads * d_k * 3)
        # Linear layer for final transformation
        self.output = nn.Linear(n_heads * d_k, n_channels)
        # Scale for dot-product attention
        self.scale = d_k**-0.5
        self.n_heads = n_heads
        self.d_k = d_k

    def forward(self, x: torch.Tensor, t: torch.Tensor | None = None):
        """
        * `x` has shape `[batch_size, in_channels, height, width]`
        * `t` has shape `[batch_size, time_channels]`
        """
        # `t` is not used, but it's kept in the arguments because for the attention layer function signature
        # to match with `ResidualBlock`.
        _ = t
        # Get shape
        batch_size, n_channels, height, width = x.shape
        # Change `x` to shape `[batch_size, seq, n_channels]`
        x = x.reshape(batch_size, n_channels, -1).permute(0, 2, 1).contiguous()
        # Get query, key, and values (concatenated) and shape it to `[batch_size, seq, n_heads, 3 * d_k]`
        qkv = self.projection(x).reshape(batch_size, -1, self.n_heads, 3 * self.d_k)
        # Split query, key, and values. Each of them will have shape `[batch_size, seq, n_heads, d_k]`
        q, k, v = torch.chunk(qkv, 3, dim=-1)
        # Calculate scaled dot-product $\frac{Q K^\top}{\sqrt{d_k}}$
        attn = torch.einsum("bihd,bjhd->bijh", q, k) * self.scale
        # Softmax along the sequence dimension $\underset{seq}{softmax}\Bigg(\frac{Q K^\top}{\sqrt{d_k}}\Bigg)$
        attn = attn.softmax(dim=1)
        # Multiply by values
        res = torch.einsum("bijh,bjhd->bihd", attn, v)
        # Reshape to `[batch_size, seq, n_heads * d_k]`
        res = res.reshape(batch_size, -1, self.n_heads * self.d_k)
        # Transform to `[batch_size, seq, n_channels]`
        res = self.output(res)

        # Add skip connection
        res += x

        # Change to shape `[batch_size, in_channels, height, width]`
        res = res.permute(0, 2, 1).contiguous().reshape(batch_size, n_channels, height, width)

        return res


class DownBlock(nn.Module):
    """
    ### Down block
    This combines `ResidualBlock` and `AttentionBlock`. These are used in the first half of U-Net at each resolution.
    """

    def __init__(self, in_channels: int, out_channels: int, time_channels: int, has_attn: bool):
        super().__init__()
        self.res = ResidualBlock(in_channels, out_channels, time_channels)
        if has_attn:
            self.attn = AttentionBlock(out_channels)
        else:
            self.attn = nn.Identity()

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        x = self.res(x, t)
        x = self.attn(x)
        return x


class UpBlock(nn.Module):
    """
    ### Up block
    This combines `ResidualBlock` and `AttentionBlock`. These are used in the second half of U-Net at each resolution.
    """

    def __init__(self, in_channels: int, out_channels: int, time_channels: int, has_attn: bool):
        super().__init__()
        # The input has `in_channels + out_channels` because we concatenate the output of the same resolution
        # from the first half of the U-Net
        self.res = ResidualBlock(in_channels + out_channels, out_channels, time_channels)
        if has_attn:
            self.attn = AttentionBlock(out_channels)
        else:
            self.attn = nn.Identity()

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        x = self.res(x, t)
        x = self.attn(x)
        return x


class MiddleBlock(nn.Module):
    """
    ### Middle block
    It combines a `ResidualBlock`, `AttentionBlock`, followed by another `ResidualBlock`.
    This block is applied at the lowest resolution of the U-Net.
    """

    def __init__(self, n_channels: int, time_channels: int):
        super().__init__()
        self.res1 = ResidualBlock(n_channels, n_channels, time_channels)
        self.attn = AttentionBlock(n_channels)
        self.res2 = ResidualBlock(n_channels, n_channels, time_channels)

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        x = self.res1(x, t)
        x = self.attn(x)
        x = self.res2(x, t)
        return x


class Upsample(nn.Module):
    """
    ### Scale up the feature map by $2 \times$
    """

    def __init__(self, n_channels):
        super().__init__()
        self.conv = nn.ConvTranspose2d(n_channels, n_channels, (4, 4), (2, 2), (1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        # `t` is not used, but it's kept in the arguments because for the attention layer function signature
        # to match with `ResidualBlock`.
        _ = t
        return self.conv(x)


class Downsample(nn.Module):
    """
    ### Scale down the feature map by $\frac{1}{2} \times$
    """

    def __init__(self, n_channels):
        super().__init__()
        self.conv = nn.Conv2d(n_channels, n_channels, (3, 3), (2, 2), (1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor):
        # `t` is not used, but it's kept in the arguments because for the attention layer function signature
        # to match with `ResidualBlock`.
        _ = t
        return self.conv(x)


# The core class definition (aka the important bit)
class UNet(nn.Module):
    """
    ## U-Net
    """

    def __init__(
        self,
        image_channels: int = 3,
        n_channels: int = 64,
        ch_mults: tuple[int, ...] | list[int] = (1, 2, 2, 4),
        is_attn: tuple[bool, ...] | list[int] = (False, False, True, True),
        n_blocks: int = 2,
    ):
        """
        * `image_channels` is the number of channels in the image. $3$ for RGB.
        * `n_channels` is number of channels in the initial feature map that we transform the image into
        * `ch_mults` is the list of channel numbers at each resolution. The number of channels is `ch_mults[i] * n_channels`
        * `is_attn` is a list of booleans that indicate whether to use attention at each resolution
        * `n_blocks` is the number of `UpDownBlocks` at each resolution
        """
        super().__init__()

        # Number of resolutions
        n_resolutions = len(ch_mults)

        # Project image into feature map
        self.image_proj = nn.Conv2d(image_channels, n_channels, kernel_size=(3, 3), padding=(1, 1))

        # Time embedding layer. Time embedding has `n_channels * 4` channels
        self.time_emb = TimeEmbedding(n_channels * 4)

        # #### First half of U-Net - decreasing resolution
        down = []
        # Number of channels
        out_channels = in_channels = n_channels
        # For each resolution
        for i in range(n_resolutions):
            # Number of output channels at this resolution
            out_channels = in_channels * ch_mults[i]
            # Add `n_blocks`
            for _ in range(n_blocks):
                down.append(DownBlock(in_channels, out_channels, n_channels * 4, is_attn[i]))
                in_channels = out_channels
            # Down sample at all resolutions except the last
            if i < n_resolutions - 1:
                down.append(Downsample(in_channels))

        # Combine the set of modules
        self.down = nn.ModuleList(down)

        # Middle block
        self.middle = MiddleBlock(
            out_channels,
            n_channels * 4,
        )

        # #### Second half of U-Net - increasing resolution
        up = []
        # Number of channels
        in_channels = out_channels
        # For each resolution
        for i in reversed(range(n_resolutions)):
            # `n_blocks` at the same resolution
            for _ in range(n_blocks):
                up.append(UpBlock(in_channels, out_channels, n_channels * 4, is_attn[i]))
            # Final block to reduce the number of channels
            out_channels = in_channels // ch_mults[i]
            up.append(UpBlock(in_channels, out_channels, n_channels * 4, is_attn[i]))
            in_channels = out_channels
            # Up sample at all resolutions except last
            if i > 0:
                up.append(Upsample(in_channels))

        # Combine the set of modules
        self.up = nn.ModuleList(up)

        # Final normalization and convolution layer
        self.norm = nn.GroupNorm(8, n_channels)
        self.act = Swish()
        self.final = nn.Conv2d(in_channels, image_channels, kernel_size=(3, 3), padding=(1, 1))

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """
        * `x` has shape `[batch_size, in_channels, height, width]`
        * `t` has shape `[batch_size]`
        """

        # Get time-step embeddings
        t = self.time_emb(t)

        # Get image projection
        x = self.image_proj(x)

        # `h` will store outputs at each resolution for skip connection
        h = [x]
        # First half of U-Net
        for m in self.down:
            x = m(x, t)
            h.append(x)

        # Middle (bottom)
        x = self.middle(x, t)

        # Second half of U-Net
        for m in self.up:
            if isinstance(m, Upsample):
                x = m(x, t)
            else:
                # Get the skip connection from first half of U-Net and concatenate
                s = h.pop()
                x = torch.cat((x, s), dim=1)
                x = m(x, t)

        # Final normalization and convolution
        return self.final(self.act(self.norm(x)))
```

## File: src/dlamp/models/builders/base_builder.py
```python
import abc
import logging

from lightning import LightningModule, Trainer
from omegaconf import OmegaConf


class BaseBuilder(metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        self.kwargs = OmegaConf.create(kwargs)
        self.log = logging.getLogger(__name__)
        self.log.info(f"Use Builder: {self.__class__.__name__}")

    def info_log(self, content: str):
        self.log.info(f"[{self.__class__.__name__}] {content}")

    @abc.abstractmethod
    def build_model(self) -> LightningModule:
        return NotImplemented

    @abc.abstractmethod
    def build_trainer(self) -> Trainer:
        return NotImplemented
```

## File: src/dlamp/models/builders/glide_builder.py
```python
from collections.abc import Callable
from pathlib import Path

import torch
from lightning import LightningModule, Trainer
from lightning.pytorch.callbacks import (
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
)
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch.strategies import FSDPStrategy
from torch import nn
from torch.utils.data import DataLoader

from dlamp.inference.infer_utils import init_ort_instance, load_pangu_model

from ...const import CHECKPOINT_DIR
from ...utils import DataCompose, convert_hydra_dir_to_timestamp
from ..architectures import GlideUNet
from ..callbacks import LogDiffusionPredSamplesCallback
from ..diffusion_process import DDIMProcess, DDPMProcess
from ..lightning_modules import create_diffusion_module
from .base_builder import BaseBuilder

__all__ = ["GlideBuilder"]


class GlideBuilder(BaseBuilder):
    def __init__(self, hydra_dir: Path, data_list: list[DataCompose], **kwargs):
        super().__init__(**kwargs)

        self.time_stamp = convert_hydra_dir_to_timestamp(hydra_dir)
        self.data_list = data_list
        self.input_channels = len(data_list)
        self.only_radar = getattr(self.kwargs, "only_radar", False)

        self.info_log(f"Input Image Shape: {self.kwargs.image_shape}")
        self.info_log(f"Glide Unet Layers: {len(self.kwargs.ch_mults)}")

    def _backbone_model(self) -> nn.Module:
        return GlideUNet(
            image_channels=1 if self.only_radar else self.input_channels,
            hidden_dim=self.kwargs.hidden_dim,
            ch_mults=self.kwargs.ch_mults,
            is_attn=self.kwargs.is_attn,
            n_blocks=self.kwargs.n_blocks,
        )

    def _regression_model(self) -> Callable[[torch.device], nn.Module]:
        if self.kwargs.regression_onnx_path:
            return init_ort_instance(onnx_path=self.kwargs.regression_onnx_path)
        elif self.kwargs.regressoin_ckpt_path:
            return load_pangu_model(
                ckpt_path=self.kwargs.regressoin_ckpt_path,
                data_list=self.data_list,
                image_shape=self.kwargs.image_shape,
            )
        else:
            raise ValueError("Either regression_onnx_path or regressoin_ckpt_path must be provided.")

    def build_model(self, test_dataloader: DataLoader | None = None) -> LightningModule:
        if self.kwargs.diffusion_type == "DDPM":
            parent_class = DDPMProcess
        elif self.kwargs.diffusion_type == "DDIM":
            parent_class = DDIMProcess
        else:
            raise ValueError("Invalid base class name.")

        return create_diffusion_module(parent_class)(
            test_dataloader=test_dataloader,
            backbone_model_fn=self._backbone_model,
            regression_model_fn=self._regression_model(),
            timesteps=self.kwargs.timesteps,
            beta_start=self.kwargs.beta_start,
            beta_end=self.kwargs.beta_end,
            optim_config=self.kwargs.optim_config,
            warmup_epochs=self.kwargs.warmup_epochs,
            loss_factor=self.kwargs.loss_factor,
            only_radar=self.only_radar,
        )

    def build_trainer(self, logger) -> Trainer:
        # set number of GPUs
        num_gpus = torch.cuda.device_count() if self.kwargs.num_gpus is None else self.kwargs.num_gpus

        # distributed training strategy
        strategy = getattr(self.kwargs, "strategy", "auto")
        match strategy:
            case "FULL_SHARD":
                strategy = FSDPStrategy(sharding_strategy="FULL_SHARD", state_dict_type="sharded")
            case "SHARD_GRAD_OP":
                strategy = FSDPStrategy(sharding_strategy="SHARD_GRAD_OP", state_dict_type="sharded")
            case _:
                pass

        # set callbacks
        callbacks = []
        callbacks.append(LearningRateMonitor())
        callbacks.append(self.checkpoint_callback())
        if self.kwargs.log_image_every_n_steps is not None:
            callbacks.append(LogDiffusionPredSamplesCallback(self.kwargs.log_image_every_n_steps))
        if self.kwargs.early_stop_patience is not None:
            callbacks.append(EarlyStopping(monitor="val_loss_epoch", patience=self.kwargs.early_stop_patience))

        return Trainer(
            num_sanity_val_steps=2,
            benchmark=True,
            fast_dev_run=self.kwargs.fast_dev_run,  # use n batch(es) to fast run through train/valid, no checkpoint, no max_epoch
            logger=logger,
            check_val_every_n_epoch=1,
            log_every_n_steps=self.kwargs.log_every_n_steps,  # only affect train_loss
            # -1: infinite epochs, None: default 1000 epochs
            max_epochs=getattr(self.kwargs, "max_epochs", None),
            # If min_steps > 0, max_epoch must be valid. And min_steps is prior to early stopping
            min_steps=getattr(self.kwargs, "min_steps", -1),
            limit_train_batches=getattr(self.kwargs, "limit_train_batches", None),
            limit_val_batches=getattr(self.kwargs, "limit_val_batches", None),
            devices=[i for i in range(num_gpus)],
            strategy=strategy,
            callbacks=callbacks,
            # profiler=AdvancedProfiler(
            #     dirpath="./profiler", filename=f"{self.__class__.__name__}"
            # ),
            precision=self.kwargs.precision,
        )

    def checkpoint_callback(self) -> ModelCheckpoint:
        return ModelCheckpoint(
            dirpath=CHECKPOINT_DIR,
            filename=self.kwargs.model_name
            + f"_{self.kwargs.diffusion_type}"
            + f"_{self.time_stamp}"
            + "-{epoch:03d}-{val_loss_epoch:.6f}",
            save_top_k=1,
            verbose=True,
            monitor="val_loss_epoch",
            mode="min",
        )

    def wandb_logger(self, save_dir: str = "./logs") -> WandbLogger:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        return WandbLogger(
            save_dir=save_dir,
            log_model=False,  # log W&B artifacts
            project="my-burdensome-project",
            name=self.kwargs.model_name + f"_{self.kwargs.diffusion_type}" + f"_{self.time_stamp}",
            offline=True,
        )
```

## File: src/dlamp/models/builders/pangu_builder.py
```python
from pathlib import Path

import torch
from lightning import LightningModule, Trainer
from lightning.pytorch.callbacks import (
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
)
from lightning.pytorch.loggers import WandbLogger
from torch import nn
from torch.utils.data import DataLoader

from ...const import CHECKPOINT_DIR
from ...utils import DataCompose, convert_hydra_dir_to_timestamp
from .. import PanguModel
from ..callbacks import LogPredictionSamplesCallback
from ..lightning_modules import PanguLightningModule
from .base_builder import BaseBuilder

__all__ = ["PanguBuilder"]


class PanguBuilder(BaseBuilder):
    def __init__(self, hydra_dir: Path, data_list: list[DataCompose], **kwargs):
        super().__init__(**kwargs)

        self.pressure_levels: list[str] = DataCompose.get_all_levels(data_list, only_upper=True, to_str=True)
        self.upper_vars: list[str] = DataCompose.get_all_vars(data_list, only_upper=True, to_str=True)
        self.surface_vars: list[str] = DataCompose.get_all_vars(data_list, only_surface=True, to_str=True)

        self.time_stamp = convert_hydra_dir_to_timestamp(hydra_dir)

        self.info_log(f"Input Image Shape: {self.kwargs.image_shape}")
        self.info_log(f"Patch Size: {self.kwargs.patch_size}")
        self.info_log(f"Window Size: {self.kwargs.window_size}")

    def _backbone_model(self) -> nn.Module:
        sfc_input_ch = len(self.surface_vars) + 4 if self.kwargs.add_time_features else len(self.surface_vars)
        return PanguModel(
            image_shape=self.kwargs.image_shape,
            patch_size=self.kwargs.patch_size,
            window_size=self.kwargs.window_size,
            upper_levels=len(self.pressure_levels),
            upper_channels=len(self.upper_vars),
            surface_input_channels=sfc_input_ch,
            surface_output_channels=len(self.surface_vars),
            embed_dim=self.kwargs.embed_dim,
            heads=self.kwargs.heads,
            depths=self.kwargs.depths,
            max_drop_path_ratio=self.kwargs.max_drop_path_ratio,
            dropout_rate=self.kwargs.dropout_rate,
            smoothing_kernel_size=self.kwargs.smoothing_kernel_size,
            segmented_smooth_boundary_width=self.kwargs.segmented_smooth_boundary_width,
        )

    def build_model(
        self,
        test_dataloader: DataLoader | None = None,
        predict_iters: int | None = None,
    ) -> LightningModule:
        return PanguLightningModule(
            test_dataloader=test_dataloader,
            backbone_model=self._backbone_model(),
            upper_var_weights=None,
            surface_var_weights=None,
            surface_alpha=self.kwargs.surface_alpha,
            pressure_levels=self.pressure_levels,
            upper_vars=self.upper_vars,
            surface_vars=self.surface_vars,
            optim_config=self.kwargs.optim_config,
            lr_schedule=self.kwargs.lr_schedule,
            predict_iters=predict_iters,
        )

    def build_trainer(self, logger) -> Trainer:
        num_gpus = torch.cuda.device_count() if self.kwargs.num_gpus is None else self.kwargs.num_gpus
        strategy = getattr(self.kwargs, "strategy", "auto")

        callbacks = []
        callbacks.append(LearningRateMonitor())
        callbacks.append(self.checkpoint_callback())
        if self.kwargs.log_image_every_n_steps is not None:
            callbacks.append(LogPredictionSamplesCallback(self.kwargs.log_image_every_n_steps))
        if self.kwargs.early_stop_patience is not None:
            callbacks.append(EarlyStopping(monitor="val_loss_epoch", patience=self.kwargs.early_stop_patience))

        return Trainer(
            num_sanity_val_steps=2,
            benchmark=True,
            fast_dev_run=self.kwargs.fast_dev_run,  # use n batch(es) to fast run through train/valid, no checkpoint, no max_epoch
            logger=logger,
            check_val_every_n_epoch=1,
            log_every_n_steps=self.kwargs.log_every_n_steps,  # only affect train_loss
            # -1: infinite epochs, None: default 1000 epochs
            max_epochs=getattr(self.kwargs, "max_epochs", None),
            # If min_steps > 0, max_epoch must be valid. And min_steps is prior to early stopping
            min_steps=getattr(self.kwargs, "min_steps", -1),
            limit_train_batches=getattr(self.kwargs, "limit_train_batches", None),
            limit_val_batches=getattr(self.kwargs, "limit_val_batches", None),
            accelerator="gpu",
            devices=[i for i in range(num_gpus)],
            strategy=strategy,
            callbacks=callbacks,
            # profiler=AdvancedProfiler(
            #     dirpath="./profiler", filename=f"{self.__class__.__name__}"
            # ),
            precision=self.kwargs.precision,
        )

    def checkpoint_callback(self) -> ModelCheckpoint:
        return ModelCheckpoint(
            dirpath=CHECKPOINT_DIR,
            filename=self.kwargs.model_name + f"_{self.time_stamp}" + "-{epoch:03d}-{val_loss_epoch:.4f}",
            save_top_k=1,
            verbose=True,
            monitor="val_loss_epoch",
            mode="min",
            save_last=self.kwargs.save_last,
        )

    def wandb_logger(self, save_dir: str = "./logs") -> WandbLogger:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        return WandbLogger(
            save_dir=save_dir,
            log_model=False,  # log W&B artifacts
            project="my-awesome-project",
            name=self.kwargs.model_name + f"_{self.time_stamp}",
            offline=True,
        )
```

## File: src/dlamp/models/callbacks/log_diffusion_pred_samples_callback.py
```python
import lightning as L
import numpy as np
import wandb
from lightning.pytorch.loggers import WandbLogger

from ...standardizer import get_standardizer
from .log_prediction_samples_callback import LogPredictionSamplesCallback


class LogDiffusionPredSamplesCallback(LogPredictionSamplesCallback):
    def __init__(self, log_image_every_n_steps: int):
        super().__init__(log_image_every_n_steps)
        self.first_guess = []
        self.first_guess_surface = []
        self.log_first_guess_imgs = []
        self.log_final_imgs = []

    def on_validation_epoch_end(self, trainer: L.Trainer, pl_module: L.LightningModule):
        global_step = trainer.global_step
        if pl_module.global_rank != 0 or (global_step != 0 and global_step - self.global_step_record < self.log_freq):
            return

        wandb_logger: WandbLogger = trainer.logger.experiment
        standardizer = get_standardizer()
        for idx, input in enumerate(self.log_input_tensors):
            sfc_ch = input["surface"].shape[-1]

            # one-time logging for first guess
            if len(self.log_first_guess_imgs) < len(self.log_input_tensors):
                regress = pl_module.inference_regression(
                    input["upper_air"], input["surface"], input["upper_air"].device
                )  # (B, Lv*C1+C2, H, W)
                regress_sfc = regress[:, -sfc_ch:].permute(0, 2, 3, 1)  # (B, H, W, C2)
                regress_sfc = regress_sfc.unsqueeze(1).cpu().numpy()  # (B, 1, H, W, C2)
                regress_sfc = np.squeeze(standardizer.destandardize(regress_sfc))  # (H, W)
                fig_fg, _ = self.painter.plot_1x1(self.data_lon, self.data_lat, regress_sfc)
                self.first_guess.append(regress)
                self.first_guess_surface.append(regress_sfc)
                self.log_first_guess_imgs.append(wandb.Image(fig_fg))

            # denoising process
            model_output = pl_module.denoising(self.first_guess[idx], input["upper_air"].device)
            model_output_radar = {}
            for step, output in model_output.items():
                # extract radar channel (B, 1, H, W, 1)
                output_surface = output[:, -1:, :, :, None]
                output_surface = output_surface.cpu().numpy()
                output_surface = np.squeeze(standardizer.destandardize(output_surface))
                model_output_radar[f"step_{step}"] = output_surface

            # plot diffusion outputs
            fig_pd, _ = self.painter.plot_1xn(
                self.data_lon,
                self.data_lat,
                list(model_output_radar.values()),
                titles=list(model_output_radar.keys()),
            )
            fig_final, _ = self.painter.plot_1x1(
                self.data_lon,
                self.data_lat,
                self.first_guess_surface[idx] + model_output_radar["step_0"],
            )
            self.log_pred_imgs.append(wandb.Image(fig_pd))
            self.log_final_imgs.append(wandb.Image(fig_final))

        wandb_logger.log(
            {
                "ground truth": self.log_target_imgs,
                "first guess": self.log_first_guess_imgs,
                "diffusion": self.log_pred_imgs,
                "final output": self.log_final_imgs,
            }
        )
        self.global_step_record = global_step
        self.log_pred_imgs.clear()
        self.log_final_imgs.clear()
```

## File: src/dlamp/models/callbacks/log_prediction_samples_callback.py
```python
from datetime import UTC, datetime

import lightning as L
import torch
import wandb
import yaml
from lightning.pytorch.callbacks import Callback

from dlamp.visual import VizPressure

from ...datasets import CustomDataset
from ...runtime_config import get_runtime_config
from ...standardizer import get_standardizer
from ...utils import DataCompose, DataGenerator


class LogPredictionSamplesCallback(Callback):
    def __init__(self, log_image_every_n_steps: int):
        super().__init__()
        self.log_freq = log_image_every_n_steps
        self.painter = VizPressure()
        self.global_step_record = 0
        self.already_load_data_for_plot = False

        # load config from runtime config
        runtime_config = get_runtime_config()
        with open(runtime_config.data_config_path, "r") as stream:
            data_config = yaml.safe_load(stream)
        data_list = DataCompose.from_config(data_config["train_data"])
        self.sfc_vars = DataCompose.get_all_vars(data_list, only_surface=True)

        self.log_input_tensors = []
        self.log_target_imgs = []
        self.log_pred_imgs = []

    def on_validation_start(self, trainer: L.Trainer, pl_module: L.LightningModule) -> None:
        if self.already_load_data_for_plot == True:
            return

        # load axis
        custom_dataset: CustomDataset = pl_module.test_dataloader().dataset
        data_gnrt: DataGenerator = custom_dataset._data_gnrt
        dc_lat, dc_lon = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})
        self.data_lat = data_gnrt.yield_data(custom_dataset._init_time_list[0], dc_lat)
        self.data_lon = data_gnrt.yield_data(custom_dataset._init_time_list[0], dc_lon)

        # choose cases from `src.const.EVAL_CASES`
        cases = [datetime(2022, 9, 12, tzinfo=UTC)]  # datetime(2022, 10, 16)
        standardizer = get_standardizer()
        for case in cases:
            internal_idx = custom_dataset.get_internal_index_from_dt(case)
            input, target = custom_dataset[internal_idx]

            # Input Data: (lv, H, W, C) -> (1, lv, H, W, C)
            for k in input:
                input[k] = torch.from_numpy(input[k][None]).cuda()
            self.log_input_tensors.append(input)  # torch.Tensor

            # Target Data
            target_data = standardizer.destandardize(target["surface"])  # (lv, H, W, C)
            (slp,) = DataCompose.from_config({"PSFC": ["Surface"]})
            var_idx = self.sfc_vars.index(slp.var_name)
            target_slp = target_data[0, :, :, var_idx]
            fig_gt = self.painter.plot_1x1(self.data_lon, self.data_lat, target_slp)
            self.log_target_imgs.append(wandb.Image(fig_gt[0]))

        self.already_load_data_for_plot = True

    def on_validation_epoch_end(self, trainer: L.Trainer, pl_module: L.LightningModule):
        global_step = trainer.global_step
        if global_step != 0 and global_step - self.global_step_record < self.log_freq:
            return

        wandb_logger = trainer.logger.experiment

        # no step slider for Table: https://github.com/wandb/wandb/issues/1826
        # table = wandb.Table(columns=["case ID", "pred", "target"])
        standardizer = get_standardizer()
        for idx, input in enumerate(self.log_input_tensors):
            _, oup_sfc = pl_module(input["upper_air"], input["surface"])
            oup_sfc = standardizer.destandardize(oup_sfc.cpu().numpy())  # (B, 1, H, W, C)
            (slp,) = DataCompose.from_config({"PSFC": ["Surface"]})
            var_idx = self.sfc_vars.index(slp.var_name)
            oup_slp = oup_sfc[0, 0, :, :, var_idx]
            fig_pd, _ = self.painter.plot_1x1(self.data_lon, self.data_lat, oup_slp)
            self.log_pred_imgs.append(wandb.Image(fig_pd))

            # table.add_data(idx, wandb.Image(fig_pd), wandb.Image(fig_gt))

        wandb_logger.log({"ground truth": self.log_target_imgs, "predictions": self.log_pred_imgs})
        # wandb_logger.log({"prediction_table": table})

        self.log_pred_imgs.clear()
        self.global_step_record = global_step
```

## File: src/dlamp/models/diffusion_process/__init__.py
```python
"""Public exports for the diffusion process subpackage."""

from .ddim_process import DDIMProcess
from .ddpm_process import DDPMProcess

__all__ = ["DDIMProcess", "DDPMProcess"]
```

## File: src/dlamp/models/diffusion_process/ddim_process.py
```python
import torch
from torch import Tensor

from .ddpm_process import DDPMProcess


class DDIMProcess(DDPMProcess):
    def __init__(self, n_steps: int, min_beta: float = 0.0001, max_beta: float = 0.02):
        super().__init__(n_steps, min_beta, max_beta)

    def sampling(
        self,
        xt: Tensor,
        eps_model: Tensor,
        curr_t: Tensor,
        prev_t: Tensor,
        eta=1.0,
        simple_var=True,
    ) -> Tensor:
        """
        xₜ₋₁ = √(ᾱₜ₋₁/ᾱₜ) · xₜ +
            (√(1 - ᾱₜ₋₁ - (1 - ᾱₜ₋₁)/(1 - ᾱₜ)βₜ) - √(ᾱₜ₋₁(1 - ᾱₜ)/ᾱₜ)) · ϵ +
            √β̃ₜz
        where z ~ N(0, I)

        β̃ₜ = η · (1 - ᾱₜ₋₁) / (1 - ᾱₜ) * βₜ where βₜ = 1 - ᾱₜ / ᾱₜ₋₁
        """
        self.device_check(xt.device)

        alpha_bar_curr = self.alpha_bars[curr_t]
        alpha_bar_prev = self.alpha_bars[prev_t] if prev_t >= 0 else 1

        if simple_var:
            eta = 1
        beta_t = 1 - alpha_bar_curr / alpha_bar_prev
        var = eta * (1 - alpha_bar_prev) / (1 - alpha_bar_curr) * beta_t

        first_term = torch.sqrt(alpha_bar_prev / alpha_bar_curr) * xt
        second_term = (
            torch.sqrt(1 - alpha_bar_prev - var) - torch.sqrt(alpha_bar_prev * (1 - alpha_bar_curr) / alpha_bar_curr)
        ) * eps_model

        if simple_var:
            var = beta_t
        sigma_t = torch.sqrt(var)
        noise = torch.randn_like(xt) * sigma_t
        x_tminus1 = first_term + second_term + noise
        return x_tminus1
```

## File: src/dlamp/models/diffusion_process/ddpm_process.py
```python
import torch


class DDPMProcess:
    def __init__(
        self,
        n_steps: int,
        min_beta: float = 0.0001,
        max_beta: float = 0.02,
    ):
        betas = DDPMProcess.linear_beta_schedule(n_steps, min_beta, max_beta)
        self.betas = betas
        self.n_steps = n_steps
        self.prepare_constants()

    def q_xt_xtminus1(self, xtminus1: torch.Tensor, t: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Equation: xₜ = √1 - βₜxₜ₋₁ + √βₜε
        """
        self.device_check(xtminus1.device)
        alpha = self.alphas[t].reshape(-1, 1, 1, 1)
        beta = self.betas[t].reshape(-1, 1, 1, 1)
        eps = torch.randn_like(xtminus1)
        xt = torch.sqrt(alpha) * xtminus1 + torch.sqrt(beta) * eps
        return xt, eps

    def q_xt_x0(self, x0: torch.Tensor, t: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Equation: xₜ = √ᾱₜx₀ + √1 - ᾱₜε
        """
        self.device_check(x0.device)
        alpha_bar = self.alpha_bars[t].reshape(-1, 1, 1, 1)
        eps = torch.randn_like(x0)
        xt = torch.sqrt(alpha_bar) * x0 + torch.sqrt(1 - alpha_bar) * eps
        return xt, eps

    def sampling(
        self,
        xt: torch.Tensor,
        eps_model: torch.Tensor,
        t: torch.Tensor,
        simple_var=True,
    ) -> torch.Tensor:
        """
        Equation: xₜ₋₁ = 1/√αₜ * [xₜ - (1 - αₜ) / √(1 - ᾱₜ) * εθ(xₜ, t)] + √β̃ₜz

        if simple_var == True:
            β̃ₜ = βₜ
        else:
            β̃ₜ = (1 - ᾱₜ₋₁) / (1 - ᾱₜ) * βₜ
        """
        self.device_check(xt.device)
        if t == 0:
            beta_t_hat = 0
        else:
            if simple_var:
                beta_t_hat = self.betas[t]
            else:
                beta_t_hat = (1 - self.alpha_bars[t - 1]) / (1 - self.alpha_bars[t]) * self.betas[t]
        sigma_t = torch.sqrt(beta_t_hat) if beta_t_hat != 0 else 0
        noise = torch.randn_like(xt) * sigma_t

        mean = (xt - (1 - self.alphas[t]) / torch.sqrt(1 - self.alpha_bars[t]) * eps_model) / torch.sqrt(self.alphas[t])
        x_tminus1 = mean + noise
        return x_tminus1

    def device_check(self, device: torch.device):
        if self.betas.device != device:
            self.betas = self.betas.to(device)
            self.prepare_constants()

    def prepare_constants(self):
        self.alphas = 1 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)

    @staticmethod
    def cosine_beta_schedule(timesteps, min_beta=0.0001, max_beta=0.9999, s=0.008):
        steps = timesteps + 1
        x = torch.linspace(0, timesteps, steps)
        alphas_cumprod = torch.cos(((x / timesteps) + s) / (1 + s) * torch.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return torch.clip(betas, min_beta, max_beta)

    @staticmethod
    def linear_beta_schedule(timesteps, min_beta, max_beta):
        return torch.linspace(min_beta, max_beta, timesteps)

    @staticmethod
    def quadratic_beta_schedule(timesteps, min_beta, max_beta):
        return torch.linspace(min_beta**0.5, max_beta**0.5, timesteps) ** 2

    @staticmethod
    def sigmoid_beta_schedule(timesteps, min_beta, max_beta):
        betas = torch.linspace(-6, 6, timesteps)
        return torch.sigmoid(betas) * (max_beta - min_beta) + min_beta
```

## File: src/dlamp/models/lightning_modules/diffusion_lightning_module.py
```python
import lightning as L
import onnxruntime as ort
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader
from tqdm import trange

from ..diffusion_process import DDIMProcess, DDPMProcess
from ..model_utils import (
    RunningAverage,
    get_scheduler_with_warmup,
    restruct_dimension,
)


def create_diffusion_module(diffusion_type: DDIMProcess | DDPMProcess):
    """
    In order to dynamically create the lightning module based on different
    diffusion types (DDPM or DDIM), we define this factory function.
    """

    class DiffusionLightningModule(L.LightningModule, diffusion_type):
        def __init__(self, *, test_dataloader, backbone_model_fn, regression_model_fn, **kwargs):
            super().__init__()
            diffusion_type.__init__(
                self,
                n_steps=kwargs["timesteps"],
                min_beta=kwargs["beta_start"],
                max_beta=kwargs["beta_end"],
            )

            self.save_hyperparameters(ignore=["test_dataloader", "backbone_model_fn", "regression_model_fn"])

            self._test_dataloader: DataLoader = test_dataloader
            self.backbone_model_fn = backbone_model_fn
            self.backbone_model: nn.Module = None
            self.regression_model_fn = regression_model_fn
            self.regress_model: ort.InferenceSession | nn.Module = None
            self.loss = nn.MSELoss()
            self.loss_record = RunningAverage()

        def forward(self, noisy_img, time_step, condtion) -> torch.Tensor:
            """
            Args:
                noisy_img (torch.Tensor): (B, C, H, W)
                time_step (torch.Tensor): (B,)
                condtion (torch.Tensor): (B, C, H, W)

            Returns:
                torch.Tensor: the predict noist with shape (B, C, H, W)
            """
            return self.backbone_model(noisy_img, time_step, condtion)

        def configure_optimizers(self):
            # set optimizer
            optimizer = getattr(torch.optim, self.hparams.optim_config.name)(
                self.parameters(), **self.hparams.optim_config.args
            )

            # set learning rate schedule
            lr_schedule_name = self.hparams.lr_schedule.name
            lr_scheduler: torch.optim.lr_scheduler.LambdaLR = get_scheduler_with_warmup(
                optimizer,
                schedule_type=lr_schedule_name,
                training_steps=int(self.trainer.estimated_stepping_batches),
                **self.hparams.lr_schedule.args,
            )
            interval = "epoch" if lr_schedule_name in ["linear_decay"] else "step"
            lr_scheduler_config = {
                "scheduler": lr_scheduler,
                "interval": interval,
                "frequency": 1,
                "name": "customized_lr",
            }

            return {"optimizer": optimizer, "lr_scheduler": lr_scheduler_config}

        def configure_model(self):
            """
            Speed up model initialization. Trainer can create model directly on GPU.
            """
            if self.backbone_model is not None and self.regress_model is not None:
                return

            self.backbone_model = self.backbone_model_fn()
            self.regress_model = self.regression_model_fn(self.global_rank)

            # freeze parameters if the regression model comes from ckpt
            if isinstance(self.regress_model, torch.nn.Module):
                for param in self.regress_model.parameters():
                    param.requires_grad = False

        def common_step(self, inp_data, target):
            """
            Args:
                inp_data (dict): A dictionary containing the input data, like:
                    {
                        'upper_air': torch.Tensor (B, Lv, H, W, C),
                        'surface': torch.Tensor (B, 1, H, W, C)
                    }
                target (dict): A dictionary containing the target data, like:
                    {
                        'upper_air': torch.Tensor (B, Lv, H, W, C),
                        'surface': torch.Tensor (B, 1, H, W, C)
                    }

            Returns:
                loss: the CRPS loss
            """
            first_guess = self.inference_regression(inp_data["upper_air"], inp_data["surface"], self.device)
            target = restruct_dimension(target["upper_air"], target["surface"])
            B = target.shape[0]

            # only radar
            if self.hparams.only_radar:
                first_guess, target = first_guess[:, -1:], target[:, -1:]

            # teacher forcing
            if torch.rand(1) < 0.5:
                kernel_size = 7
                padding = (kernel_size - 1) // 2
                padded_target = F.pad(target, (padding, padding, padding, padding), mode="reflect")
                first_guess = F.avg_pool2d(padded_target, kernel_size=kernel_size, stride=1)

            # DDPM
            x_0 = target - first_guess  # (B, C, H, W)
            t = torch.randint(0, self.hparams.timesteps, (B,), dtype=torch.long)  # (B,)
            t = t.to(self.device)
            x_t, noise = self.q_xt_x0(x_0, t)
            pred_noise = self(x_t.float(), t, first_guess.float())
            loss = self.loss(pred_noise, noise)
            self.loss_record.add(loss.item() * B, B)
            return loss * self.hparams.loss_factor

        def training_step(self, batch, batch_idx):
            inp_data, target = batch
            loss = self.common_step(inp_data, target)
            self.log("train_loss", loss, on_step=True, prog_bar=True, sync_dist=True)
            self.log("orig_loss", self.loss_record.get(), on_step=True, sync_dist=True)
            return loss

        def validation_step(self, batch, batch_idx):
            inp_data, target = batch
            loss = self.common_step(inp_data, target)
            self.log(
                "val_loss",
                loss,
                on_step=True,
                on_epoch=True,
                prog_bar=True,
                sync_dist=True,
            )
            return loss

        def on_train_epoch_end(self):
            self.loss_record.reset()

        def test_dataloader(self) -> DataLoader:
            """
            Load the test dataset from external `LightningDataModule`.

            The reason doing so is that the `test_dataloader` is not accessible during
            the `trainer.fit()` loop, but we need the `test_dataloader` to record the
            images in `LogPredictionSamplesCallback`.
            """
            return self._test_dataloader

        # ============== the following functions are not coherent w/ LightningModule ==============
        # ============== however they are critical for training DDPM models          ==============

        def denoising(self, cond: torch.Tensor, device: torch.device) -> dict[int, torch.Tensor]:
            """
            Reverse process to get the image from noise. Log 6 images in a list.

            Args:
                cond (torch.Tensor): (B, C, H, W)
                device (torch.device): The device to run the model

            Returns:
                ims (dict[int, torch.Tensor]): A dictionary of images
                    {step: torch.Tensor (B, C, H, W)}
            """
            if self.hparams.only_radar and cond.shape[1] != 1:
                cond = cond[:, -1:]

            B, C, H, W = cond.shape
            x = torch.randn(B, C, H, W).to(device)  # Start with random noise
            ims = {self.hparams.timesteps: x}
            if DDPMProcess in self.__class__.__bases__:
                steps = trange(self.hparams.timesteps - 1, -1, -1, desc="DDPM Denoising")
                for step in steps:
                    t = torch.full((B,), step, dtype=torch.long).to(device)
                    with torch.no_grad():
                        pred_noise = self(x, t, cond)
                        x = self.sampling(x, pred_noise, t)
                    if step % (self.hparams.timesteps // 5) == 0:
                        ims[step] = x
            elif DDIMProcess in self.__class__.__bases__:
                ddim_steps = self.hparams.timesteps // 5
                skipped_steps = torch.linspace(self.hparams.timesteps, 0, (ddim_steps + 1), dtype=torch.long)
                steps = trange(1, ddim_steps + 1, desc="DDIM Denoising")
                for step in steps:
                    curr_t = skipped_steps[step - 1] - 1  # t large
                    prev_t = skipped_steps[step] - 1  # t small
                    t = torch.full((B,), curr_t, dtype=torch.long).to(device)
                    with torch.no_grad():
                        pred_noise = self(x, t, cond)
                        x = self.sampling(x, pred_noise, curr_t, prev_t, eta=0, simple_var=False)
                    if step % (ddim_steps // 5) == 0:
                        key = int(prev_t + 1)
                        ims[key] = x
            return ims

        def inference_regression(
            self, input_upa: torch.Tensor, input_sfc: torch.Tensor, device: torch.device
        ) -> torch.Tensor:
            """
            Inference process for the regression model. This process can be either onnxruntime-gpu
            or original pytorch.

            Args:
                input_upa (torch.Tensor): (B, Lv, H, W, C1)
                input_sfc (torch.Tensor): (B, 1, H, W, C2)
                device (torch.device): Device of the output tensor.

            Returns:
                torch.Tensor: (B, Lv*C1+C2, H, W)
            """
            if self.regress_model is None:
                self.regress_model = self.regression_model_fn(device)

            if isinstance(self.regress_model, ort.InferenceSession):
                ort_inputs = {
                    self.regress_model.get_inputs()[0].name: input_upa.cpu().numpy(),
                    self.regress_model.get_inputs()[1].name: input_sfc.cpu().numpy(),
                }
                first_guess_upper, first_guess_surface = self.regress_model.run(None, ort_inputs)
            elif isinstance(self.regress_model, torch.nn.Module):
                with torch.inference_mode():
                    first_guess_upper, first_guess_surface = self.regress_model(input_upa, input_sfc)
                first_guess_surface = torch.clone(first_guess_surface).detach_()
                first_guess_upper = torch.clone(first_guess_upper).detach_()
            else:
                raise NotImplementedError

            first_guess = restruct_dimension(
                first_guess_upper,
                first_guess_surface,
                is_numpy=isinstance(self.regress_model, ort.InferenceSession),
                device=device,
            )
            return first_guess

    return DiffusionLightningModule
```

## File: src/dlamp/models/lightning_modules/pangu_lightning_module.py
```python
import lightning as L
import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm import trange

from ..model_utils import get_scheduler_with_warmup

__all__ = ["PanguLightningModule"]


# TODO: weighted MAE loss
class PanguLightningModule(L.LightningModule):
    def __init__(self, *, test_dataloader, backbone_model, **kwargs):
        super().__init__()
        self.save_hyperparameters(ignore=["test_dataloader", "backbone_model"])
        self._test_dataloader: DataLoader = test_dataloader
        self.backbone_model: nn.Module = backbone_model

        if kwargs["upper_var_weights"] is None or kwargs["surface_var_weights"] is None:
            self.weighted_loss = False
            self.criterion = nn.L1Loss(reduction="mean")
            upper_var_weights_tensor = None
            surface_var_weights_tensor = None
        self.register_buffer("upper_var_weights", upper_var_weights_tensor)
        self.register_buffer("surface_var_weights", surface_var_weights_tensor)

    def forward(self, input_upper: torch.Tensor, input_surface: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        return self.backbone_model(input_upper, input_surface)

    def configure_optimizers(self):
        # set optimizer
        optimizer = getattr(torch.optim, self.hparams.optim_config.name)(
            self.parameters(), **self.hparams.optim_config.args
        )

        # set learning rate schedule
        lr_schedule_name = self.hparams.lr_schedule.name
        lr_scheduler: torch.optim.lr_scheduler.LambdaLR = get_scheduler_with_warmup(
            optimizer,
            schedule_type=lr_schedule_name,
            training_steps=int(self.trainer.estimated_stepping_batches),
            **self.hparams.lr_schedule.args,
        )
        interval = "epoch" if lr_schedule_name in ["linear_decay"] else "step"
        lr_scheduler_config = {
            "scheduler": lr_scheduler,
            "interval": interval,
            "frequency": 1,
            "name": "customized_lr",
        }

        return {"optimizer": optimizer, "lr_scheduler": lr_scheduler_config}

    def common_step(self, inp_data, target):
        """
        Calculates 1. model output, 2. total loss and 3. the MAE loss for each element.

        Args:
            inp_data (dict): A dictionary containing the input data with keys "upper_air" and "surface",
                whose structure like:
                    {
                        "upper_air": (B, Z, H, W, C),
                        "surface": (B, 1, H, W, C)
                    }
            target (dict): A dictionary containing the target data with keys "upper_air" and "surface",
                whose structure like:
                    {
                        "upper_air": (B, Z, H, W, C),
                        "surface": (B, 1, H, W, C)
                    }
        """
        # all data in the shape of (B, Z, H, W, C)
        oup_upper, oup_surface = self(inp_data["upper_air"], inp_data["surface"])
        if self.weighted_loss:
            raise NotImplementedError("WeightedMAE not implemented")
        else:
            loss_upper = self.criterion(oup_upper, target["upper_air"])
            loss_surface = self.criterion(oup_surface, target["surface"])
        total_loss = loss_upper + loss_surface * self.hparams.surface_alpha

        # MAE for each variable/level, shape of (Z, C)
        mae_upper = torch.abs(oup_upper - target["upper_air"]).mean(dim=(0, 2, 3))
        mae_surface = torch.abs(oup_surface - target["surface"]).mean(dim=(0, 2, 3))

        return total_loss, (oup_upper, oup_surface), (mae_upper, mae_surface)

    def training_step(self, batch, batch_idx):
        inp_data, target = batch
        loss, _, (mae_upper, mae_surface) = self.common_step(inp_data, target)
        self.log("train_loss", loss, on_step=True, prog_bar=True, sync_dist=True)
        self.log_mae_for_each_element("train", self.hparams.pressure_levels, self.hparams.upper_vars, mae_upper)
        self.log_mae_for_each_element("train", ["Surface"], self.hparams.surface_vars, mae_surface)
        return loss

    def validation_step(self, batch, batch_idx):
        inp_data, target = batch
        loss, _, (mae_upper, mae_surface) = self.common_step(inp_data, target)
        self.log("val_loss", loss, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log_mae_for_each_element("val", self.hparams.pressure_levels, self.hparams.upper_vars, mae_upper)
        self.log_mae_for_each_element("val", ["Surface"], self.hparams.surface_vars, mae_surface)
        return loss

    def predict_step(self, batch, batch_idx):
        inp_data, target = batch
        upper, surface = inp_data["upper_air"], inp_data["surface"]
        for _ in trange(self.hparams.predict_iters, desc=f"Predict batch {batch_idx}"):
            upper, surface = self(upper, surface)
        return (
            inp_data["upper_air"],
            inp_data["surface"],
            target["upper_air"],
            target["surface"],
            upper,
            surface,
        )

    @staticmethod
    def get_product_mapping():
        # check `self.predict_step()` for the order
        return {
            "input_upper": 0,
            "input_surface": 1,
            "target_upper": 2,
            "target_surface": 3,
            "output_upper": 4,
            "output_surface": 5,
        }

    # Compute the 2-norm for each layer
    # If using mixed precision, the gradients are already unscaled here
    # def on_before_optimizer_step(self, optimizer):
    #     norms = grad_norm(self.backbone_model, norm_type=2)
    #     self.log(
    #         name="gradient_2norm", value=norms["grad_2.0_norm_total"], on_step=True
    #     )
    #     norms.pop("grad_2.0_norm_total")
    #     self.log_dict(norms, on_step=True)

    def log_mae_for_each_element(self, prefix: str, lv_names: list[str], var_names: list[str], mae: torch.Tensor):
        for i, pl in enumerate(lv_names):
            for j, var in enumerate(var_names):
                self.log(
                    f"{prefix}_mae/{var}_{pl}",
                    mae[i, j],
                    on_step=False,
                    on_epoch=True,
                    sync_dist=True,
                )

    def test_dataloader(self) -> DataLoader:
        """
        Load the test dataset from external `LightningDataModule`.

        The reason doing so is that the `test_dataloader` is not accessible during
        the `trainer.fit()` loop, but we need the `test_dataloader` to record the
        images in `LogPredictionSamplesCallback`.
        """
        return self._test_dataloader
```

## File: src/dlamp/models/loss_fn/crps.py
```python
import torch
from torch import nn


class CRPS(nn.Module):
    def __init__(self, integral_number: int = 1000):
        super().__init__()
        self.number = integral_number

    def forward(self, prediction: torch.Tensor, target: torch.Tensor):
        return self._calculate_crps(prediction.flatten(), target.flatten())

    def _calculate_crps(self, prediction: torch.Tensor, target: torch.Tensor):
        min_val = torch.min(torch.min(prediction), torch.min(target))
        max_val = torch.max(torch.max(prediction), torch.max(target))

        x = torch.linspace(min_val, max_val, self.number, device=prediction.device)
        x = x.to(prediction.dtype)

        cdf_prediction = self._calculate_cdf(x, prediction)
        cdf_target = self._calculate_cdf(x, target)
        diff = torch.abs(cdf_prediction - cdf_target)

        return torch.trapz(diff**2, x)

    def _calculate_cdf(self, x: torch.Tensor, data: torch.Tensor):
        # use sigmoid to approximate the cdf, since genuine method:
        # return torch.mean((data.unsqueeze(1) <= x.unsqueeze(0)).float(), dim=0)
        # is not continuous.
        return torch.mean(torch.sigmoid((x.unsqueeze(0) - data.unsqueeze(1)) * 1000), dim=0)


class L1CRPS(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, prediction, target):
        sort_p, _ = torch.sort(torch.flatten(prediction))
        sort_t, _ = torch.sort(torch.flatten(target))
        dx = torch.abs(sort_p - sort_t)
        loss = torch.sum(dx) / torch.numel(target)

        return loss
```

## File: src/dlamp/models/model_utils.py
```python
from importlib import import_module
from math import ceil, floor

import numpy as np
import torch
from einops import rearrange
from torch import nn
from torch.optim.lr_scheduler import LambdaLR


def get_builder(model_name: str):
    return getattr(import_module("..", __name__), f"{model_name}Builder")


def window_partition_3d(
    input_feature: torch.Tensor,
    window_size: tuple[int, int, int],
    combine_img_dim: bool = False,
) -> torch.Tensor:
    """
    Partitions the given input into windows.

    Args:
        input_feature (tensor): (B, Z, H, W, C)
        window_size (tuple[int, int, int]): attention window's shape (wZ, wH, wW)
        combine_img_dim (bool): whether to combine the image dimensions into one channel
    Returns:
        torch.Tensor: Tensor of shape (B * num_windows, wZ, wH, wW, C) or (B * num_windows, wZ*wH*wW, C)
            if `combine_img_dim` is True
    """
    arg = "(b nZ nH nW) (wZ wH wW) c" if combine_img_dim else "(b nZ nH nW) wZ wH wW c"
    windows = rearrange(
        input_feature,
        "b (nZ wZ) (nH wH) (nW wW) c -> " + arg,
        wZ=window_size[0],
        wH=window_size[1],
        wW=window_size[2],
    )
    return windows


def window_reverse_3d(
    windows: torch.Tensor,
    window_size: tuple[int, int, int],
    orig_img_size: tuple[int, int, int],
    from_combine_dim: bool = False,
) -> torch.Tensor:
    """
    Merges windows to produce higher resolution features.

    Args:
        windows (torch.Tensor): Tensor of shape (B * num_windows, wZ, wH, wW, C) or (B * num_windows, wZ*wH*wW, C)
            if `from_combined_img_dim` is True
        window_size (tuple[int, int, int]): window size (wZ, wH, wW)
        orig_img_size (tuple[int, int, int]): original image size (Z, H, W)
        from_combine_dim (bool): whether the input tensor is the same shape as `combine_img_dim=True` from
            `window_partition_3d`
    Returns:
        torch.Tensor: Tensor of shape (B, Z, H, W, C)
    """
    arg = "(b nZ nH nW) (wZ wH wW) c" if from_combine_dim else "(b nZ nH nW) wZ wH wW c"
    nZ, nH, nW = map(lambda x, y: x // y, orig_img_size, window_size)
    orig_img = rearrange(
        windows,
        arg + " -> b (nZ wZ) (nH wH) (nW wW) c",
        nZ=nZ,
        nH=nH,
        nW=nW,
        wZ=window_size[0],
        wH=window_size[1],
        wW=window_size[2],
    )
    return orig_img


def pad_3d(img_shape: tuple[int, int, int], sub_shape: tuple[int, int, int]) -> nn.ZeroPad3d:
    """
    Get nn.ZeroPad3d for padding the input to be divisible by sub_shape.

    Args:
        img_shape (tuple[int, int, int]): Shape of the input tensor (Z, H, W).
        sub_shape (tuple[int, int, int]): Shape of the sub tensor (z, h, w).
    Returns:
        nn.ZeroPad3d: Padding layer.
    """
    Z, H, W = img_shape
    z, h, w = sub_shape
    pad = nn.ZeroPad3d(
        (
            floor((-W % w) / 2),
            ceil((-W % w) / 2),
            floor((-H % h) / 2),
            ceil((-H % h) / 2),
            floor((-Z % z) / 2),
            ceil((-Z % z) / 2),
        )
    )
    return pad


def pad_2d(img_shape: tuple[int, int], sub_shape: tuple[int, int]) -> nn.ZeroPad2d:
    """
    Get nn.ZeroPad2d for padding the input to be divisible by sub_shape.

    Args:
        img_shape (tuple[int, int]): Shape of the input tensor (H, W).
        sub_shape (tuple[int, int]): Shape of the sub tensor (h, w).
    Returns:
        nn.ZeroPad2d: Padding layer.
    """
    H, W = img_shape
    h, w = sub_shape
    pad = nn.ZeroPad2d(
        (
            floor((-W % w) / 2),
            ceil((-W % w) / 2),
            floor((-H % h) / 2),
            ceil((-H % h) / 2),
        )
    )
    return pad


def crop_pad_3d(img_shape: tuple[int, int, int], sub_shape: tuple[int, int, int]) -> tuple[slice, slice, slice]:
    """
    Get the index for reversing padding via GetPad3D.

    Args:
        img_shape (tuple[int, int, int]): Shape of the input tensor (Z, H, W).
        sub_shape (tuple[int, int, int]): Shape of the sub tensor (z, h, w).
    Returns:
        tuple[slice, slice, slice]: Crop index.
    """
    Z, H, W = img_shape
    z, h, w = sub_shape
    return (
        slice(floor((-Z % z) / 2), -ceil((-Z % z) / 2)) if Z % z != 0 else slice(None),
        slice(floor((-H % h) / 2), -ceil((-H % h) / 2)) if H % h != 0 else slice(None),
        slice(floor((-W % w) / 2), -ceil((-W % w) / 2)) if W % w != 0 else slice(None),
    )


def crop_pad_2d(img_shape: tuple[int, int], sub_shape: tuple[int, int]) -> tuple[slice, slice]:
    """
    Get the index for reversing padding via GetPad2D.

    Args:
        img_shape (tuple[int, int]): Shape of the input tensor (H, W).
        sub_shape (tuple[int, int]): Shape of the sub tensor (h, w).
    Returns:
        tuple[slice, slice]: Crop index.
    """
    H, W = img_shape
    h, w = sub_shape
    return (
        slice(floor((-H % h) / 2), -ceil((-H % h) / 2)) if H % h != 0 else slice(None),
        slice(floor((-W % w) / 2), -ceil((-W % w) / 2)) if W % w != 0 else slice(None),
    )


def is_divisible_elementwise(list1: list[int], list2: list[int]) -> bool:
    """
    Check if each element in list1 is divisible by the corresponding element in list2.

    Args:
        list1 (list[int]): List of integers.
        list2 (list[int]): List of integers.

    Returns:
        bool: True if all elements are divisible element-wise, False otherwise.
    """
    assert len(list1) == len(list2)
    return all(x % y == 0 for x, y in zip(list1, list2))


def get_scheduler_with_warmup(
    optimizer: torch.optim.Optimizer,
    schedule_type: str,
    training_steps: int,
    warmup_steps: int | None = None,
    warmup_epochs: int | None = None,
    cycles: float = 0.5,
    last_epoch: int = -1,
) -> LambdaLR:
    def cosine_decay(current_step):
        # Warmup
        if current_step < warmup_steps:
            return current_step / max(1, warmup_steps)
        # decadence
        progress = (current_step - warmup_steps) / max(1, training_steps - warmup_steps)
        return max(0.0, 0.5 * (1.0 + np.cos(np.pi * float(cycles) * 2.0 * progress)))

    def constant(current_step):
        return 1.0

    def constant_warmup(current_step):
        if current_step < warmup_steps:
            return current_step / max(1, warmup_steps)
        return 1.0

    def linear_decay(current_epoch):
        if current_epoch <= warmup_epochs:
            lr_scale = 1.0
        else:
            overflow = current_epoch - warmup_epochs
            lr_scale = 0.995**overflow
            lr_scale = max(lr_scale, 0.05)
        return lr_scale

    match schedule_type:
        case "cosine":
            return LambdaLR(optimizer, cosine_decay, last_epoch)
        case "constant":
            return LambdaLR(optimizer, constant, last_epoch)
        case "constant_warmup":
            return LambdaLR(optimizer, constant_warmup, last_epoch)
        case "linear_decay":
            return LambdaLR(optimizer, linear_decay, last_epoch)
        case _:
            raise ValueError(f"Unsupported schedule type: {schedule_type}")


class RunningAverage:
    def __init__(self):
        self._N = 0
        self._sum = 0

    def get(self):
        if self._N > 0:
            return self._sum / self._N

        return None

    def reset(self):
        self._N = 0
        self._sum = 0

    def add(self, val, n):
        self._N += n
        self._sum += val


def restruct_dimension(x_upper, x_surface, is_numpy=False, device=None):
    """
    Args:
        x_upper (torch.Tensor): Tensor of shape (B, Lv, H, W, C1)
        x_surface (torch.Tensor): Tensor of shape (B, 1, H, W, C2)
        is_numpy (bool, optional): Whether the input is in numpy format
        device (torch.device, optional): Device of the output tensor

    Returns:
        torch.Tensor: Tensor of shape (B, Lv*C1+C2, H, W)
    """
    if is_numpy and device is not None:
        x_upper = torch.from_numpy(x_upper).to(device)
        x_surface = torch.from_numpy(x_surface).to(device)
    elif is_numpy and device is None:
        raise ValueError("If `is_numpy` is True, `device` must be provided.")

    x_upper = rearrange(x_upper, "b z h w c -> b (z c) h w")
    x_surface = rearrange(x_surface, "b 1 h w c -> b c h w")
    x = torch.cat([x_upper, x_surface], dim=1)
    return x


def deconstruct(x: torch.Tensor, upper_ch: int, surface_ch: int) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Deconstructs a tensor `x` into two tensors `x_upper` and `x_surface`.

    Args:
        x (torch.Tensor): The input tensor of shape (B, Lv*C1+C2, H, W).
        upper_ch (int): The number of channels in the upper layer (C1).
        surface_ch (int): The number of channels in the surface layer (C2).

    Returns:
        tuple[torch.Tensor, torch.Tensor]: A tuple containing `x_upper` and `x_surface`.
            - `x_upper` (torch.Tensor): The upper layer tensor of shape (B, Lv, H, W, C1).
            - `x_surface` (torch.Tensor): The surface layer tensor of shape (B, 1, H, W, C2).
    """
    x_upper, x_surface = x[:, :-surface_ch], x[:, -surface_ch:]
    x_upper = rearrange(x_upper, "b (z c) h w -> b z h w c", c=upper_ch)
    x_surface = rearrange(x_surface, "b c h w -> b 1 h w c")
    return x_upper, x_surface
```

## File: src/dlamp/utils/test_data_type.py
```python
from dlamp.utils.data_type import DataType


def test_data_type_attributes():
    # Test for TK (Temperature)
    assert DataType.TK.short_name == "TK"
    assert DataType.TK.nc_key == "TK"
    assert DataType.TK.units == "K"
    assert DataType.TK.standard_name == "air_temperature"
    assert "temperature" in DataType.TK.description.lower()

    # Test for Z (Geopotential Height)
    assert DataType.Z.short_name == "Z"
    assert DataType.Z.nc_key == "Z"
    assert "geopotential height" in DataType.Z.description.lower()

    # Test for Lat (Latitude, 1-D coordinate)
    assert DataType.Lat.short_name == "lat"
    assert DataType.Lat.nc_key == "lat"
    assert "latitude" in DataType.Lat.description.lower()

    # Test for XLAT (Latitude meshgrid, 2-D)
    assert DataType.XLAT.short_name == "XLAT"
    assert DataType.XLAT.nc_key == "XLAT"

    # Test for Qt (model input, read directly)
    assert DataType.Qt.nc_key == "Qt"
```

## File: src/dlamp/utils/time_util.py
```python
from datetime import UTC, datetime, timedelta

import numpy as np


class TimeUtil:
    @staticmethod
    def entire_period(
        year: int,
        month: int,
        day: int,
        hour: int | None = None,
        interval: dict[str, int] | timedelta | None = None,
    ) -> list[datetime]:
        """
        Generate a list of datetime objects representing the entire period for a given date and time interval.

        Parameters:
            year (int): The year of the target date.
            month (int): The month of the target date.
            day (int): The day of the target date.
            hour (int | None, optional): The hour of the target date. Defaults to None.
            interval (dict[str, int] | timedelta, optional): The time interval used to iterate through the target dates.
                The keys of the dictionary must be one of the following: "days", "seconds", "microseconds",
                "milliseconds", "minutes", "hours", "weeks". Defaults to {"minutes": 1}.

        Returns:
            list[datetime]: A list of datetime objects representing the entire period for the given date and time interval.
        """
        if isinstance(interval, dict):
            interval = timedelta(**interval)
        if interval is None:
            interval = timedelta(minutes=1)
        time_list = []
        if hour:
            dt = datetime(year, month, day, hour, tzinfo=UTC)
            while dt.hour == hour:
                time_list.append(dt)
                dt += interval
        else:
            dt = datetime(year, month, day, tzinfo=UTC)
            while dt.day == day:
                time_list.append(dt)
                dt += interval
        return time_list

    @staticmethod
    def N_days_time_list(
        year: int,
        month: int,
        day: int,
        interval: dict[str, int] | timedelta,
        n_days: int,
    ) -> list[datetime]:
        """
        Generate a list of datetime objects representing the three days before and after a given date.

        Parameters:
            year (int): The year of the target date.
            month (int): The month of the target date.
            day (int): The day of the target date.
            interval (dict[str, int] | timedelta): The time interval used to iterate through the target dates.
                The keys of the dictionary must be one of the following: "days", "seconds", "microseconds",
                "milliseconds", "minutes", "hours", "weeks". Defaults to {"minutes": 1}.

        Returns:
            list[datetime]: A list of datetime objects representing the three days before and after the given date.
        """
        assert n_days >= 1, f"n_days must be a positive integer but get {n_days}"
        half_range = n_days // 2
        start = -half_range if n_days > 1 else 0
        end = half_range + 1 if n_days % 2 == 1 else half_range

        target_t = [datetime(year, month, day, tzinfo=UTC) + i * timedelta(days=1) for i in range(start, end)]

        time_list = []
        for calendar in target_t:
            time_list.extend(TimeUtil.entire_period(calendar.year, calendar.month, calendar.day, interval=interval))
        return time_list

    @staticmethod
    def create_time_features(curr_dt: datetime, array_shape: tuple[int, int]) -> np.ndarray:
        """
        Computes the sine and cosine transformations of the Day of Year (DoY) and Time
        of Day (ToD) from the provided datetime object and returns arrays of the specified
        shape filled with these values.

        Parameters:
        - curr_dt (datetime): The datetime object for which to compute DoY and ToD.
        - array_shape (tuple): The desired 2D shape of the output arrays.

        Returns:
        - time_features (np.ndarray): Array of shape (**array_shape, 4) filled with the
            computed DoY and ToD values.
        """
        assert len(array_shape) == 2, "array_shape must be a tuple of length 2"

        # Calculate Day of Year (DoY)
        doy = curr_dt.timetuple().tm_yday

        # Calculate Time of Day (ToD) in hours
        tod = curr_dt.hour + curr_dt.minute / 60 + curr_dt.second / 3600

        # Compute sine and cosine transformations for DoY
        doy_sin = np.sin(2 * np.pi * doy / 365.0)
        doy_cos = np.cos(2 * np.pi * doy / 365.0)

        # Compute sine and cosine transformations for ToD
        tod_sin = np.sin(2 * np.pi * tod / 24.0)
        tod_cos = np.cos(2 * np.pi * tod / 24.0)

        # Create arrays filled with the computed values
        doy_sin_array = np.full(array_shape, doy_sin, dtype=np.float32)
        doy_cos_array = np.full(array_shape, doy_cos, dtype=np.float32)
        tod_sin_array = np.full(array_shape, tod_sin, dtype=np.float32)
        tod_cos_array = np.full(array_shape, tod_cos, dtype=np.float32)

        # stack the arrays (H, W, 4)
        time_features = np.stack([doy_sin_array, doy_cos_array, tod_sin_array, tod_cos_array], axis=-1)

        return time_features
```

## File: src/dlamp/visual/__init__.py
```python
"""Public exports for the visual subpackage."""

from .tw_background import TwBackground
from .viz_gph import VizGph
from .viz_mixing_ratio import VizMixingRatio
from .viz_omega import VizOmega
from .viz_pressure import VizPressure
from .viz_radar import VizRadar
from .viz_swdown import VizSwdown
from .viz_temp import VizTemp
from .viz_vor import VizVor
from .viz_wind import VizWind

__all__ = [
    "TwBackground",
    "VizGph",
    "VizMixingRatio",
    "VizOmega",
    "VizPressure",
    "VizRadar",
    "VizSwdown",
    "VizTemp",
    "VizVor",
    "VizWind",
]
```

## File: src/dlamp/visual/tw_background.py
```python
import geopandas as gpd
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from dlamp.const import COUNTY_SHP_PATH


class TwBackground:
    def __init__(self):
        self.canvas_settings()
        self.county_data = gpd.read_file(COUNTY_SHP_PATH)

    def canvas_settings(self) -> None:
        font = {"family": "sans-serif", "weight": "bold", "size": 14}
        axes = {
            "titlesize": 16,
            "titleweight": "bold",
            "labelsize": 14,
            "labelweight": "bold",
        }
        mpl.rc("font", **font)  # pass in the font dict as kwargs
        mpl.rc("axes", **axes)

    def plot_bg(self, fig: Figure, ax: Axes, grid_on: bool = False) -> tuple[Figure, Axes]:
        """
        Plots the county data on a figure
        """
        # fig.patch.set_visible(False)
        # ax.axis("off")
        ax = self.county_data.plot(ax=ax, color="none", edgecolor="k", linewidth=1, zorder=1)

        # canvas setting
        # ax.set_xlim(118, 123.5) # QPESUMS
        # ax.set_ylim(20, 27) # QPESUMS
        # ax.set_xlim(116, 125.7)  # full RWRF
        # ax.set_ylim(19.4, 28)  # full RWRF
        ax.set_xlim(116.5, 125)  # 224x224 RWRF
        ax.set_ylim(19.75, 27.75)  # 224x224 RWRF
        # ax.set_xlim(117.5, 124.2)  # 336x336 RWRF
        # ax.set_ylim(20.6, 26.8)  # 336x336 RWRF

        # default grid zorder is 2.5
        if grid_on:
            ax.grid(True, linestyle="--", color="k", alpha=0.8)

        return fig, ax
```

## File: src/dlamp/visual/viz_gph.py
```python
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .tw_background import TwBackground


class VizGph(TwBackground):
    def __init__(self, pressure_level: int | None = None):
        """
        This class plot geopotential height (Z) for a given pressure level.
        If you have geopotential ($phi$), Z = phi / g0 where g0 = 9.80665 m/s^2.
        """
        super().__init__()
        self.press_lv = pressure_level
        self.title_suffix = f"GPH@{self.press_lv}" if pressure_level else ""

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: list[np.ndarray],
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []

        cols = len(data)

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(15, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_gph(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax

    def _plot_gph(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[plt.Figure, plt.Axes]:
        conf = ax.contour(
            lon,
            lat,
            data,
            levels=np.linspace(5550, 5900, 15),
            cmap="viridis",
            zorder=0,
        )

        # inline lables
        clabels = ax.clabel(conf, inline=True, colors="k", fontsize=10, use_clabeltext=False)
        for label in clabels:
            label.set_path_effects(
                [
                    path_effects.Stroke(linewidth=2, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("m")

        return fig, ax
```

## File: src/dlamp/visual/viz_mixing_ratio.py
```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .tw_background import TwBackground


class VizMixingRatio(TwBackground):
    def __init__(self, pressure_level: int | None = None):
        super().__init__()
        self.press_lv = pressure_level
        self.title_suffix = f"Q@{self.press_lv}" if pressure_level else ""

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: list[np.ndarray],
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = len(data)

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(15, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_q(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax)
        fig, ax = self._plot_q(fig, ax, lon, lat, data, title)

        return fig, ax

    def _plot_q(
        self,
        fig: plt.Figure,
        ax: plt.Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        # data *= 1000  # kg/kg -> g/kg
        conf = ax.contourf(
            lon,
            lat,
            data,
            levels=np.arange(0, 2.1, 0.1),
            cmap="BuPu",
            # cmap="BrBG",
            zorder=0,
        )

        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("g/kg")

        return fig, ax
```

## File: src/dlamp/visual/viz_omega.py
```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .tw_background import TwBackground


class VizOmega(TwBackground):
    def __init__(self):
        super().__init__()

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax, grid_on)
        fig, ax = self._plot_omega(fig, ax, lon, lat, data, title)

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = data.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_omega(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax

    def _plot_omega(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        # data = -data  # omega to w
        conf = ax.contourf(
            lon,
            lat,
            data,
            cmap="bwr",
            levels=np.arange(-0.5, 0.5, 0.05),
            zorder=0,
            extend="both",
        )

        if title:
            ax.set_title(title)

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("$\\frac{m}{s}$")

        return fig, ax
```

## File: src/dlamp/visual/viz_pressure.py
```python
from datetime import datetime

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .tw_background import TwBackground


class VizPressure(TwBackground):
    def __init__(self):
        super().__init__()

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax, grid_on)
        fig, ax = self._plot_pressure(fig, ax, lon, lat, data, title)

        return fig, ax

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth: np.ndarray,
        prediction: np.ndarray,
        all_init_times: list[datetime] | None = None,
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        """
        Args:
            lon (np.ndarray): The longitude data with shape (H, W).
            lat (np.ndarray): The latitude data with shape (H, W).
            ground_truth (np.ndarray): The ground truth data with shape (S, H, W).
            prediction (np.ndarray): The predicted data with shape (S, H, W).
            all_init_times (list[datetime]): A list of all initial times in length S.
            grid_on (bool, optional): Whether to show grid. Defaults to False.
        """
        if all_init_times is None:
            all_init_times = []
        assert len(ground_truth.shape) == 3
        assert ground_truth.shape[-2:] == lat.shape

        rows = 2  # gt/pred
        columns = ground_truth.shape[0]

        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_pressure(fig, tmp_ax, lon, lat, ground_truth[j], time_title)

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_pressure(fig, tmp_ax, lon, lat, prediction[j], time_title)

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = data.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_pressure(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax

    def _plot_pressure(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        data = np.round(data / 100)  # pa to hpa
        conf = ax.contourf(
            lon,
            lat,
            data,
            cmap="viridis",
            levels=np.arange(900, 1005, 5),
            zorder=0,
            extend="both",
        )

        # inline lables
        clabels = ax.clabel(conf, inline=True, colors="k", fontsize=10, use_clabeltext=False)
        for label in clabels:
            label.set_path_effects(
                [
                    path_effects.Stroke(linewidth=2, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        if title:
            ax.set_title(title)

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("hpa")

        return fig, ax
```

## File: src/dlamp/visual/viz_swdown.py
```python
from datetime import datetime

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from .tw_background import TwBackground


class VizSwdown(TwBackground):
    def __init__(self):
        super().__init__()

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax, grid_on)
        fig, ax = self._plot_swdown(fig, ax, lon, lat, data, title)

        return fig, ax

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth: np.ndarray,
        prediction: np.ndarray,
        all_init_times: list[datetime] | None = None,
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        """
        Args:
            lon (np.ndarray): The longitude data with shape (H, W).
            lat (np.ndarray): The latitude data with shape (H, W).
            ground_truth (np.ndarray): The ground truth data with shape (S, H, W).
            prediction (np.ndarray): The predicted data with shape (S, H, W).
            all_init_times (list[datetime]): A list of all initial times in length S.
            grid_on (bool, optional): Whether to show grid. Defaults to False.
        """
        if all_init_times is None:
            all_init_times = []
        assert len(ground_truth.shape) == 3
        assert ground_truth.shape[-2:] == lat.shape

        rows = 2  # gt/pred
        columns = ground_truth.shape[0]

        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_pressure(fig, tmp_ax, lon, lat, ground_truth[j], time_title)

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_swdown(fig, tmp_ax, lon, lat, prediction[j], time_title)

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = data.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_swdown(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax

    def _plot_swdown(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        data = np.round(data / 100)  # pa to hpa
        conf = ax.contourf(
            lon,
            lat,
            data,
            cmap="viridis",
            levels=np.arange(-40, 400, 40),  # SWDOWN
            # levels=np.arange(0, 300, 30),  # OLR
            zorder=0,
            extend="both",
        )

        # inline lables
        clabels = ax.clabel(conf, inline=True, colors="k", fontsize=10, use_clabeltext=False)
        for label in clabels:
            label.set_path_effects(
                [
                    path_effects.Stroke(linewidth=2, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        if title:
            ax.set_title(title)

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("$\\frac{W}{m^2}$")

        return fig, ax
```

## File: src/dlamp/visual/viz_wind.py
```python
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dlamp.const import FIGURE_PATH, WSP_COLOR, WSP_LV
from dlamp.utils import DataCompose, DataType, Level, gen_data

from .tw_background import TwBackground


class VizWind(TwBackground):
    def __init__(self, pressure_level: str | None = None):
        super().__init__()
        self.press_lv = pressure_level
        self.title_suffix = f"Wind@{self.press_lv}" if pressure_level else ""

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth_u: np.ndarray,
        ground_truth_v: np.ndarray,
        prediction_u: np.ndarray,
        prediction_v: np.ndarray,
        all_init_times: list[datetime] | None = None,
    ) -> tuple[Figure, Axes]:
        assert len(ground_truth_u.shape) == 3
        assert ground_truth_u.shape[-2:] == lat.shape

        rows = 2  # gt/pred
        columns = ground_truth_u.shape[0]
        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax)
            fig, tmp_ax = self._plot_wind(fig, tmp_ax, lon, lat, ground_truth_u[j], ground_truth_v[j], time_title)

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax)
            fig, tmp_ax = self._plot_wind(fig, tmp_ax, lon, lat, prediction_u[j], prediction_v[j], time_title)

        return fig, ax

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind: np.ndarray,
        v_wind: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:

        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax)
        fig, ax = self._plot_wind(fig, ax, lon, lat, u_wind, v_wind, title)

        return fig, ax

    def _plot_wind(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind: np.ndarray,
        v_wind: np.ndarray,
        title: str = "",
        quiver_only: bool = False,
    ) -> tuple[Figure, Axes]:
        # since lat/lon may not be monotonically increasing in a same pace
        if len(lat.shape) == 2 and len(lon.shape) == 2:
            lat = np.linspace(lat[0, 0], lat[-1, 0], lat.shape[0])
            lon = np.linspace(lon[0, 0], lon[0, -1], lon.shape[1])

        # wind speed
        scalar = np.hypot(u_wind, v_wind)

        # plot data
        ax.streamplot(lon, lat, u_wind, v_wind, zorder=0, color="C0", linewidth=0.5, arrowsize=0.6)

        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        if not quiver_only:
            conf = ax.contourf(
                lon,
                lat,
                scalar,
                levels=WSP_LV,
                colors=WSP_COLOR,
                zorder=-1,
            )

            # create an axes on the right side of ax. The width of cax will be 5%
            # of ax and the padding between cax and ax will be fixed at 0.05 inch.
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)

            # colorbar
            cbar = fig.colorbar(conf, cax=cax)
            cbar.ax.set_title("$\\frac{m}{s}$")

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind_list: np.ndarray,
        v_wind_list: np.ndarray,
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = u_wind_list.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_wind(fig, tmp_ax, lon, lat, u_wind_list[j], v_wind_list[j], title)

        return fig, ax


if __name__ == "__main__":
    target_time = datetime(2022, 10, 16, 0, tzinfo=UTC)
    u850 = gen_data(target_time, DataCompose(DataType.U, Level.Hpa850))
    v850 = gen_data(target_time, DataCompose(DataType.V, Level.Hpa850))
    data_lat = gen_data(target_time, DataCompose(DataType.Lat, Level.Surface))
    data_lon = gen_data(target_time, DataCompose(DataType.Lon, Level.Surface))

    viz = VizWind("Hpa850")
    fig, ax = viz.plot_1x1(data_lon, data_lat, u850, v850)
    fig.savefig(
        f"{FIGURE_PATH}/{target_time.strftime('%Y%m%d_%H%M')}_wind.png",
        transparent=False,
    )
    plt.close()
```

## File: src/dlamp/workflows/data_prep_runner.py
```python
"""Data preparation workflow runner for the DLAMP pipeline.

Generates constant-mask artefacts (land-sea mask, topography mask) that
are required by downstream training and inference workflows.  Three mask
sources are supported, selected by ``cfg.data_prep.method``:

- ``extract_from_nc``  — extract masks from an existing WRF NetCDF file
  (default, recommended when model output is available)
- ``gen_tw_cn_terrain`` — interpolate from a GeoTIFF raster covering
  East Asia (requires ``assets/terrain_shp/gt30e100n40.tif``)
- ``gen_tw_only_terrain`` — interpolate from a Taiwan-specific shapefile
  (requires ``assets/terrain_shp/GIS_terrain.shp``)

Raises:
    ValueError: If ``cfg.data_prep.method`` is not one of the supported
        values listed above.
    FileNotFoundError: If a required source file cannot be located.
"""

import logging
from pathlib import Path
from typing import Any

from omegaconf import DictConfig

from dlamp.runtime_config import RuntimeConfig, get_runtime_config

logger = logging.getLogger(__name__)

_SUPPORTED_METHODS = frozenset({"extract_from_nc", "gen_tw_cn_terrain", "gen_tw_only_terrain"})


class DataPrepRunner:
    """Runs the data-preparation (constant-mask generation) workflow.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        runtime_config (RuntimeConfig): The validated runtime configuration
            singleton for the current process.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the DataPrepRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain a ``data_prep.method`` key whose value is one of
                the supported mask-generation methods.

        Raises:
            ValueError: If ``cfg.data_prep.method`` is not supported.
        """
        self.cfg = cfg
        self.runtime_config: RuntimeConfig = get_runtime_config()

        method: str = cfg.data_prep.method
        if method not in _SUPPORTED_METHODS:
            raise ValueError(f"Unsupported data_prep.method '{method}'. Choose from: {sorted(_SUPPORTED_METHODS)}")
        self._method = method

    def run(self) -> dict[str, Any]:
        """Executes the mask-generation workflow.

        Dispatches to the appropriate helper based on
        ``self._method`` and logs the paths of artefacts written.

        Returns:
            dict[str, Any]: A summary containing:
                - ``method`` (str): The method used.
                - ``output_dir`` (str): Directory where masks were written.
                - ``artifacts`` (list[str]): Absolute paths of files written.

        Raises:
            FileNotFoundError: If a required source raster or NetCDF file
                is missing.
        """
        logger.info("DataPrepRunner: method=%s", self._method)

        if self._method == "extract_from_nc":
            artifacts = self._extract_from_nc()
        elif self._method == "gen_tw_cn_terrain":
            artifacts = self._gen_tw_cn_terrain()
        else:
            artifacts = self._gen_tw_only_terrain()

        out_dir = str(self.runtime_config.standardization_path.parent / "constant_masks")
        logger.info("DataPrepRunner: wrote %d artefact(s) to %s", len(artifacts), out_dir)
        return {"method": self._method, "output_dir": out_dir, "artifacts": artifacts}

    # ------------------------------------------------------------------
    # Private helpers — delegate to generate_const_masks functions
    # ------------------------------------------------------------------

    def _extract_from_nc(self) -> list[str]:
        """Extract land-sea and topography masks from a WRF NetCDF file.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.
        """
        import numpy as np
        import xarray as xr
        import yaml

        from dlamp.const import REPO_ROOT
        from dlamp.utils import gen_path

        rc = self.runtime_config
        with open(rc.data_config_path, "r") as fh:
            data_config = yaml.safe_load(fh)

        from datetime import UTC, datetime

        start_t = datetime.strptime(data_config["start_time"], data_config["format"]).replace(tzinfo=UTC)
        filename = gen_path(start_t)
        if not Path(str(filename)).exists():
            raise FileNotFoundError(
                f"Source NetCDF not found: {filename}. Ensure DLAMP_DATA_PATH and DLAMP_EXP_CODE are correct."
            )

        data_shape = data_config["data_shape"]
        img_shape = data_config["image_shape"]

        dataset = xr.open_dataset(str(filename))
        terrain = dataset["HGT"].values.squeeze()
        landsea = dataset["LANDMASK"].values.squeeze()
        assert tuple(data_shape) == terrain.shape == landsea.shape, (
            f"Shape mismatch: data_shape={data_shape}, terrain={terrain.shape}"
        )

        terrain = terrain[1:-1, 1:-1]
        landsea = landsea[1:-1, 1:-1]
        terrain_mask = terrain[::2, ::2]
        landsea_mask = landsea[::2, ::2]
        assert tuple(img_shape) == terrain_mask.shape == landsea_mask.shape

        out_dir = REPO_ROOT / "assets" / "constant_masks"
        out_dir.mkdir(parents=True, exist_ok=True)
        topo_path = out_dir / "topography_mask_4km.npy"
        land_path = out_dir / "land_sea_mask_4km.npy"
        np.save(topo_path, terrain_mask)
        np.save(land_path, landsea_mask)
        return [str(topo_path), str(land_path)]

    def _gen_tw_cn_terrain(self) -> list[str]:
        """Interpolate masks from a GeoTIFF raster covering East Asia.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.

        Raises:
            FileNotFoundError: If the GeoTIFF raster is not present.
        """
        from dlamp.generate_const_masks import gen_TW_CN_terrain

        gen_TW_CN_terrain()
        rc = self.runtime_config
        out_dir = rc.standardization_path.parent / "constant_masks"
        return [
            str(out_dir / "topography_mask_4km.npy"),
            str(out_dir / "land_sea_mask_4km.npy"),
        ]

    def _gen_tw_only_terrain(self) -> list[str]:
        """Interpolate masks from a Taiwan-specific point shapefile.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.

        Raises:
            FileNotFoundError: If the shapefile is not present.
        """
        from dlamp.generate_const_masks import gen_TW_only_terrain

        gen_TW_only_terrain()
        rc = self.runtime_config
        out_dir = rc.standardization_path.parent / "constant_masks"
        return [
            str(out_dir / "topography_mask_4km.npy"),
            str(out_dir / "land_sea_mask_4km.npy"),
        ]
```

## File: src/dlamp/workflows/data_stats_runner.py
```python
"""Data-statistics workflow runner for the DLAMP pipeline.

Computes per-variable z-score statistics (mean and standard deviation)
from a random sample of raw NetCDF data and writes the results to the
standardization JSON file specified by ``RuntimeConfig``.

The computation is delegated to ``dlamp.standardizer.Standardizer.
calc_standardization``.  If a variable already exists in the JSON it is
skipped, so the script can be re-run safely after interruption.

Raises:
    RuntimeConfigError: If the model code does not match an existing
        data-config or standardization file on disk.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from omegaconf import DictConfig

from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import Standardizer, get_standardizer

logger = logging.getLogger(__name__)


class DataStatsRunner:
    """Runs the z-score standardization-statistics computation workflow.

    Wraps ``Standardizer.calc_standardization`` and exposes all four
    configurable parameters via the Hydra config object so that they can
    be overridden on the command line without touching source code.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        standardizer (Standardizer): The singleton Standardizer instance
            for the current process, pre-loaded with any existing stats.
    """

    def __init__(self, cfg: DictConfig, runtime_config: RuntimeConfig) -> None:
        """Initialises the DataStatsRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain a ``stats`` group with keys: ``start_time``,
                ``end_time``, ``sample_size``, ``num_criteria``.
            runtime_config (RuntimeConfig): The validated runtime
                configuration singleton for the current process.
        """
        self.cfg = cfg
        self.standardizer: Standardizer = get_standardizer(runtime_config)
        self._start_time: datetime = datetime.strptime(cfg.stats.start_time, "%Y-%m-%d %H:%M").replace(
            tzinfo=UTC
        )
        self._end_time: datetime = datetime.strptime(cfg.stats.end_time, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
        self._sample_size: int = cfg.stats.sample_size
        self._num_criteria: int = cfg.stats.num_criteria

    def run(self) -> dict[str, Any]:
        """Executes the statistics computation workflow.

        Iterates over all variables in the data config and computes z-score
        statistics for those not already present in the JSON file.

        Returns:
            dict[str, Any]: A summary containing:
                - ``standardization_path`` (str): Path to the JSON written.
                - ``start_time`` (str): Start of the sampling window.
                - ``end_time`` (str): End of the sampling window.
                - ``sample_size`` (int): Number of random pixels per frame.
                - ``num_criteria`` (int): Minimum samples required to keep
                    a variable's statistics.
        """
        logger.info(
            "DataStatsRunner: computing stats for %s → %s (sample_size=%d, num_criteria=%d)",
            self._start_time.date(),
            self._end_time.date(),
            self._sample_size,
            self._num_criteria,
        )
        self.standardizer.calc_standardization(
            start_time=self._start_time,
            end_time=self._end_time,
            sample_size=self._sample_size,
            num_criteria=self._num_criteria,
        )
        json_path = str(self.standardizer._config.standardization_path)
        logger.info("DataStatsRunner: stats written to %s", json_path)
        return {
            "standardization_path": json_path,
            "start_time": str(self._start_time),
            "end_time": str(self._end_time),
            "sample_size": self._sample_size,
            "num_criteria": self._num_criteria,
        }
```

## File: src/dlamp/workflows/predict_feedback_runner.py
```python
"""Two-way boundary-feedback inference workflow runner for DLAMP.

Executes the auto-regression loop with boundary re-injection at **every
model time-step**.  At each 1-hour step the boundary ring of the
predicted field is overwritten with observations loaded from disk before
the prediction is fed back as the next input — this is the "two-way
feedback" or "nudging" mode that prevents error accumulation near the
domain edges.

The feedback is implemented by setting a non-null ``bdy_swap_method``
in the Hydra config, which the underlying
``BatchInferenceOnnx.infer()`` / ``BatchInferenceCkpt.infer()`` loop
already accepts.  This runner validates that the required config keys
are present and provides a descriptive error if the caller forgets to
set them.

Decision record (Q1 from implementation plan):
    Boundary re-injection fires at every model time-step (the 1-hour
    inner loop in ``BatchInferenceOnnx.infer``), not only at
    ``output_itv`` intervals.  This is the strongest form of nudging
    and matches the "two-way" naming convention from the WRF literature.
    If you want nudging only at output intervals, set
    ``inference.bdy_swap_method`` to ``null`` in ``predict_dscale.yaml``
    and apply the swap yourself in post-processing.

Raises:
    ValueError: If ``cfg.inference.bdy_swap_method`` is null — the
        feedback runner requires a concrete swap method.
"""

import logging
from typing import Any

from omegaconf import DictConfig, OmegaConf

from dlamp.analysis.prediction import PredictionRunner

logger = logging.getLogger(__name__)


class PredictFeedbackRunner:
    """Runs the two-way boundary-feedback inference workflow.

    Extends the one-way downscaling approach by enforcing a non-null
    ``bdy_swap_method`` so that boundary conditions from ground-truth
    observations are blended into the model state at every auto-
    regression step.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        _predictor (PredictionRunner): The underlying prediction engine.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the PredictFeedbackRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain:
                - ``inference.bdy_swap_method`` (dict): A non-null dict
                  with at least ``name`` (str) and ``n_of_grid`` (int)
                  keys identifying the blending kernel and the number of
                  boundary grid cells to replace.
                - ``inference.feedback_iters`` (int): Documented key for
                  future use — currently informational only, as the
                  feedback loop length is determined by
                  ``showcase_length`` and ``output_itv`` in the base
                  class.

        Raises:
            ValueError: If ``cfg.inference.bdy_swap_method`` is null or
                missing.
        """
        self.cfg = cfg
        self._validate_feedback_config()
        self._predictor: PredictionRunner = PredictionRunner(cfg)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Executes the two-way boundary-feedback inference.

        The ``bdy_swap_method`` configured in Hydra is forwarded to
        ``InferenceBase.infer()``, which calls
        ``_boundary_swapping()`` at every model time-step inside the
        auto-regression loop.

        Returns:
            dict[str, Any]: Prediction results as returned by
                ``PredictionRunner.run()``, containing:
                - ``output_upper`` (np.ndarray): Upper-air predictions.
                - ``output_surface`` (np.ndarray): Surface predictions.
                - ``lat`` (np.ndarray): Latitude grid.
                - ``lon`` (np.ndarray): Longitude grid.
                - ``mask`` (np.ndarray): Land-sea mask.
                - ``start_time`` (datetime): Forecast start time.
        """
        method_name: str = self.cfg.inference.bdy_swap_method["name"]
        n_grid: int = self.cfg.inference.bdy_swap_method["n_of_grid"]
        logger.info(
            "PredictFeedbackRunner: two-way feedback enabled (method=%s, n_of_grid=%d)",
            method_name,
            n_grid,
        )
        results = self._predictor.run()
        logger.info("PredictFeedbackRunner: inference with feedback complete")
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_feedback_config(self) -> None:
        """Validates that the feedback-specific config keys are present.

        Raises:
            ValueError: If ``cfg.inference.bdy_swap_method`` is null or
                missing the required ``name`` / ``n_of_grid`` sub-keys.
        """
        bdy_method = OmegaConf.select(self.cfg, "inference.bdy_swap_method")
        if not bdy_method:
            raise ValueError(
                "PredictFeedbackRunner requires cfg.inference.bdy_swap_method "
                "to be a non-null dict with 'name' and 'n_of_grid' keys. "
                "Got: null. "
                "Set bdy_swap_method in config/predict_feedback.yaml or pass "
                "'inference.bdy_swap_method.name=<method>' on the CLI."
            )
        for key in ("name", "n_of_grid"):
            if key not in bdy_method:
                raise ValueError(
                    f"cfg.inference.bdy_swap_method is missing key '{key}'. Current value: {dict(bdy_method)}"
                )
```

## File: src/dlamp/const.py
```python
# src/const.py
"""Static constants for the DLAMP pipeline.

This module no longer reads environment variables or performs
side effects at import time. Runtime configuration is now
explicit via ``src.runtime_config.RuntimeConfig``.

All values here are true constants that do not vary between
experiments or model versions.
"""

from datetime import UTC, datetime
from pathlib import Path

import matplotlib as mpl
import numpy as np

REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent

# Static constant paths (do not depend on model code)
BLACKLIST_PATH = str(REPO_ROOT / "assets" / "blacklist_rwrf_3h.txt")
CHECKPOINT_DIR = str(REPO_ROOT / "checkpoints")
LAND_SEA_MASK_PATH = str(REPO_ROOT / "assets" / "constant_masks" / "land_sea_mask_4km.npy")
TOPOGRAPHY_MASK_PATH = str(REPO_ROOT / "assets" / "constant_masks" / "topography_mask_4km.npy")
COUNTY_SHP_PATH = str(REPO_ROOT / "assets" / "town_shp" / "COUNTY_MOI_1090820.shp")
FIGURE_PATH = str(REPO_ROOT / "gallery")

# Variable naming suffix (used in data_compose.py for file basename)
VAR_SUFFIX = "WE01H0202500"

# Radar color bar
DBZ_LV = np.arange(0, 66, 1)
DBZ_COLOR = np.concatenate(
    [
        np.array([[255, 255, 255]]),  # 0
        np.array([np.linspace(0, 0, 14), np.linspace(255, 0, 14), np.linspace(255, 255, 14)]).T,  # 1~14
        np.array([np.linspace(0, 0, 11), np.linspace(255, 150, 11), np.linspace(0, 0, 11)]).T,  # 15~25
        np.array([np.linspace(51, 204, 4), np.linspace(171, 234, 4), np.linspace(0, 0, 4)]).T,  # 26~29
        np.array([np.linspace(255, 255, 5), np.linspace(255, 211, 5), np.linspace(0, 0, 5)]).T,  # 30~34
        np.array([np.linspace(255, 255, 6), np.linspace(200, 120, 6), np.linspace(0, 0, 6)]).T,  # 35~40
        np.array([np.linspace(255, 255, 5), np.linspace(96, 0, 5), np.linspace(0, 0, 5)]).T,  # 41~45
        np.array([np.linspace(244, 150, 10), np.linspace(0, 0, 10), np.linspace(0, 0, 10)]).T,  # 46~55
        np.array([np.linspace(171, 255, 5), np.linspace(0, 0, 5), np.linspace(51, 255, 5)]).T,  # 56~60
        np.array([np.linspace(234, 150, 5), np.linspace(0, 0, 5), np.linspace(255, 255, 5)]).T,  # 61~65
    ]
)
DBZ_COLOR = mpl.colors.ListedColormap(DBZ_COLOR / 255)
DBZ_NORM = mpl.colors.BoundaryNorm(DBZ_LV, DBZ_COLOR.N)

# Rain rate color bar
RR_LV = [
    0,
    1,
    2,
    5,
    10,
    15,
    20,
    30,
    40,
    50,
    70,
    90,
    110,
    130,
    150,
    200,
    300,
]
RR_COLOR = mpl.colors.ListedColormap(
    [
        "#FFFFFF",
        "#9CFCFF",
        "#03C8FF",
        "#059BFF",
        "#0363FF",
        "#059902",
        "#39FF03",
        "#FFFB03",
        "#FFC800",
        "#FF9500",
        "#FF0000",
        "#CC0000",
        "#990000",
        "#960099",
        "#C900CC",
        "#FB00FF",
        "#FDC9FF",
    ]
)
RR_NORM = mpl.colors.BoundaryNorm(RR_LV, RR_COLOR.N)

# Wind speed color bar and intervals
WSP_LV = [
    0,
    4,
    6,
    8,
    10,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    34,
    36,
    38,
    40,
    43,
    46,
    49,
    52,
    55,
    58,
    61,
    64,
    67,
    70,
    73,
    76,
    79,
    82,
    85,
]
WSP_COLOR = [
    "#ffffff",
    "#80ffff",
    "#6fedf1",
    "#5fdde4",
    "#50cdd5",
    "#40bbc7",
    "#2facba",
    "#1f9bac",
    "#108c9f",
    "#007a92",
    "#00b432",
    "#33c341",
    "#67d251",
    "#99e060",
    "#cbf06f",
    "#ffff80",
    "#ffdd52",
    "#ffdc52",
    "#ffa63e",
    "#ff6d29",
    "#ff3713",
    "#ff0000",
    "#d70000",
    "#af0000",
    "#870000",
    "#5f0000",
    "#aa00ff",
    "#b722fe",
    "#c446ff",
    "#d46aff",
    "#e38dff",
    "#f1b1ff",
    "#ffd3ff",
    "#ffc6ea",
    "#ffb6d5",
    "#ffa6c1",
    "#ff97ac",
    "#ff8798",
    "#fe7884",
    "#ff696e",
    "#ff595a",
    "#e74954",
    "#cc3a4c",
    "#b22846",
    "#9a1941",
]

# Temperature color bar and intervals
TEMP_LV = np.linspace(6, 30, 41)
TEMP_COLOR = [
    "#a8acdf",
    "#9092d4",
    "#777acc",
    "#5f63c3",
    "#4949b6",
    "#4655c3",
    "#435aca",
    "#3b6ddf",
    "#3979ef",
    "#3386f5",
    "#2d99fe",
    "#22affe",
    "#1bc2ff",
    "#0ee6fe",
    "#07fbff",
    "#6ee699",
    "#65e08d",
    "#4fd06f",
    "#45c65f",
    "#34bd4b",
    "#28b338",
    "#16a71f",
    "#16a111",
    "#43b121",
    "#66c034",
    "#78c63c",
    "#9ad54d",
    "#c5e763",
    "#e1f26f",
    "#fef87b",
    "#fdeb76",
    "#fad66a",
    "#f9c662",
    "#f8b558",
    "#f6a24e",
    "#ef9043",
    "#e4692c",
    "#e15f27",
    "#cc3513",
    "#c8250a",
    "#c8250a",
]

# Evaluation cases (static dates, do not vary by model)
EVAL_CASES = {
    "one_day": [
        datetime(2021, 6, 4, tzinfo=UTC),  # ATS
        datetime(2022, 6, 24, tzinfo=UTC),  # ATS, observe graupel in Taipei
        datetime(2022, 8, 25, tzinfo=UTC),  # ATS
    ],
    "three_days": [
        datetime(2020, 5, 21, tzinfo=UTC),  # Meiyu
        datetime(2021, 8, 7, tzinfo=UTC),  # South-western flow + Tropical Depression
        datetime(2021, 8, 8, tzinfo=UTC),  # South-western flow
        datetime(2023, 4, 20, tzinfo=UTC),  # cold front
    ],
    "five_days": [
        # == harsh northward turning == #
        # datetime(2022, 9, 3, tzinfo=UTC), # TC HINNAMNOR
        datetime(2022, 9, 12, tzinfo=UTC),  # TC MUIFA
        # datetime(2021, 7, 23, tzinfo=UTC), # TC IN-FA
        # == north-eastern wind accompanied == #
        # datetime(2022, 10, 16, tzinfo=UTC),  # TC NESAT
        # datetime(2022, 10, 31, tzinfo=UTC),  # TC NALGAE
        # == pass by northern Taiwan == #
        # datetime(2020, 8, 3, tzinfo=UTC),  # TC HAGUPI
        # == pass by eastern Taiwan == #
        # datetime(2023, 7, 26, tzinfo=UTC),  # TC DOKSURI
        # == landing == #
        # datetime(2023, 9, 3, tzinfo=UTC),  # TC HAIKUI
        datetime(2024, 7, 24, tzinfo=UTC),  # TC GAEMI
        datetime(2024, 10, 31, tzinfo=UTC),  # TC Kong-rey
    ],
    "seven_days": [
        # == landing == #
        datetime(2024, 10, 3, tzinfo=UTC),  # TC Krathon
    ],
}
```

## File: src/dlamp/export_onnx.py
```python
import hydra
import onnx
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.managers import DataManager
from dlamp.models import PanguLightningModule, get_builder
from dlamp.utils import DataCompose


@hydra.main(version_base=None, config_path=str(REPO_ROOT / "config"), config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)

    # prepare data
    data_list = DataCompose.from_config(cfg.data.train_data)
    data_manager = DataManager(data_list, **cfg.data, **cfg.lightning)
    data_manager.setup("fit")

    # sample data
    data_loader = data_manager.train_dataloader()
    inp_data, _oup_data = next(iter(data_loader))
    inp_data["upper_air"] = inp_data["upper_air"].to("cuda")
    inp_data["surface"] = inp_data["surface"].to("cuda")

    # model builder
    model_builder = get_builder(cfg.model.model_name)(
        "export_onnx",
        data_list,
        image_shape=data_manager.image_shape,
        add_time_features=cfg.data.add_time_features,
        **cfg.model,
        **cfg.lightning,
    )

    # load LightningModule from checkpoint
    pl_module = PanguLightningModule.load_from_checkpoint(
        checkpoint_path=cfg.inference.best_ckpt,
        test_dataloader=None,
        backbone_model=model_builder._backbone_model(),
    )

    # export onnx
    pl_module = pl_module.cuda()
    date = cfg.inference.best_ckpt.split("_")[1]  # e.g. 240831
    pl_module.to_onnx(
        file_path=f"./export/{cfg.model.model_name}_model_{date}.onnx",
        input_sample=(inp_data["upper_air"], inp_data["surface"]),
        export_params=True,
        verbose=False,
        input_names=["input_upper", "input_surface"],
        output_names=["output_upper", "output_surface"],
        dynamic_axes={
            "input_upper": {0: "batch_size"},
            "input_surface": {0: "batch_size"},
            "output_upper": {0: "batch_size"},
            "output_surface": {0: "batch_size"},
        },
    )


def save_single_onnx():
    file_path = "./export/Pangu_model_250215.onnx"
    model = onnx.load(file_path)
    onnx.save_model(
        model,
        "./export/Pangu_model_250215_168.onnx",
        save_as_external_data=True,
        all_tensors_to_one_file=True,
        location="Pangu_model_250215_168_external_data",  # same dir "./export/"
        size_threshold=10240,
        convert_attribute=False,
    )


if __name__ == "__main__":
    main()
```

## File: src/dlamp/generate_const_masks.py
```python
from datetime import UTC, datetime

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import xarray as xr
import yaml
from scipy.interpolate import RegularGridInterpolator
from tqdm import trange

from dlamp.runtime_config import get_runtime_config
from dlamp.utils import DataCompose, DataGenerator, gen_path


def gen_TW_only_terrain():
    # load config
    config = get_runtime_config()
    with open(config.data_config_path, "r") as stream:
        data_config = yaml.safe_load(stream)
        data_shape = data_config["data_shape"]
        img_shape = data_config["image_shape"]

    data_gnrt = DataGenerator(data_shape, img_shape)
    # Note that the lat/lon generated by DataGenerator is not consist with the
    # image_lat/lon in config.yaml
    dc_lat, dc_lon = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})
    start_t = datetime.strptime(data_config["start_time"], data_config["format"]).replace(tzinfo=UTC)
    target_lat = data_gnrt.yield_data(start_t, dc_lat)
    target_lon = data_gnrt.yield_data(start_t, dc_lon)

    # Taiwan-only terrain data
    # OBJECTID_1	OBJECTID	townname	countyname	BASIN_NAME	N_1	E_1	高程	坡度	坡向	Shape_Leng	ORIG_FID	geometry
    # 0	1	1	None	None	None	25.3000	120.0	0.0	0.0	0.0	0.05	0	POINT (120.00000 25.30000)
    # 1	2	2	None	None	None	25.2875	120.0	0.0	0.0	0.0	0.05	1	POINT (120.00000 25.28750)
    # 2	3	3	None	None	None	25.2750	120.0	0.0	0.0	0.0	0.05	2	POINT (120.00000 25.27500)
    # 3	4	4	None	None	None	25.2625	120.0	0.0	0.0	0.0	0.05	3	POINT (120.00000 25.26250)
    # 4	5	5	None	None	None	25.2500	120.0	0.0	0.0	0.0	0.05	4	POINT (120.00000 25.25000)
    filename = "./assets/terrain_shp/GIS_terrain.shp"
    terrain_data: gpd.GeoDataFrame = gpd.read_file(filename)
    terrain_lat: np.ndarray = np.sort(terrain_data["N_1"].unique())  # (273,)
    terrain_lon: np.ndarray = np.sort(terrain_data["E_1"].unique())  # (161,)
    assert len(terrain_lat) * len(terrain_lon) == len(terrain_data)
    # mapping
    terrain_mask = np.zeros_like(target_lat, dtype=np.float32)
    for i in trange(target_lat.shape[0]):
        for j in range(target_lat.shape[1]):
            lat = target_lat[i, j]
            lon = target_lon[i, j]

            if lat < terrain_lat[0] or lat > terrain_lat[-1] or lon < terrain_lon[0] or lon > terrain_lon[-1]:
                continue

            closest_lat = find_closest_value(terrain_lat, lat)
            closest_lon = find_closest_value(terrain_lon, lon)
            combined_filter = terrain_data[(terrain_data["E_1"] == closest_lon) & (terrain_data["N_1"] == closest_lat)]
            terrain_mask[i, j] = combined_filter["高程"].values

    # save npy
    np.save(config.standardization_path.parent / "constant_masks" / "topography_mask_4km.npy", terrain_mask)
    np.save(
        config.standardization_path.parent / "constant_masks" / "land_sea_mask_4km.npy",
        np.where(terrain_mask > 0.5, 1, 0),
    )
    print("done")


def gen_TW_CN_terrain():
    """
    Prepare land_sea mask and terrain mask for training. The coordinates are the
    same as those recorded in config.yaml.
    """

    # load config
    config = get_runtime_config()
    with open(config.data_config_path, "r") as stream:
        data_config = yaml.safe_load(stream)
        data_shape = data_config["data_shape"]
        img_shape = data_config["image_shape"]

    data_gnrt = DataGenerator(data_shape, img_shape)
    # Note that the lat/lon generated by DataGenerator is not consist with the
    # image_lat/lon in config.yaml
    dc_lat, dc_lon = DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})
    start_t = datetime.strptime(data_config["start_time"], data_config["format"]).replace(tzinfo=UTC)
    target_lat = data_gnrt.yield_data(start_t, dc_lat)
    target_lon = data_gnrt.yield_data(start_t, dc_lon)

    # East Asia terrain data
    filename = "./assets/terrain_shp/gt30e100n40.tif"
    with rasterio.open(filename) as src:
        # Read the data
        terrain_data = src.read(1)
        # Display basic information
        print(f"Width: {src.width}, Height: {src.height}")
        print(f"Coordinate Reference System: {src.crs}")
        print(f"Bounds: {src.bounds}")
        # Gen Interpolator
        geo_lat = np.linspace(40, -10, src.height)
        geo_lon = np.linspace(100, 140, src.width)
        interp = RegularGridInterpolator((geo_lat, geo_lon), terrain_data)

    # Flatten the meshgrid for interpolation
    points = np.column_stack((target_lat.ravel(), target_lon.ravel()))
    print("Interpolating...")
    terrain_mask = interp(points)
    terrain_mask = terrain_mask.reshape(target_lon.shape)
    terrain_mask = np.where(terrain_mask < 0, 0, terrain_mask)

    # save npy
    np.save(config.standardization_path.parent / "constant_masks" / "topography_mask_4km.npy", terrain_mask)
    np.save(
        config.standardization_path.parent / "constant_masks" / "land_sea_mask_4km.npy",
        np.where(terrain_mask > 0.5, 1, 0),
    )
    print("done")


def extract_landmask_from_ncfile():
    config = get_runtime_config()
    with open(config.data_config_path, "r") as stream:
        data_config = yaml.safe_load(stream)
        data_shape = data_config["data_shape"]
        img_shape = data_config["image_shape"]

    start_t = datetime.strptime(data_config["start_time"], data_config["format"]).replace(tzinfo=UTC)
    filename = gen_path(start_t)
    dataset = xr.open_dataset(str(filename))
    terrain = dataset["HGT"].values.squeeze()
    landsea = dataset["LANDMASK"].values.squeeze()
    assert tuple(data_shape) == terrain.shape == landsea.shape

    terrain = terrain[1:-1, 1:-1]  # (448, 448)
    landsea = landsea[1:-1, 1:-1]  # (448, 448)
    terrain_mask = terrain[::2, ::2]  # (224, 224)
    landsea_mask = landsea[::2, ::2]  # (224, 224)
    assert tuple(img_shape) == terrain_mask.shape == landsea_mask.shape

    # save npy
    np.save(config.standardization_path.parent / "constant_masks" / "topography_mask_4km.npy", terrain_mask)
    np.save(config.standardization_path.parent / "constant_masks" / "land_sea_mask_4km.npy", landsea_mask)
    print("done")


def find_closest_value(input_array: np.ndarray, target: float) -> float:
    assert len(input_array.shape) == 1, "Input array must be 1D"
    new_array = input_array - target
    min_index = np.argmin(np.abs(new_array))  # Only the first occurrence is returned.
    return input_array[min_index]


def plot(terrain_mask, lat, lon):
    c = plt.pcolor(lon, lat, terrain_mask)
    ax = c.axes
    ax.axis("equal")
    plt.colorbar()


def main() -> None:
    """Generate the land-sea and topography constant masks.

    This is the ``dlamp-gen-const-masks`` console-script entry point.
    It delegates to :func:`extract_landmask_from_ncfile`, which derives
    the masks from the ERA5 source file referenced by the runtime config.
    """
    extract_landmask_from_ncfile()


if __name__ == "__main__":
    main()
```

## File: src/dlamp/inference_onnx.py
```python
import time
from datetime import UTC, datetime

import hydra
import onnxruntime as ort
import psutil
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.managers import DataManager
from dlamp.standardizer import get_standardizer
from dlamp.utils import DataCompose

"""
This is a sample code for quickly inference onnx model.
"""


@hydra.main(version_base=None, config_path=str(REPO_ROOT / "config"), config_name="predict")
def main(cfg: DictConfig) -> None:
    OmegaConf.set_struct(cfg, True)

    # prepare data
    eval_cases = [datetime(2022, 9, 11, tzinfo=UTC)]
    data_list = DataCompose.from_config(cfg.data.train_data)
    data_manager = DataManager(data_list, eval_cases, **cfg.data, **cfg.lightning)
    data_manager.setup("predict")

    # sample data
    data_loader = data_manager.predict_dataloader()
    inp_data, _oup_data = next(iter(data_loader))

    # onnxruntime settings
    assert "CUDAExecutionProvider" in ort.get_available_providers()
    print(f"ort device: {ort.get_device()}")

    # An issue about onnxruntime for cuda12.x
    # ref: https://github.com/microsoft/onnxruntime/issues/8313#issuecomment-1486097717
    _default_session_options = ort.capi._pybind_state.get_default_session_options()

    def get_default_session_options_new():
        _default_session_options.inter_op_num_threads = 1
        _default_session_options.intra_op_num_threads = 1
        return _default_session_options

    ort.capi._pybind_state.get_default_session_options = get_default_session_options_new

    # inference
    onnx_filename = cfg.inference.onnx_path
    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = psutil.cpu_count(logical=True)  # faster
    ort_session = ort.InferenceSession(
        onnx_filename,
        sess_options,
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
    )
    ort_inputs = {
        ort_session.get_inputs()[0].name: inp_data["upper_air"].cpu().numpy(),
        ort_session.get_inputs()[1].name: inp_data["surface"].cpu().numpy(),
    }
    start = time.time()
    pred_upper, pred_surface = ort_session.run(None, ort_inputs)

    standardizer = get_standardizer()
    pred_upper = standardizer.destandardize(pred_upper)
    pred_surface = standardizer.destandardize(pred_surface)
    print(type(pred_upper), pred_upper.shape, pred_surface.shape)
    print(f"execution time: {time.time() - start:.5f} sec")


if __name__ == "__main__":
    main()
```

## File: src/dlamp/standardizer.py
```python
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import yaml
from tqdm import tqdm

from .const import BLACKLIST_PATH
from .runtime_config import RuntimeConfig
from .utils import DataCompose, DataGenerator, DataType, gen_path

logger = logging.getLogger(__name__)

MEAN_THRESHOLD = 1e-4


class Standardizer:
    """Standardizes and destandardizes weather data.

    Loads statistics once at construction time from the
    ``standardization_path`` and ``data_config_path`` provided by
    ``RuntimeConfig``. Eliminates the per-call YAML re-reads and the
    import-time module-level state of the old ``standardization`` module.

    Both ``standardize`` and ``destandardize`` share the same stats
    dictionary and data ordering, so they can never disagree.
    """

    def __init__(self, config: RuntimeConfig):
        self._config = config
        self._stat_dict = self._load_stats(config.standardization_path)
        self._data_list = DataCompose.from_config(config.data_config_path)

    def _load_stats(self, path: Path) -> dict:
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def standardize(self, dc_name: str, array: np.ndarray) -> np.ndarray:
        """Standardize a single variable array.

        An absent ``dc_name`` is an :term:`Unstandardized Variable` and is
        legal: the array is passed through unchanged (identity), never zeroed.
        A variable whose stats are absent by accident is caught by schema
        checks elsewhere, not by zeroing here.
        """
        if dc_name in self._stat_dict:
            stat = self._stat_dict[dc_name]
            if abs(stat["mean"]) < MEAN_THRESHOLD:
                return array
            elif "Qt@Hpa" in dc_name:
                return np.log(array * 1e5 + 1)
            else:
                return (array - stat["mean"]) / stat["std"]
        else:
            return array

    def destandardize(self, array: np.ndarray) -> np.ndarray:
        """Destandardize a full stacked array.

        The array shape is either (lv, H, W, C) or (B, lv, H, W, C).
        Variable ordering is determined by the data_list loaded from the
        data config at construction time, so no per-call YAML re-reads
        are needed.
        """
        num_array_dim = len(array.shape)
        if num_array_dim not in [4, 5]:
            raise ValueError(f"Expected 4D or 5D array, got {num_array_dim}D")

        is_surface = array.shape[1 if num_array_dim == 5 else 0] == 1
        return self._destandardize(array, is_surface)

    def _destandardize(self, array: np.ndarray, is_sfc: bool) -> np.ndarray:
        """Handle destandardization for surface or upper-level variables."""
        new_array = np.zeros_like(array)

        if is_sfc:
            filtered_dc = [dc for dc in self._data_list if dc.level.is_surface()]
            variables = DataCompose.get_all_vars(self._data_list, only_surface=True)
        else:
            filtered_dc = [dc for dc in self._data_list if not dc.level.is_surface()]
            levels = DataCompose.get_all_levels(self._data_list, only_upper=True)
            variables = DataCompose.get_all_vars(self._data_list, only_upper=True)

        for dc in filtered_dc:
            if str(dc) not in self._stat_dict:
                continue

            stat = self._stat_dict[str(dc)]
            lv_idx = 0 if is_sfc else levels.index(dc.level)
            var_idx = variables.index(dc.var_name)

            if len(array.shape) == 5:
                new_array[:, lv_idx, :, :, var_idx] = self._destandardize_array(
                    array[:, lv_idx, :, :, var_idx], stat, dc
                )
            else:
                new_array[lv_idx, :, :, var_idx] = self._destandardize_array(array[lv_idx, :, :, var_idx], stat, dc)

        return new_array

    def _destandardize_array(self, array: np.ndarray, stat: dict[str, float], dc: DataCompose) -> np.ndarray:
        """Apply destandardization to a single array using statistics from stat_dict."""
        if abs(stat["mean"]) < MEAN_THRESHOLD:
            return array
        elif "Qt@Hpa" in str(dc):
            return (np.exp(array) - 1) / 1e5
        else:
            return array * stat["std"] + stat["mean"]

    def calc_standardization(
        self,
        start_time: datetime = datetime(2021, 1, 1, tzinfo=UTC),
        end_time: datetime = datetime(2022, 12, 31, tzinfo=UTC),
        sample_size: int = 100,
        num_criteria: int = 1000,
    ) -> None:
        """Calculate the mean and standard deviation from a dataset within a specified time range."""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        with open(self._config.data_config_path, "r") as stream:
            data_config = yaml.safe_load(stream)

        with open(BLACKLIST_PATH, "r") as f:
            blacklist = [
                datetime.strptime(line.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
                for line in f
                if line.strip()
            ]

        data_list = DataCompose.from_config(data_config["train_data"])
        data_gnrt = DataGenerator(data_config["data_shape"], data_config["image_shape"])
        use_Kth_hour_pred = data_config.get("use_Kth_hour_pred", None)

        def _progress_one_step(dt, month_cnt):
            dt += timedelta(hours=8)
            if (dt - start_time) / timedelta(days=30) > month_cnt:
                month_cnt += 1
                logger.info(f"now is processing {dt}")
            return dt, month_cnt

        for data_compose in tqdm(data_list):
            dt = start_time
            month_cnt = 0
            container = []
            logger.info(f"start executing {data_compose}")

            if str(data_compose) in self._stat_dict:
                logger.info(f"skip {data_compose} because it already exists in {self._config.standardization_path}")
                continue

            while dt < end_time:
                if gen_path(dt, data_compose, use_Kth_hour_pred).exists() and dt not in blacklist:
                    data: np.ndarray = data_gnrt.yield_data(dt, data_compose, use_Kth_hour_pred=use_Kth_hour_pred)

                    indices = np.arange(data.size)
                    chosen_indices = np.random.choice(indices, sample_size, replace=False)
                    rows, cols = np.unravel_index(chosen_indices, data.shape)
                    random_values = data[rows, cols]

                    if data_compose.var_name == DataType.SWDOWN and np.mean(random_values) == 0:
                        dt, month_cnt = _progress_one_step(dt, month_cnt)
                        continue

                    container.append(random_values)

                dt, month_cnt = _progress_one_step(dt, month_cnt)

            all_data = np.stack(container).flatten()
            lower_bound = np.percentile(all_data, 10)
            upper_bound = np.percentile(all_data, 90)
            filtered_data = all_data[(all_data > lower_bound) & (all_data < upper_bound)]

            if len(filtered_data) < num_criteria:
                logger.info(f"skip {data_compose} because data sample {len(filtered_data)} is not enough")
                continue

            self._stat_dict[str(data_compose)] = {
                "mean": float(np.mean(filtered_data)),
                "std": float(np.std(filtered_data)),
            }

            with open(self._config.standardization_path, "w") as f:
                json.dump(self._stat_dict, f, indent=4)


def get_standardizer(config: RuntimeConfig | None = None) -> Standardizer:
    """Return (or construct) the singleton Standardizer for the current
    process. If ``config`` is provided, a new Standardizer is built and
    cached. If ``config`` is None, the cached instance is returned, or
    one is built from ``get_runtime_config()``.

    .. note:: If multiple entrypoints are run in the same process
              (e.g. tests), the last call with a config wins.
    """
    if not hasattr(get_standardizer, "_singleton"):
        if config is None:
            from .runtime_config import get_runtime_config

            config = get_runtime_config()
        get_standardizer._singleton = Standardizer(config)
    return get_standardizer._singleton
```

## File: src/dlamp/unzip_tgz.py
```python
import logging
import tarfile
from pathlib import Path

from dlamp.runtime_config import get_runtime_config

logging.basicConfig(
    filename=Path(__file__).parent.resolve() / "unzip.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def main():
    logger = logging.getLogger("dev")
    logger.info("start to unzip")

    config = get_runtime_config()
    file_dir = config.data_path
    tar_gz_files = sorted(file_dir.glob("*.tar.gz"))

    for tar_gz_file in tar_gz_files:
        # new dir
        new_dir_name = tar_gz_file.name.split(".")[0]
        new_dir = Path(tar_gz_file.parent / new_dir_name)
        new_dir.mkdir(parents=True, exist_ok=True)

        # extraction
        tar_gz_file = str(tar_gz_file)
        new_dir = str(new_dir)
        try:
            if tar_gz_file.endswith("tar.gz"):
                with tarfile.open(tar_gz_file, "r:gz") as tar:
                    tar.extractall(new_dir)
            elif tar_gz_file.endswith("tar"):
                with tarfile.open(tar_gz_file, "r:") as tar:
                    tar.extractall(new_dir)
        except Exception as e:  # noqa: BLE001 - broad error boundary on archive extraction
            logger.error(e)

        # done
        logger.info(f"{tar_gz_file} has been extracted to {new_dir}")


def move_files():
    config = get_runtime_config()
    file_dir = config.data_path
    target_subdir = ["rwf_202005-06", "rwf_202105-06"]

    for subdir in target_subdir:
        subdir = file_dir / subdir

        for file in subdir.iterdir():
            new_dir = file_dir / f"rwf_{file.name[:6]}"
            if not new_dir.exists():
                new_dir.mkdir(parents=True, exist_ok=True)

            # move file to new dir
            file.rename(new_dir / file.name)

        print(f"{subdir} has been moved to {new_dir}")


if __name__ == "__main__":
    main()
```

## File: config/data/rwrf_202501.yaml
```yaml
start_time: "2020-05-01 00:00"
end_time: "2024-10-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
add_time_features: True
use_Kth_hour_pred: 3
train_data:
  Z:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  T:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter2
  U:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter10
  V:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter10
  W:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qv:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter2
  Qr:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qs:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qg:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qc:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qi:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  RH:
    - Meter2
  Td:
    - Meter2
  SLP:
    - SeaSurface
  SST:
    - SeaSurface
  PSFC:
    - Surface
  PW:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/data/rwrf_20250310.yaml
```yaml
start_time: "2010-09-18 18:00"
end_time: "2010-09-20 00:00"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
grid_spacing:
  ground_truth_m: 2000.0
  forecast_m: 4000.0
add_time_features: True
use_Kth_hour_pred: 0
train_data:
  Z:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  T:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter2
  U:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter10
  V:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter10
  W:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  Qv:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter2
  Qw:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  SST:
    - SeaSurface
  SLP:
    - SeaSurface
  PSFC:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/data/rwrf_20250611.yaml
```yaml
start_time: "2010-09-18 18:00"   #"2020-05-01 00:00"
end_time: "2010-09-20 00:00"     #"2024-10-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
grid_spacing:
  ground_truth_m: 2000.0
  forecast_m: 4000.0
add_time_features: True
use_Kth_hour_pred: 0
train_data:
  Z:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  T:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  U:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  V:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter10
  W:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
  Qv:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    - Meter2
  Qw:
    - Hpa50
    - Hpa100
    - Hpa150
    - Hpa200
    - Hpa250
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa850
    - Hpa925
    - Hpa1000
    # - Meter2
  SST:
    - SeaSurface
  PSFC:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/lightning/pangu_rwrf_202501.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 1
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 1e-4
    weight_decay: 1e-5
lr_schedule:
  name: linear_decay
  args:
    warmup_epochs: 10
    last_epoch: -1
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: null
max_steps: null
min_steps: 5e4 # 50k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
```

## File: config/lightning/pangu_rwrf_202502.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [3, 1, 0]
  split_method: "half_month"
sampling_rate: 2
batch_size: 3
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 2e-4
    weight_decay: 3e-6
lr_schedule:
  name: cosine
  args:
    warmup_steps: 1000
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: null
max_steps: null
min_steps: 5e5 # 500k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
save_last: True
```

## File: config/model/diffusion_rwrf_202409.yaml
```yaml
model_name: Glide
hidden_dim: 128
ch_mults: [1, 2, 2, 4]
is_attn: [False, False, False, True]
n_blocks: 2
# diffusion
diffusion_type: DDIM
timesteps: 500
beta_start: 1e-4
beta_end: 4e-2
```

## File: config/model/pangu_rwrf_202409.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 5
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 6]
# earth block
max_drop_path_ratio: 0.2
# earth attn 3d
heads: [6, 12]
embed_dim: 192
dropout_rate: 0
window_size: [3, 4, 4]
```

## File: config/model/pangu_rwrf_202412.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 7
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 6]
# earth block
max_drop_path_ratio: 0.2
# earth attn 3d
heads: [8, 16]
embed_dim: 256
dropout_rate: 0
window_size: [4, 4, 4]
```

## File: config/model/pangu_rwrf_202501.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 3
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 6]
# earth block
max_drop_path_ratio: 0.2
# earth attn 3d
heads: [8, 16]
embed_dim: 512
dropout_rate: 0
window_size: [4, 7, 7]
```

## File: config/model/pangu_rwrf_202502.yaml
```yaml
model_name: Pangu
# patch embedding
patch_size: [1, 2, 2]
smoothing_kernel_size: 5
segmented_smooth_boundary_width: null
# earth layer
depths: [2, 2, 6]
# earth block
max_drop_path_ratio: 0.3
# earth attn 3d
heads: [8, 8, 16]
embed_dim: 256
dropout_rate: 0
window_size: [3, 7, 7]
```

## File: src/dlamp/analysis/plotter.py
```python
# analysis/plotter.py
"""Generates and saves detailed 12-panel weather analysis plots.

This module provides the WeatherPlotter for creating visualizations that
compare the model's forecast against ground truth data across multiple
variables and atmospheric levels in a single figure, using cartopy for
correct geospatial projection.
"""

import logging
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.axes import Axes
from matplotlib.colors import CenteredNorm, LogNorm, PowerNorm, TwoSlopeNorm
from matplotlib.figure import Figure
from omegaconf import DictConfig
from pyproj import Geod
from scipy.interpolate import griddata

from dlamp.analysis.data_manager import AnalysisDataManager
from dlamp.analysis.plot_meta import ANALYSIS_PLOT_CONFIGS
from dlamp.runtime_config import get_runtime_config
from dlamp.utils.data_type import DataType, Level

logger = logging.getLogger(__name__)

R_D = 287.0  # gas constant of dry air (J kg-1 K-1)
C_P = 1004.0  # specific heat of dry air at constant pressure (J kg-1 K-1)

_GEOD = Geod(ellps="WGS84")


def _great_circle_distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Return the great-circle distance between two lat/lon points in km.

    Args:
        point_a (Tuple[float, float]): (latitude, longitude) of the first point.
        point_b (Tuple[float, float]): (latitude, longitude) of the second point.

    Returns:
        float: The great-circle distance in kilometers.
    """
    _fwd_az, _back_az, dist_m = _GEOD.inv(point_a[1], point_a[0], point_b[1], point_b[0])
    return dist_m / 1000.0


class WeatherPlotter:
    """Creates and saves 12-panel forecast vs. ground truth plots.

    This class orchestrates the creation of a complex meteorological figure
    that visualizes multiple variables side-by-side for forecast and ground
    truth, aiding in qualitative model performance assessment.

    Attributes:
        manager (AnalysisDataManager): The data manager for data retrieval.
        output_dir (Path): Directory where plot images will be saved.
        map_projection: The cartopy projection used for all subplots.
    """

    def __init__(
        self,
        cfg: DictConfig,
        manager: AnalysisDataManager,
        output_dir: Path,
        exp_code: str = "analysis",
    ):
        """Initializes the WeatherPlotter.

        Args:
            cfg (DictConfig): The Hydra configuration object.
            manager (AnalysisDataManager): An initialized data manager.
            output_dir (Path): Target directory for saving plot images.
            exp_code (str): An experiment code to use as a prefix for filenames.
        """
        self.cfg: DictConfig = cfg
        self.manager: AnalysisDataManager = manager
        self.output_dir: Path = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.map_projection = ccrs.PlateCarree()
        self.exp_code: str = exp_code

        self._plot_dispatch_table: dict[str, Callable[..., Any]] = {
            "wind_speed": self._plot_wind_speed,
            "vorticity": self._plot_vorticity,
            "temperature": self._plot_temperature,
            "column_max_qt": self._plot_column_max_qt,
            "hydrometeors_mixing_ratio": self._plot_mixing_ratio,
            "theta_e": self._plot_theta_e,
        }

    def create_analysis_figure(self, forecast_step: int) -> Path:
        """Creates and saves a single 12-panel analysis figure.

        Args:
            forecast_step (int): The 0-indexed forecast step to visualize.

        Returns:
            Path: The path to the saved PNG image file.
        """
        fig: Figure = plt.figure(figsize=(12, 5))
        gs = gridspec.GridSpec(2, 6, figure=fig, hspace=0.1, wspace=0.1)
        forecast_time: datetime = self.manager.get_forecast_time(forecast_step)
        start_time: str = self.manager.start_time.strftime("%Y-%m-%d_%H%M")
        valid_time: str = forecast_time.strftime("%Y-%m-%d_%H%M")

        step_str: str = "F000H" if forecast_step == -1 else f"F{forecast_step + 1:03d}H"
        config = get_runtime_config()
        fig.suptitle(
            f"DLAMP.tw | {config.model_code} | Valid: {valid_time}Z | Initial: {start_time}Z {step_str}",
            fontsize=8,
            y=0.95,
        )

        for idx, config in enumerate(ANALYSIS_PLOT_CONFIGS):
            ax_fc: Axes = fig.add_subplot(gs[0, idx])
            ax_gt: Axes = fig.add_subplot(gs[1, idx])

            plot_func_key: str = config["plot_func_key"]

            try:
                plot_func: Callable[..., Any] = self._plot_dispatch_table[plot_func_key]
                plot_func(ax_fc, ax_gt, forecast_step, config)
            except KeyError:
                logger.error("Plot function key '%s' not found in dispatch table.", plot_func_key)
                continue

        start_time_str: str = self.manager.start_time.strftime("%Y%m%d_%H%M")
        step_str_for_filename: str
        if forecast_step == -1:
            step_str_for_filename = "F000H"
        else:
            step_str_for_filename = f"F{forecast_step + 1:03d}H"

        filename: str = f"{self.exp_code}_{start_time_str}_{step_str_for_filename}.png"
        output_path: Path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved analysis plot to {output_path}")
        return output_path

    def _plot_wind_speed(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots wind speed and geopotential height."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)
        wspd_fc: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=False)
        u_fc, v_fc = self.manager._get_wind_components(step, level)

        time: datetime = self.manager.get_forecast_time(step)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)
        wspd_gt: np.ndarray = self.manager.get_wind_speed(step, level, is_gt=True)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            wspd_fc,
            z_fc,
            (u_fc, v_fc),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            wspd_gt,
            z_gt,
            (u_gt, v_gt),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    def _plot_vorticity(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots relative vorticity and geopotential height."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        u_fc, v_fc = self.manager._get_wind_components(step, level)
        vort_fc: np.ndarray = self.manager.get_relative_vorticity(step, level, False) * 1e6
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)

        time: datetime = self.manager.get_forecast_time(step)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)
        vort_gt: np.ndarray = self.manager.get_relative_vorticity(step, level, True) * 1e6
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            np.clip(vort_fc, vmin, vmax),
            z_fc,
            (u_fc, v_fc),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            np.clip(vort_gt, vmin, vmax),
            z_gt,
            (u_gt, v_gt),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    # --- 新增：繪製 Theta-e 的方法 ---
    def _plot_theta_e(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots equivalent potential temperature (Theta-e) with geopotential
        height contours and 10-m wind streams, mirroring the temperature panel.
        """
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        # Forecast fields
        thetae_fc: np.ndarray = self.manager.get_equivalent_potential_temperature(step, level, is_gt=False)
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)
        u_fc, v_fc = self.manager._get_wind_components(step, level)

        # Ground-truth fields
        time: datetime = self.manager.get_forecast_time(step)
        thetae_gt: np.ndarray = self.manager.get_equivalent_potential_temperature(step, level, is_gt=True)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)
        u_gt, v_gt = self.manager._get_gt_wind_components(time, level)

        # Plot: FC (theta-e shading + Z contours + streamlines)
        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            thetae_fc,
            z_fc,
            (u_fc, v_fc),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

        # Plot: GT (theta-e shading + Z contours + streamlines)
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            thetae_gt,
            z_gt,
            (u_gt, v_gt),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    def _plot_temperature(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots temperature and 10-meter wind."""
        title: str = config["title"]
        level: Level = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        t_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.TK, level)
        z_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Z, level)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        t_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.TK, level)
        z_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Z, level)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            t_fc,
            z_fc,
            (u10_fc, v10_fc),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            t_gt,
            z_gt,
            (u10_gt, v10_gt),
            "stream",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    def _plot_mixing_ratio(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots 925hPa Qt and 10-meter wind."""
        title: str = config["title"]
        level: Level | None = config["level"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        qt_fc: np.ndarray = self.manager.get_forecast_data(step, DataType.Qt, level)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        time: datetime = self.manager.get_forecast_time(step)
        qt_gt: np.ndarray = self.manager.get_ground_truth_data(time, DataType.Qt, level)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            qt_fc,
            None,
            (u10_fc, v10_fc),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            qt_gt,
            None,
            (u10_gt, v10_gt),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    def _plot_column_max_qt(self, ax_fc: Axes, ax_gt: Axes, step: int, config: dict[str, Any]):
        """Plots column-maximum Qt and 10-meter wind."""
        title: str = config["title"]
        unit: str = config["unit"]
        cmap: str = config["cmap"]
        vmin: float = config["vmin"]
        vmax: float = config["vmax"]
        colorbar_scale: str | None = config.get("colorbar_scale")
        colorbar_gamma: float | None = config.get("colorbar_gamma")
        colorbar_center: float | None = config.get("colorbar_center")

        qt_fc: np.ndarray = self.manager.get_column_max_qt(step, False)
        u10_fc, v10_fc = self.manager._get_wind_components(step, Level.Meter10)

        qt_gt: np.ndarray = self.manager.get_column_max_qt(step, True)
        time: datetime = self.manager.get_forecast_time(step)
        u10_gt, v10_gt = self.manager._get_gt_wind_components(time, Level.Meter10)

        self._generic_grid_plot(
            ax_fc,
            f"FC: {title}",
            qt_fc,
            None,
            (u10_fc, v10_fc),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )
        self._generic_grid_plot(
            ax_gt,
            f"GT: {title}",
            qt_gt,
            None,
            (u10_gt, v10_gt),
            "barbs",
            cmap,
            vmin,
            vmax,
            unit,
            colorbar_scale,
            colorbar_gamma,
            colorbar_center=colorbar_center,
        )

    def _generic_grid_plot(
        self,
        ax: Axes,
        title: str,
        color_data: np.ndarray,
        contour_data: np.ndarray | None,
        wind_data: tuple[np.ndarray, np.ndarray] | None,
        wind_type: str,
        cmap: str,
        vmin: float,
        vmax: float,
        unit: str,
        colorbar_scale: str | None = None,
        colorbar_gamma: float | None = None,
        colorbar_center: float | None = None,
    ):
        """Plots data on a model grid with transformed coastlines.

        Args:
            ax: The matplotlib Axes object to plot on.
            title: The title for the subplot.
            color_data: 2D data for the pcolormesh.
            contour_data: 2D data for contours.
            wind_data: (u, v) winds.
            wind_type: 'stream' for streamplot or 'barbs' for barbs.
            cmap: The colormap for the color_data.
            vmin: The minimum value for the color scale.
            vmax: The maximum value for the color scale.
            unit: The unit label for the colorbar.
            colorbar_scale: Scale for the colorbar.
            colorbar_gamma: Gamma value for the power scale.
            colorbar_center: Center value for CenteredNorm or TwoSlopeNorm.
        """
        model_lon: np.ndarray = self.manager.results["lon"]
        model_lat: np.ndarray = self.manager.results["lat"]
        model_map: np.ndarray = self.manager.results["mask"]
        ny, nx = color_data.shape
        x_indices: np.ndarray = np.arange(nx)
        y_indices: np.ndarray = np.arange(ny)
        xgrid, ygrid = np.meshgrid(x_indices, y_indices)

        ax.set_title(title, fontsize=6)

        norm = None
        if colorbar_scale == "log":
            safe_vmin = vmin if vmin > 0 else 1e-6  # Avoid vmin <= 0 for LogNorm
            norm = LogNorm(vmin=safe_vmin, vmax=vmax)
            if vmin <= 0:
                logger.warning(
                    f"LogNorm received vmin <= 0 ({vmin}). Adjusting vmin to {safe_vmin} for plotting '{title}'."
                )
        elif colorbar_scale == "power" and colorbar_gamma is not None:
            norm = PowerNorm(gamma=colorbar_gamma, vmin=vmin, vmax=vmax)
        elif colorbar_scale == "centered" and colorbar_center is not None:
            halfrange = max(abs(vmax - colorbar_center), abs(vmin - colorbar_center))
            norm = CenteredNorm(vcenter=colorbar_center, halfrange=halfrange)
        elif colorbar_scale == "two_slope" and colorbar_center is not None:
            norm = TwoSlopeNorm(vcenter=colorbar_center, vmin=vmin, vmax=vmax)
        else:
            norm = mpl.colors.Normalize(
                vmin=vmin,
                vmax=vmax,
            )

        pcm = ax.pcolormesh(
            xgrid,
            ygrid,
            color_data,
            cmap=cmap,
            shading="auto",
            norm=norm,
        )
        cbar = plt.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.06, shrink=0.95)
        cbar.set_label(unit, size=4)
        cbar.ax.tick_params(labelsize=4, size=4, tickdir="in")

        if contour_data is not None:
            ax.contour(xgrid, ygrid, contour_data, colors="k", linewidths=0.4)

        if wind_data:
            u, v = wind_data
            skip = 11
            if wind_type == "barbs":
                ax.barbs(
                    xgrid[::skip, ::skip],
                    ygrid[::skip, ::skip],
                    u[::skip, ::skip] / 0.5144,
                    v[::skip, ::skip] / 0.5144,
                    color="gray",
                    length=3.5,
                    linewidth=0.35,
                )
            elif wind_type == "stream":
                ax.streamplot(
                    xgrid,
                    ygrid,
                    u,
                    v,
                    color="navy",
                    linewidth=0.35,
                    density=1.0,
                    arrowstyle="->",
                )

        ax.contour(xgrid, ygrid, model_map, [0.5, 1.5], colors="black", linewidths=0.5, linestyles="-")
        ax.contour(xgrid, ygrid, model_lon, np.linspace(-180, 180, 73), colors="gray", linewidths=0.35, linestyles=":")
        ax.contour(xgrid, ygrid, model_lat, np.linspace(-90, 90, 37), colors="gray", linewidths=0.35, linestyles=":")

        ax.set_xlim(xgrid.min(), xgrid.max())
        ax.set_ylim(ygrid.min(), ygrid.max())
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])

    def create_cross_section_figure(
        self,
        start_point: tuple[float, float],
        end_point: tuple[float, float],
        forecast_step: int,
        is_gt: bool = False,
        band_width_km: float = 0.0,
        num_points: int = 100,
    ) -> Path:
        """
        繪製指定兩點連線的垂直剖面圖。
        填色圖(contourf)為 Qv (水氣混和比)，等高線(contour)為位溫。

        Args:
            start_point (Tuple[float, float]): 起始點 (緯度, 經度)。
            end_point (Tuple[float, float]): 結束點 (緯度, 經度)。
            forecast_step (int): 預報步長 (0-indexed)。
            is_gt (bool): 是否使用 ground truth 資料。
            band_width_km (float): 剖面帶寬(km)。若為 0，則為"一刀切"剖面。
                                   若大於 0，則在剖面線法線方向上取此寬度的平均值。
            num_points (int): 剖面線上取樣點的數量。

        Returns:
            Path: 儲存的圖片路徑。
        """
        logger.info(f"Generating cross section from {start_point} to {end_point}...")

        # 1. 準備網格和資料
        model_lon: np.ndarray = self.manager.results["lon"]
        model_lat: np.ndarray = self.manager.results["lat"]
        points = np.vstack((model_lon.ravel(), model_lat.ravel())).T

        levels_enum = self.manager.levels
        pressure_levels = np.array([float(l.value.replace("hPa", "")) for l in levels_enum])

        # 獲取所有垂直層的 3D 資料
        all_level_qv = []
        all_level_t = []
        time = self.manager.get_forecast_time(forecast_step)

        for level in levels_enum:
            if is_gt:
                qv = self.manager.get_ground_truth_data(time, DataType.Qt, level)
                t = self.manager.get_ground_truth_data(time, DataType.TK, level)
            else:
                qv = self.manager.get_forecast_data(forecast_step, DataType.Qt, level)
                t = self.manager.get_forecast_data(forecast_step, DataType.TK, level)
            all_level_qv.append(qv)
            all_level_t.append(t)

        qv_3d = np.stack(all_level_qv)
        t_3d = np.stack(all_level_t)

        # 2. 定義剖面路徑
        lats = np.linspace(start_point[0], end_point[0], num_points)
        lons = np.linspace(start_point[1], end_point[1], num_points)
        path_points = list(zip(lats, lons))

        distances = [0.0]
        for i in range(1, len(path_points)):
            dist = _great_circle_distance(path_points[i - 1], path_points[i])
            distances.append(distances[-1] + dist)

        # 3. 內插資料到剖面路徑上
        cross_section_qv = np.zeros((len(pressure_levels), num_points))
        cross_section_theta = np.zeros((len(pressure_levels), num_points))

        for i, (lat, lon) in enumerate(path_points):
            query_points = np.array([[lon, lat]])

            if band_width_km <= 0:  # "一刀切"模式
                for level_idx in range(len(pressure_levels)):
                    grid_qv = griddata(points, qv_3d[level_idx].ravel(), query_points, method="linear")
                    grid_t = griddata(points, t_3d[level_idx].ravel(), query_points, method="linear")
                    cross_section_qv[level_idx, i] = grid_qv[0]
                    cross_section_theta[level_idx, i] = grid_t[0] * (1000.0 / pressure_levels[level_idx]) ** (R_D / C_P)
            else:  # 帶寬平均模式
                # 計算剖面線的法線方向
                if i < num_points - 1:
                    d_lat = lats[i + 1] - lats[i]
                    d_lon = lons[i + 1] - lons[i]
                else:  # 最後一點使用前一點的方向
                    d_lat = lats[i] - lats[i - 1]
                    d_lon = lons[i] - lons[i - 1]

                # 法線向量 (注意經度在赤道附近與距離的換算)
                norm_vec = np.array([-d_lon * np.cos(np.deg2rad(lat)), d_lat])
                norm_vec /= np.linalg.norm(norm_vec)

                # 在法線方向上取樣5個點進行平均
                sample_points_ll = []
                for s in np.linspace(-0.5, 0.5, 5):
                    # 將帶寬轉換為經緯度偏移量 (近似)
                    offset_lat = s * (band_width_km / 111.0) * norm_vec[1]
                    offset_lon = s * (band_width_km / (111.0 * np.cos(np.deg2rad(lat)))) * norm_vec[0]
                    sample_points_ll.append([lon + offset_lon, lat + offset_lat])

                for level_idx in range(len(pressure_levels)):
                    grid_qv = griddata(points, qv_3d[level_idx].ravel(), sample_points_ll, method="linear")
                    grid_t = griddata(points, t_3d[level_idx].ravel(), sample_points_ll, method="linear")

                    cross_section_qv[level_idx, i] = np.nanmean(grid_qv)
                    theta = np.nanmean(grid_t) * (1000.0 / pressure_levels[level_idx]) ** (R_D / C_P)
                    cross_section_theta[level_idx, i] = theta

        # 4. 繪圖
        fig, ax = plt.subplots(figsize=(12, 6))

        # 繪製 Qv (水氣) 填色圖
        # 註: 請求是 contourf: Qv 和 contour: Qv，但目前資料只有 Qv。
        # 我們用位溫 theta 做 contour，這是更常見且有意義的物理剖面圖。
        qv_levels = np.linspace(0, 0.02, 21)  # kg/kg
        cf = ax.contourf(distances, pressure_levels, cross_section_qv, levels=qv_levels, cmap="GnBu", extend="max")
        fig.colorbar(cf, ax=ax, label="Specific Humidity (Qv) [kg kg-1]")

        # 繪製位溫等高線
        theta_levels = np.arange(280, 400, 4)  # K
        cs = ax.contour(
            distances, pressure_levels, cross_section_theta, levels=theta_levels, colors="k", linewidths=0.8
        )
        ax.clabel(cs, inline=True, fontsize=8, fmt="%1.0f")

        ax.set_ylim(1000, 150)  # Y軸反轉，地面在下
        ax.set_yscale("log")
        ax.set_yticks([1000, 850, 700, 500, 300, 200])
        ax.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
        ax.set_ylabel("Pressure (hPa)")
        ax.set_xlabel("Distance (km)")

        title_prefix = "Ground Truth" if is_gt else "Forecast"
        valid_time = self.manager.get_forecast_time(forecast_step).strftime("%Y-%m-%d %H:%M Z")
        ax.set_title(
            f"{title_prefix} Cross Section at {valid_time}\n"
            f"From ({start_point[0]:.2f}, {start_point[1]:.2f}) to ({end_point[0]:.2f}, {end_point[1]:.2f})"
        )

        # 在 X 軸上標示起點和終點
        ax.set_xticks(np.linspace(0, distances[-1], 5))
        secax = ax.secondary_xaxis("top")
        secax.set_xticks([distances[0], distances[-1]])
        secax.set_xticklabels(
            [f"Start\n({start_point[0]:.1f}, {start_point[1]:.1f})", f"End\n({end_point[0]:.1f}, {end_point[1]:.1f})"]
        )

        ax.grid(True, linestyle="--", alpha=0.6)

        # 5. 儲存圖片
        filename = f"cross_section_{'gt' if is_gt else 'fc'}_{forecast_step:03d}.png"
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved cross section plot to {output_path}")
        return output_path
```

## File: src/dlamp/inference/infer_utils.py
```python
from collections import defaultdict
from collections.abc import Callable
from functools import partial, wraps

import numpy as np
import onnxruntime as ort
import torch
import yaml
from torch import nn

from dlamp.const import REPO_ROOT
from dlamp.models.builders.pangu_builder import PanguBuilder
from dlamp.standardizer import Standardizer, get_standardizer
from dlamp.utils import DataCompose


def prediction_postprocess(
    trainer_output: list[list[np.ndarray]],
    mapping: dict[int, str],
    standardizer: Standardizer | None = None,
) -> defaultdict[str, np.ndarray]:
    """
    Perform post-processing on the trainer output predictions by combining all the batches.

    Parameters:
        trainer_output (list[list[np.ndarray]]): The output predictions from the trainer.
            Shape: [epochs][num_product_type][B, lv, h, w, c]
        mapping (dict[int, str]): A mapping dictionary representing the order of trainer_output.
            The structure is like:
            {
                "input_upper": 0,
                "input_surface": 1,
                "target_upper": 2,
                "target_surface": 3,
                "output_upper": 4,
                "output_surface": 5,
            }
            For more details, please refer to `XXXLightningModule.get_pred_mapping()`

    Returns:
        defaultdict: Processed predictions in shape: {product_type: (B, lv, h, w, c)...}
    """
    predictions = defaultdict(list)
    standardizer = standardizer or get_standardizer()
    for epoch_id in range(len(trainer_output)):
        for key, value in mapping.items():
            predictions[key].append(trainer_output[epoch_id][value])

    for k, v in predictions.items():
        if "output" in k:
            tmp = [standardizer.destandardize(ele) for ele in v]
            tmp = np.stack(tmp, axis=0)  # {"output_upper": (B, Seq, lv, h, w, c)}
        else:
            tmp = np.concatenate(v, axis=0)  # {"input_upper": (B, lv, h, w, c)...}
            tmp = standardizer.destandardize(tmp)
        predictions[k] = tmp
    return predictions


def ort_instance_decorator(func):
    onnx_path = None
    gpu_id = None

    @wraps(func)
    def wrapper(**kwargs) -> ort.InferenceSession | partial:
        nonlocal onnx_path, gpu_id
        if "onnx_path" in kwargs:
            onnx_path = kwargs["onnx_path"]
        if "gpu_id" in kwargs:
            gpu_id = kwargs["gpu_id"]

        if onnx_path is not None and gpu_id is not None:
            return func(onnx_path=onnx_path, gpu_id=gpu_id)
        elif onnx_path is not None:
            return partial(func, onnx_path=onnx_path)
        elif gpu_id is not None:
            return partial(func, gpu_id=gpu_id)
        else:
            raise RuntimeError("onnx_path and gpu_id are both None. Please specify onnx_path and gpu_id.")

    return wrapper


@ort_instance_decorator
def init_ort_instance(gpu_id: int, onnx_path: str) -> ort.InferenceSession:
    assert "CUDAExecutionProvider" in ort.get_available_providers()

    # An issue about onnxruntime for cuda12.x
    # ref: https://github.com/microsoft/onnxruntime/issues/8313#issuecomment-1486097717
    _default_session_options = ort.capi._pybind_state.get_default_session_options()

    def get_default_session_options_new():
        _default_session_options.inter_op_num_threads = 1
        _default_session_options.intra_op_num_threads = 1
        return _default_session_options

    ort.capi._pybind_state.get_default_session_options = get_default_session_options_new

    return ort.InferenceSession(
        onnx_path,
        providers=[
            (
                "CUDAExecutionProvider",
                {
                    "device_id": gpu_id,
                },
            ),
            "CPUExecutionProvider",
        ],
    )


def load_pangu_model(
    ckpt_path: str, data_list: list[DataCompose], image_shape: list[int, int]
) -> Callable[[torch.device], nn.Module]:
    """Load a Pangu model from a PyTorch Lightning checkpoint.

    Args:
        ckpt_path (str): Absolute path to the ``.ckpt`` file.
        data_list (list[DataCompose]): Variable composition list used at
            training time.
        image_shape (list[int, int]): Spatial dimensions ``[H, W]``.

    Returns:
        Callable[[torch.device], nn.Module]: A closure that moves the
            loaded model to ``device`` when called.

    Raises:
        FileNotFoundError: If either the model or lightning YAML config
            cannot be found under ``REPO_ROOT / 'config'``.
    """
    model_cfg_path = REPO_ROOT / "config" / "model" / "pangu_rwrf.yaml"
    lightning_cfg_path = REPO_ROOT / "config" / "lightning" / "pangu_rwrf.yaml"
    with open(model_cfg_path) as stream:
        cfg_model = yaml.safe_load(stream)
    with open(lightning_cfg_path) as stream:
        cfg_lightning = yaml.safe_load(stream)

    # build model
    pangu_builder = PanguBuilder("dummy", data_list, image_shape=image_shape, **cfg_model, **cfg_lightning)
    model = pangu_builder._backbone_model()

    # load weights from checkpoint
    ckpt = torch.load(ckpt_path, weights_only=False)
    state_dict = {k.replace("backbone_model.", ""): v for k, v in ckpt["state_dict"].items()}
    model.load_state_dict(state_dict)

    return lambda device: model.to(device)
```

## File: src/dlamp/utils/data_compose.py
```python
from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic.dataclasses import dataclass

from ..const import VAR_SUFFIX
from .data_type import DataType, Level

__all__ = ["DataCompose", "DataType", "Level"]


@dataclass
class DataCompose:
    var_name: DataType
    level: Level
    basename: str = ""
    combined_key: str = ""
    is_radar: bool = False

    def __post_init__(self) -> None:
        """
        This method is called automatically after an instance of the class is created.

        It sets the `level` attribute to `Level.NoRule` if the `var_name` attribute is
        either `DataType.dBZ`, `DataType.XLAT`, or `DataType.XLON`.

        Args:
            self (DataCompose): The instance of the class.

        Returns:
            None
        """
        if self.var_name in [DataType.dBZ, DataType.XLAT, DataType.XLON]:
            self.level = Level.NoRule
        if self.var_name in [DataType.Td2m, DataType.RH]:
            self.level = Level.Meter2

        self.basename = f"{self.level.code}{self.var_name.short_name}{VAR_SUFFIX}"
        self.combined_key = self.get_combined_key()
        self.is_radar = self.var_name == DataType.dBZ

    def __str__(self) -> str:
        return f"{self.var_name.name}@{self.level.name}"

    @staticmethod
    def retrive_var_level_from_string(sentence: str) -> tuple[DataType, Level]:
        var_str = sentence.split("@")[0]
        level_str = sentence.split("@")[1]
        return getattr(DataType, var_str), getattr(Level, level_str)

    def get_combined_key(self) -> str:
        """
        Combine the NetCDF key of the variable and level into a single string.
        """
        if self.level not in [Level.Meter2, Level.Meter10, Level.Meter100]:
            return self.var_name.nc_key

        if self.var_name in [DataType.Td2m, DataType.RH]:
            return f"{self.var_name.nc_key}{self.level.nc_key}"

        if self.var_name in [DataType.U10m, DataType.V10m]:
            prefix = self.var_name.nc_key.split("_")[0]
            return f"{prefix}{self.level.nc_key}"

        if self.var_name in [DataType.T2m, DataType.Qv]:
            prefix = self.var_name.short_name[0]
            return f"{prefix}{self.level.nc_key}"

        return self.var_name.nc_key

    @classmethod
    def from_config(cls, config: dict[str, list[str]]) -> list[DataCompose]:
        """
        A method to create a list of DataCompose objects based on the provided config.

        Args:
            config (dict[str, str]): A dictionary containing the configuration.
                The dictoinary should have the following structure:
                    {
                        "PH": ["Hpa200", "Hpa500", "Hpa700", "Hpa850", "Hpa925"],
                        "TK": ["Hpa200", "Hpa500", "Hpa700", "Hpa850", "Hpa925"],
                        ...
                    }
        Returns:
            list[DataCompose]: A list of DataCompose objects.
        """
        data_list = []
        for var, lvs in config.items():
            for lv in lvs:
                data_list.append(cls(DataType[var], Level[lv]))  # type: ignore[call-arg]
        return data_list

    @staticmethod
    def get_all_hook(
        fn: Callable[[Any, DataCompose], None],
    ) -> Callable[..., list[Enum] | list[str]]:
        def wrapper(
            data_list: list[DataCompose],
            only_upper: bool = False,
            only_surface: bool = False,
            to_str: bool = False,
        ) -> list[Enum] | list[str]:
            """
            A wrapper function that takes a list of `DataCompose` objects, along with optional
            boolean flags `only_upper` and `only_surface`, and returns a list of `StrEnum` or `str` values.

            Parameters:
                data_list (list[DataCompose]): A list of `DataCompose` objects.
                only_upper (bool, optional): If True, only the levels that are not surface levels will be
                    included in the returned list. Defaults to False.
                only_surface (bool, optional): If True, only the surface levels will be included in the returned
                    list. Defaults to False.
                to_str (bool, optional): If True, the returned list will contain `str` values instead of `StrEnum`
                    objects. Defaults to False.

            Raises:
                ValueError: If both `only_upper` and `only_surface` are True.

            Returns:
                list[StrEnum] | list[str]: A list of `StrEnum` or `str` values, depending on the value of `to_str`.
            """
            if only_upper and only_surface:
                raise ValueError("only_upper and only_surface cannot both be True")

            ret: list[Enum] | list[str] = []
            for data_compose in data_list:
                lv = data_compose.level
                if (
                    lv.is_surface()
                    and only_surface
                    or not lv.is_surface()
                    and only_upper
                    or not only_surface
                    and not only_upper
                ):
                    fn(ret, data_compose)
            return [x.name for x in ret] if to_str else ret  # type: ignore[union-attr]

        return wrapper

    @staticmethod
    @get_all_hook
    def get_all_levels(result: list[Level], data_compose: DataCompose) -> None:
        """
        Get a list of `Level` objects or a list of Level `str` from a given list of `DataCompose` objects.

        Can choose to include only surface levels or only upper levels.
        """
        if data_compose.level not in result:
            result.append(data_compose.level)

    @staticmethod
    @get_all_hook
    def get_all_vars(result: list[DataType], data_compose: DataCompose) -> None:
        """
        Get a list of `DataType` objects or a list of DataType `str` from a given list of `DataCompose` objects.

        Can choose to include only surface levels or only upper levels.
        """
        if data_compose.var_name not in result:
            result.append(data_compose.var_name)
```

## File: src/dlamp/utils/data_generator.py
```python
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, cast

import numpy as np
import torch
from einops.layers.torch import Rearrange
from torchvision.transforms.v2 import CenterCrop, Compose, Resize

from .data_compose import DataCompose
from .file_util import gen_data


class DataGenerator:
    def __init__(self, data_shape: list[int], image_shape: list[int]) -> None:
        self._data_shp = data_shape
        self._img_shp = image_shape
        self.preprocess = self._preprocess()

    @staticmethod
    def yield_data_hook(
        fn: Callable[[Any, np.ndarray, bool], torch.Tensor | np.ndarray],
    ) -> Callable[..., torch.Tensor | np.ndarray | dict[str, np.ndarray]]:
        def wrapper(
            self: DataGenerator,
            target_time: datetime,
            data_compose: DataCompose | list[DataCompose],
            to_numpy: bool = True,
            **kwargs: Any,
        ) -> torch.Tensor | np.ndarray | dict[str, np.ndarray]:
            """
            A wrapper function that handles data generation and preprocessing. The output can be either
            a single sequence data or a dictionary of sequences depending on the type of input data_compose.

            Parameters:
                target_time (datetime): The target timestamp for data generation.
                data_compose (DataCompose | list[DataCompose]): Single or multiple DataCompose objects
                    specifying the type and level of data to generate.
                to_numpy (bool, optional): Whether to return the processed data as numpy array or torch
                    Tensor. Defaults to True.

            Returns:
                Sequence | dict[str, Sequence]: Processed data either as a single sequence or
                dictionary of sequences if multiple DataCompose objects are provided.
            """
            data: np.ndarray | dict[str, np.ndarray] = gen_data(
                target_time, data_compose, dtype=np.float32, **kwargs
            )  # (H, W)

            if isinstance(data, np.ndarray):
                return fn(self, data, to_numpy)
            elif isinstance(data, dict):
                for key, np_data in data.items():
                    data[key] = cast(np.ndarray, fn(self, np_data, to_numpy))
                return data
            raise AssertionError("unreachable")

        return wrapper

    @yield_data_hook
    def yield_data(self, np_data: np.ndarray, to_numpy: bool = True) -> torch.Tensor | np.ndarray:
        """
        Generate a tensor or numpy array of processed data based on the provided numpy array.

        Parameters:
            np_data (np.ndarray): The numpy array containing the data to be processed.
            to_numpy (bool, optional): Whether to return the data as a numpy array. Defaults to True.

        Returns:
            torch.Tensor or np.ndarray: The processed data in shape (H, W).
        """
        if isinstance(self.preprocess, Compose):
            torch_data = torch.from_numpy(np_data[None]).type(torch.float32)  # (1, H, W)
            processed_data: torch.Tensor = self.preprocess(torch_data)  # (H, W)
            return processed_data.numpy() if to_numpy else processed_data
        else:
            return self.preprocess(np_data)

    def _preprocess(self) -> torch.Tensor:
        """
        Perform preprocessing on the data by applying a series of transformations:
        1. Center crop the image based on the specified dimensions.
        2. Resize the image to the desired shape.
        3. Rearrange the image dimensions from "c h w" to "h w".

        Returns:
            torch.Tensor: Preprocessed data
        """
        factors = [x // y for x, y in zip(self._data_shp, self._img_shp)]
        return Compose(
            [
                CenterCrop([n * x for n, x in zip(factors, self._img_shp)]),
                Resize(self._img_shp),
                Rearrange("c h w -> (c h) w"),
            ]
        )

    def _data_shape_check(self, target_dt: datetime, data: np.ndarray) -> None:
        """
        Check if the shape of the given data matches the original data shape.

        Args:
            target_dt (datetime): The target datetime for which the data is being checked.
            data (np.ndarray): The data array to be checked.

        Raises:
            AssertionError: If the shape of the data does not match the expected shape.

        Returns:
            None
        """
        assert data.shape == self._data_shp, f"{target_dt} data shape mismatch: {data.shape} != {self._data_shp}"
```

## File: src/dlamp/utils/data_type.py
```python
from __future__ import annotations

from enum import Enum
from typing import Self, cast


class DataType(Enum):
    def __new__(
        cls,
        short_name: str,
        standard_name: str,
        description: str,
        units: str,
        nc_key: str,
    ) -> Self:
        obj = object.__new__(cls)
        obj._value_ = (short_name, standard_name, description, units, nc_key)
        return obj

    @property
    def short_name(self) -> str:
        return cast(str, self.value[0])

    @property
    def standard_name(self) -> str:
        return cast(str, self.value[1])

    @property
    def description(self) -> str:
        return cast(str, self.value[2])

    @property
    def units(self) -> str:
        return cast(str, self.value[3])

    @property
    def nc_key(self) -> str:
        return cast(str, self.value[4])

    # Coordinates
    # fmt: off
    # (short_name, standard_name, description, units, nc_key)
    Lat   = ("lat",   "latitude",  "Latitude (1-D, monotonic increasing)",  "degrees_north", "lat")
    Lon   = ("lon",   "longitude", "Longitude (1-D, monotonic increasing)", "degrees_east",  "lon")
    XLAT  = ("XLAT",  "latitude",  "Latitude meshgrid (2-D)",               "degrees_north", "XLAT")
    XLON  = ("XLON",  "longitude", "Longitude meshgrid (2-D)",              "degrees_east",  "XLON")

    # Pressure-level fields (nc_key = {shortname}_{hPa})
    TK  = ("TK",  "air_temperature",                  "Temperature",                      "K",       "TK")
    Z   = ("Z",   "geopotential_height",              "Geopotential height",              "m",       "Z")
    UM  = ("UM",  "eastward_wind",                    "U-wind component",                 "m s-1",   "UM")
    VM  = ("VM",  "northward_wind",                   "V-wind component",                 "m s-1",   "VM")
    WA  = ("WA",  "upward_air_velocity",              "W-wind (vertical) component",      "m s-1",   "WA")
    RH  = ("RH",  "relative_humidity",                "Relative humidity",                "%",       "RH")
    Qv  = ("Qv",  "water_vapor_mixing_ratio",         "Water-vapor mixing ratio",         "kg kg-1", "Qv")
    Qc  = ("Qc",  "cloud_water_mixing_ratio",         "Cloud-water mixing ratio",         "kg kg-1", "Qc")
    Qi  = ("Qi",  "cf:cloud_ice_mixing_ratio",        "Cloud-ice mixing ratio",           "kg kg-1", "Qi")
    Qr  = ("Qr",  "cf:rain_water_mixing_ratio",       "Rain-water mixing ratio",          "kg kg-1", "Qr")
    Qs  = ("Qs",  "cf:snow_mixing_ratio",             "Snow mixing ratio",                "kg kg-1", "Qs")
    Qg  = ("Qg",  "cf:graupel_mixing_ratio",          "Graupel mixing ratio",             "kg kg-1", "Qg")

    # AGL fields (nc_key = {shortname}_{height_in_m}m)
    T2m  = ("T",  "air_temperature",        "Air temperature",           "K",       "T_2m")
    Td2m = ("Td", "dew_point_temperature",  "Dew-point temperature",     "K",       "Td_2m")
    U10m = ("U",  "eastward_wind",          "U-wind component",          "m s-1",   "U_10m")
    V10m = ("V",  "northward_wind",         "V-wind component",          "m s-1",   "V_10m")

    # Other single-level horizontal fields
    SLP      = ("SLP",     "air_pressure_at_sea_level",         "Sea-level pressure",            "Pa",      "SLP")
    PSFC     = ("PSFC",    "surface_air_pressure",              "Surface pressure",              "Pa",      "PSFC")
    SST      = ("SST",     "sea_surface_temperature",           "Sea-surface temperature",       "K",       "SST")
    PW       = ("PW",      "atmosphere_mass_content_of_water_vapor", "Precipitable-water column", "kg m-2",  "PW")
    PBLH     = ("PBLH",    "atmosphere_boundary_layer_thickness", "Planetary boundary-layer height", "m",  "PBLH")
    RAINNC   = ("RAINNC",  "precipitation_amount",              "Accumulated precipitation",     "kg m-2",  "RAINNC")
    SWDOWN   = ("SWDOWN",  "surface_downwelling_shortwave_flux_in_air", "Downward shortwave flux", "W m-2",  "SWDOWN")
    OLR      = ("OLR",     "toa_outgoing_longwave_flux",        "Outgoing longwave radiation",   "W m-2",   "OLR")
    HGT      = ("HGT",     "surface_altitude",                  "Terrain height",                "m",       "HGT")
    MASKLAND = ("MASKLAND", "cf:land_binary_mask",              "Land-sea mask (bool)",          "1",       "LANDMASK")
    dBZ      = ("REFL",    "radar_reflectivity",                "Max column radar reflectivity", "dBZ",     "REFL")

    # Model input: read directly from source, never derived (no diagnostic).
    Qt = ("Qt", "cf:total_hydrometeor_mixing_ratio", "Total hydrometeor mixing ratio", "kg kg-1", "Qt")

    # Pressure coordinate (not a model output): source pressure-level array, used
    # only to map a level to its index when reading a pressure-level field.
    P = ("P", "air_pressure", "Pressure coordinate", "Pa", "pres_levels")
    # fmt: on


class Level(Enum):
    code: str
    nc_key: str

    def __new__(cls, description: str, code: str, nc_key: str) -> Self:
        obj = object.__new__(cls)
        obj._value_ = description
        obj.code = code
        obj.nc_key = nc_key
        return obj

    # level_name = (description, code, nc_key)
    Hpa50 = ("50 Hpa", "50", "50")
    Hpa100 = ("100 Hpa", "100", "100")
    Hpa150 = ("150 Hpa", "150", "150")
    Hpa200 = ("200 Hpa", "200", "200")
    Hpa250 = ("250 Hpa", "250", "250")
    Hpa300 = ("300 Hpa", "300", "300")
    Hpa350 = ("350 Hpa", "350", "350")
    Hpa400 = ("400 Hpa", "400", "400")
    Hpa450 = ("450 Hpa", "450", "450")
    Hpa500 = ("500 Hpa", "500", "500")
    Hpa550 = ("550 Hpa", "550", "550")
    Hpa600 = ("600 Hpa", "600", "600")
    Hpa650 = ("650 Hpa", "650", "650")
    Hpa700 = ("700 Hpa", "700", "700")
    Hpa750 = ("750 Hpa", "750", "750")
    Hpa800 = ("800 Hpa", "800", "800")
    Hpa850 = ("850 Hpa", "850", "850")
    Hpa900 = ("900 Hpa", "900", "900")
    Hpa925 = ("925 Hpa", "925", "925")
    Hpa950 = ("950 Hpa", "950", "950")
    Hpa975 = ("975 Hpa", "975", "975")
    Hpa1000 = ("1000 Hpa", "H00", "1000")
    LowestModelLevel = ("Lowest Model Level", "B00", "")
    Meter2 = ("2 m", "B02", "2")
    Meter10 = ("10 m", "B10", "10")
    Meter100 = ("100 m", "H10", "")
    Surface = ("Surface", "S00", "")
    SeaSurface = ("Sea Surface", "W00", "")
    TOA = ("Top Of Atmosphere", "W00", "")
    NoRule = ("NoRule", "X00", "")

    def is_surface(self) -> bool:
        return self in [
            self.LowestModelLevel,
            self.Meter2,
            self.Meter10,
            self.Meter100,
            self.Surface,
            self.SeaSurface,
            self.TOA,
            self.NoRule,
        ]
```

## File: src/dlamp/utils/file_util.py
```python
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import numpy as np
import xarray as xr

from ..data.source_strategy import NEO171RwrDataSource, get_data_source
from ..runtime_config import RuntimeConfig, get_runtime_config
from .data_compose import DataCompose, DataType


def _get_config() -> RuntimeConfig:
    return get_runtime_config()


def gen_data(
    target_time: datetime,
    data_compose: DataCompose | list[DataCompose],
    use_Kth_hour_pred: int | None = None,
    dtype: np.dtype | None = None,
) -> np.ndarray | dict[str, np.ndarray]:
    """
    Generate numpy array data for a given target time and data composition.

    Args:
        target_time (datetime): The target time for which the data is generated.
        data_compose (DataCompose | list[DataCompose]): The data composition object or a list
            of data composition objects.
        use_Kth_hour_pred (int | None): Use the Kth hour prediciton to generate the file path if
            not None. Else, use the target time.
        dtype (np.dtype | None, optional): The data type of the generated data. Defaults to None.

    Returns:
        The generated data.
    """
    config = _get_config()
    source = get_data_source(config.data_source)
    is_neo = isinstance(source, NEO171RwrDataSource)
    if isinstance(data_compose, DataCompose):
        file_name = source.gen_path(
            target_time,
            config,
            data_compose=data_compose,
            use_Kth_hour_pred=use_Kth_hour_pred,
        )
        if is_neo:
            return read_cwa_npfile(file_name, data_compose.is_radar, dtype)
        return read_cwa_ncfile(file_name, data_compose, dtype)
    else:
        ret = {}
        for ele in data_compose:
            file_name = source.gen_path(
                target_time,
                config,
                data_compose=ele,
                use_Kth_hour_pred=use_Kth_hour_pred,
            )
            if is_neo:
                ret[str(ele)] = read_cwa_npfile(file_name, ele.is_radar, dtype)
            else:
                ret[str(ele)] = read_cwa_ncfile(file_name, ele, dtype)
        return ret


def read_cwa_ncfile(
    file_path: Path,
    data_compose: DataCompose | list[DataCompose],
    dtype: np.dtype | None = None,
) -> np.ndarray | dict[str, np.ndarray]:
    """
    Read data from a NetCDF file based on the provided data composition.

    Args:
        file_path (Path): Path to the NetCDF file.
        data_compose (DataCompose | list[DataCompose]): A single DataCompose object or a list of
            DataCompose objects specifying what data to extract.
        dtype (np.dtype | None, optional): The numpy dtype to cast the data to. If None, keeps original dtype.
            Defaults to None.

    Returns:
        np.ndarray | dict[str, np.ndarray]: If data_compose is a single DataCompose object, returns a numpy array
            containing the requested data. If data_compose is a list, returns a dictionary mapping DataCompose
            string representations to their corresponding numpy arrays.
    """
    dataset = xr.open_dataset(str(file_path))

    def fn(dc: DataCompose) -> np.ndarray:
        """
        Extract variable data from a RWRF output NetCDF dataset based on the data composition.

        Args:
            dc (DataCompose): DataCompose object specifying the variable and level to extract

        Returns:
            np.ndarray: The extracted variable data. For surface variables, returns shape (H, W).
                For pressure level variables, extracts the specified level and returns shape (H, W).
                H and W are the horizontal dimensions of the data.
        """
        if dc.var_name == DataType.Qt:
            # Read the total hydrometeor field directly from source; never
            # derive it from Qr/Qc/Qi/Qs/Qg (diagnostics live in data plugins).
            data = dataset[dc.combined_key].values
        elif dc.var_name == DataType.SST:
            data = dataset[dc.combined_key].values
            data[np.isnan(data)] = 298.60870361328125  # SST mean
            # original masking of land points was disabled
        else:
            data = dataset[dc.combined_key].values  # (1, Z, H, W) or (1, H, W)

        data = data.astype(dtype) if dtype is not None else data

        if dc.level.is_surface():
            return data[0]
        else:
            pres_lvs = dataset[DataType.P.nc_key].values
            (idx,) = np.where(pres_lvs == float(dc.level.nc_key))
            return data[0, idx[0]]

    try:
        if isinstance(data_compose, DataCompose):
            return fn(data_compose)
        elif isinstance(data_compose, list):
            ret = {}
            for ele in data_compose:
                ret[str(ele)] = fn(ele)
            return ret
    except Exception as e:  # noqa: BLE001 - re-raised as RuntimeError
        raise RuntimeError(f"Data retrieval fails for {file_path}. Original error: {e}")


def read_cwa_npfile(file_path: Path, is_radar: bool, dtype: np.dtype | None = None) -> np.ndarray:
    """
    The x and y grids point of RWRF model data are 450 and 450, respectively.

    One thing needs to notice, the data type may save as little-endian with
    double precision or big-endian with double precision. User may design a
    judgment rule for checking if there are weird values after read data.
    """
    data = np.fromfile(file_path, dtype=">d", count=-1, sep="").reshape(450, 450)

    # since log(0) = -inf, log(neg) = nan, np.all() will always return False
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        log_data = np.log(data)
    log_data = np.ma.array(log_data, mask=np.isnan(log_data) + np.isneginf(log_data))

    if is_radar and (np.all(data < 0.1) and np.all(log_data > -10000)):
        data = np.fromfile(file_path, dtype="<d", count=-1, sep="").reshape(450, 450)

    if (not is_radar) and np.all(log_data < -500):
        data = np.fromfile(file_path, dtype="<d", count=-1, sep="").reshape(450, 450)

    if dtype is not None:
        data = data.astype(dtype)

    if is_radar:
        data[data < 0] = 0  # set negative values to 0

    return data


def gen_path(
    target_time: datetime,
    data_compose: None | DataCompose = None,
    use_Kth_hour_pred: int | None = None,
    data_source: str | None = None,
) -> Path:
    """
    A function that generates a path based on the given target time and data compose.

    Parameters:
        target_time (datetime): The target time for generating the path.
        data_compose (None | DataCompose): The data composition object.
        use_Kth_hour_pred (int | None): Use Kth hour prediciton to generate the file path
            if not None. Else, use the oringal inital time.
        data_source (str): The way generating the path depends on different data sources.
            e.g.
                "NEO171_RWRF" -> data stored on neo171 server
                "CWA_RWRF" -> data stored on CWA HPC

    Returns:
        Path: The generated path.
    """
    config = _get_config()
    if data_source is None:
        data_source = config.data_source
    source = get_data_source(data_source)
    return source.gen_path(
        target_time,
        config,
        data_compose=data_compose,
        use_Kth_hour_pred=use_Kth_hour_pred,
    )


def convert_hydra_dir_to_timestamp(hydra_dir: Path | str) -> str:
    """
    Convert a directory path to a timestamp string. Or just return itself if it's in `str` type.

    Args:
        hydra_dir (Path | str): The path to the hydra output directory.

    Returns:
        str: The timestamp string in the format "%y%m%d_%H%M%S".

    Raises:
        ValueError: If the hydra directory path cannot be parsed into a datetime object.
    """
    try:
        path = cast(Path, hydra_dir)
        dt = datetime.strptime(f"{path.parent.name} {path.name}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        if isinstance(hydra_dir, str):
            warnings.warn(
                f'given hydra dir "{hydra_dir}" can\'t be parsed into datetime, '
                f"return itself ({hydra_dir}) as timestamp",
                UserWarning,
            )
            return hydra_dir
        else:
            raise TypeError(f"given hydra dir {hydra_dir} can't be parsed into datetime")

    return dt.strftime("%y%m%d_%H%M%S")
```

## File: src/dlamp/visual/viz_radar.py
```python
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dlamp.const import DBZ_COLOR, DBZ_LV, DBZ_NORM, FIGURE_PATH
from dlamp.utils import DataCompose, DataType, Level, gen_data

from .tw_background import TwBackground


class VizRadar(TwBackground):
    def __init__(self):
        super().__init__()
        self.title_suffix = "Radar Reflectivity"

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth: np.ndarray,
        prediction: np.ndarray,
        all_init_times: list[datetime] | None = None,
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        """
        Args:
            lon (np.ndarray): The longitude data with shape (H, W).
            lat (np.ndarray): The latitude data with shape (H, W).
            ground_truth (np.ndarray): The ground truth data with shape (S, H, W).
            prediction (np.ndarray): The predicted data with shape (S, H, W).
            all_init_times (list[datetime]): A list of all initial times in length S.
            grid_on (bool, optional): Whether to show grid. Defaults to False.
        """
        if all_init_times is None:
            all_init_times = []
        assert len(ground_truth.shape) == 3
        assert ground_truth.shape[-2:] == lat.shape

        # since lat/lon may not be monotonically increasing in a same pace
        if len(lat.shape) == 2 and len(lon.shape) == 2:
            lat = np.linspace(lat[0, 0], lat[-1, 0], lat.shape[0])
            lon = np.linspace(lon[0, 0], lon[0, -1], lon.shape[1])

        rows = 2  # gt/pred
        columns = ground_truth.shape[0]

        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_radar(fig, tmp_ax, lon, lat, ground_truth[j], time_title)

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_radar(fig, tmp_ax, lon, lat, prediction[j], time_title)

        return fig, ax

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        # since lat/lon may not be monotonically increasing in a same pace
        if len(lat.shape) == 2 and len(lon.shape) == 2:
            lat = np.linspace(lat[0, 0], lat[-1, 0], lat.shape[0])
            lon = np.linspace(lon[0, 0], lon[0, -1], lon.shape[1])

        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(7, 7), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax, grid_on)
        fig, ax = self._plot_radar(fig, ax, lon, lat, data, title)

        return fig, ax

    def _plot_radar(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        ax.pcolormesh(
            lon,
            lat,
            data,
            edgecolors="none",
            shading="auto",
            norm=DBZ_NORM,
            cmap=DBZ_COLOR,
            # cmap="magma",  # corrdiff
            # vmax=40,  # corrdiff
            # vmin=0,  # corrdiff
            zorder=0,
        )
        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        # cbar = fig.colorbar(pc, cax=cax) # corrdiff
        cbar = fig.colorbar(
            cm.ScalarMappable(norm=DBZ_NORM, cmap=DBZ_COLOR),
            cax=cax,
            ticks=np.arange(DBZ_LV[0], DBZ_LV[-1] + 1, 5),
        )
        cbar.ax.set_title("dBZ")
        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: list[np.ndarray],
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        if len(lat.shape) == 2 and len(lon.shape) == 2:
            lat = np.linspace(lat[0, 0], lat[-1, 0], lat.shape[0])
            lon = np.linspace(lon[0, 0], lon[0, -1], lon.shape[1])

        cols = len(data)

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(20, 7), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_radar(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax


if __name__ == "__main__":
    target_time = datetime(2022, 10, 16, 0, tzinfo=UTC)
    data_radar = gen_data(target_time, DataCompose(DataType.dBZ, Level.NoRule))
    data_lat = gen_data(target_time, DataCompose(DataType.XLAT, Level.Surface))
    data_lon = gen_data(target_time, DataCompose(DataType.XLON, Level.Surface))

    viz = VizRadar()
    fig, ax = viz.plot_1x1(data_lon, data_lat, data_radar)
    fig.savefig(
        f"{FIGURE_PATH}/{target_time.strftime('%Y%m%d_%H%M')}_mos.png",
        transparent=False,
    )
    plt.close()
```

## File: src/dlamp/visual/viz_temp.py
```python
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dlamp.const import FIGURE_PATH, TEMP_COLOR, TEMP_LV
from dlamp.utils import DataCompose, DataType, Level, gen_data

from .tw_background import TwBackground


class VizTemp(TwBackground):
    def __init__(self, pressure_level: int | None = None):
        super().__init__()
        self.press_lv = pressure_level
        self.title_suffix = f"Temperature@{self.press_lv}" if pressure_level else ""

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth: np.ndarray,
        prediction: np.ndarray,
        all_init_times: list[datetime] | None = None,
        grid_on: bool = False,
    ) -> tuple[Figure, Axes]:
        """
        Args:
            lon (np.ndarray): The longitude data with shape (H, W).
            lat (np.ndarray): The latitude data with shape (H, W).
            ground_truth (np.ndarray): The ground truth data with shape (S, H, W).
            prediction (np.ndarray): The predicted data with shape (S, H, W).
            all_init_times (list[datetime]): A list of all initial times in length S.
            grid_on (bool, optional): Whether to show grid. Defaults to False.
        """
        if all_init_times is None:
            all_init_times = []
        assert len(ground_truth.shape) == 3
        assert ground_truth.shape[-2:] == lat.shape

        rows = 2  # gt/pred
        columns = ground_truth.shape[0]

        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_temp(fig, tmp_ax, lon, lat, ground_truth[j], time_title)

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_temp(fig, tmp_ax, lon, lat, prediction[j], time_title)

        return fig, ax

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        temp: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax)
        fig, ax = self._plot_temp(fig, ax, lon, lat, temp, title)

        return fig, ax

    def _plot_temp(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        temp: np.ndarray,
        title: str = "",
    ) -> tuple[Figure, Axes]:
        # from Kelvin to Celsius
        temp_c = temp - 273.15

        # plot data
        conf = ax.contourf(
            lon,
            lat,
            temp_c,
            levels=TEMP_LV,
            colors=TEMP_COLOR,
            zorder=0,
            extend="max",
        )
        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("$^{o}$C")

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        data: np.ndarray,
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = data.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_temp(fig, tmp_ax, lon, lat, data[j], title)

        return fig, ax


if __name__ == "__main__":
    target_time = datetime(2022, 10, 16, 0, tzinfo=UTC)
    t850 = gen_data(target_time, DataCompose(DataType.TK, Level.Hpa850))
    data_lat = gen_data(target_time, DataCompose(DataType.XLAT, Level.Surface))
    data_lon = gen_data(target_time, DataCompose(DataType.XLON, Level.Surface))

    viz = VizTemp("Hpa850")
    fig, ax = viz.plot_1x1(data_lon, data_lat, t850)
    fig.savefig(
        f"{FIGURE_PATH}/{target_time.strftime('%Y%m%d_%H%M')}_temperature.png",
        transparent=False,
    )
    plt.close()
```

## File: src/dlamp/visual/viz_vor.py
```python
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dlamp.const import FIGURE_PATH
from dlamp.utils import DataCompose, DataType, Level, gen_data

from .tw_background import TwBackground


class VizVor(TwBackground):
    def __init__(self, pressure_level: int | None = None):
        super().__init__()
        self.press_lv = pressure_level
        self.title_suffix = f"Vorticity@{self.press_lv}" if pressure_level else ""

    def plot_mxn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        ground_truth_u: np.ndarray,
        ground_truth_v: np.ndarray,
        prediction_u: np.ndarray,
        prediction_v: np.ndarray,
        grid_resolution_in_meter: list[int],
        all_init_times: list[datetime] | None = None,
    ) -> tuple[Figure, Axes]:
        assert len(ground_truth_u.shape) == 3
        assert ground_truth_u.shape[-2:] == lat.shape

        rows = 2  # gt/pred
        columns = ground_truth_u.shape[0]
        plt.close()
        fig, ax = plt.subplots(rows, columns, figsize=(20, 7), dpi=200, facecolor="w")

        # ground truth
        for j in range(columns):
            tmp_ax = ax[0, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax)
            fig, tmp_ax = self._plot_vor(
                fig,
                tmp_ax,
                lon,
                lat,
                ground_truth_u[j],
                ground_truth_v[j],
                grid_resolution_in_meter,
                time_title,
            )

        # prediction
        for j in range(columns):
            tmp_ax = ax[1, j]
            time_title = all_init_times[j].strftime("%Y%m%d_%H%M") if all_init_times else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax)
            fig, tmp_ax = self._plot_vor(
                fig,
                tmp_ax,
                lon,
                lat,
                prediction_u[j],
                prediction_v[j],
                grid_resolution_in_meter,
                time_title,
            )

        return fig, ax

    def plot_1x1(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind: np.ndarray,
        v_wind: np.ndarray,
        grid_resolution_in_meter: list[int],
        title: str = "",
    ) -> tuple[Figure, Axes]:
        plt.close()
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), dpi=200, facecolor="w")
        fig, ax = super().plot_bg(fig, ax)
        fig, ax = self._plot_vor(fig, ax, lon, lat, u_wind, v_wind, grid_resolution_in_meter, title)

        return fig, ax

    def _plot_vor(
        self,
        fig: Figure,
        ax: Axes,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind: np.ndarray,
        v_wind: np.ndarray,
        grid_resolution_in_meter: list[int],
        title: str = "",
    ) -> tuple[Figure, Axes]:
        # calculate vorticity
        vor_u = (u_wind[1:, :] - u_wind[0:-1, :]) / grid_resolution_in_meter[1]
        vor_u = np.concatenate([vor_u[0:1, :], vor_u], axis=0)
        vor_v = (v_wind[:, 1:] - v_wind[:, 0:-1]) / grid_resolution_in_meter[0]
        vor_v = np.concatenate([vor_v[:, 0:1], vor_v], axis=1)
        vor = vor_v - vor_u

        # plot data
        conf = ax.contourf(
            lon,
            lat,
            10**5 * vor,
            np.arange(-100, 101, 2),
            cmap="bwr",
            zorder=0,
            extend="both",
        )
        if title:
            ax.set_title(f"{title} {self.title_suffix}")

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        # colorbar
        cbar = fig.colorbar(conf, cax=cax)
        cbar.ax.set_title("$\\frac{1}{10^5 s}$")
        cbar.set_ticks(np.arange(-100, 101, 20))

        return fig, ax

    def plot_1xn(
        self,
        lon: np.ndarray,
        lat: np.ndarray,
        u_wind_list: np.ndarray,
        v_wind_list: np.ndarray,
        grid_resolution_in_meter: list[int],
        titles: list[str] | None = None,
        grid_on: bool = False,
    ):
        if titles is None:
            titles = []
        cols = u_wind_list.shape[0]

        plt.close()
        fig, ax = plt.subplots(1, cols, figsize=(18, 2.5), dpi=200, facecolor="w")
        for j in range(cols):
            tmp_ax = ax[j]
            title = titles[j] if titles else ""
            fig, tmp_ax = self.plot_bg(fig, tmp_ax, grid_on)
            fig, tmp_ax = self._plot_vor(
                fig,
                tmp_ax,
                lon,
                lat,
                u_wind_list[j],
                v_wind_list[j],
                grid_resolution_in_meter,
                title,
            )

        return fig, ax


if __name__ == "__main__":
    target_time = datetime(2022, 10, 16, 0, tzinfo=UTC)
    u850 = gen_data(target_time, DataCompose(DataType.UM, Level.Hpa850))
    v850 = gen_data(target_time, DataCompose(DataType.VM, Level.Hpa850))
    data_lat = gen_data(target_time, DataCompose(DataType.XLAT, Level.Surface))
    data_lon = gen_data(target_time, DataCompose(DataType.XLON, Level.Surface))
    grid_point_resolution = [2e3, 2e3]  # unit: m (for lon/lat)

    viz = VizVor()
    fig, ax = viz.plot_1x1(
        data_lon,
        data_lat,
        u850,
        v850,
        grid_point_resolution,
    )
    fig.savefig(
        f"{FIGURE_PATH}/{target_time.strftime('%Y%m%d_%H%M')}_vorticity.png",
        transparent=False,
    )
    plt.close()
```

## File: src/dlamp/runtime_config.py
```python
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class RuntimeConfigError(Exception):
    """Raised when the runtime config fails validation."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime config driven by environment variables.

    Model code, data source, data path, and derived paths are all
    validated at construction time so that a mismatch of
    ``DLAMP_EXP_CODE`` fails loudly at startup rather than silently
    loading the wrong standardization.

    Constants set by the constructor are used in the same way as the
    previous module-level defaults but are explicitly validated.

    The singleton is threaded through the entrypoints and the
    deepened module layer. Callers that cannot use a constructor pass
    should call ``get_runtime_config()`` to retrieve the current
    singleton.
    """

    model_code: str
    data_source: str
    data_path: Path
    standardization_path: Path
    data_config_path: Path
    var_suffix: str = "WE01H0202500"

    @classmethod
    def from_env(cls) -> RuntimeConfig:
        """Build ``RuntimeConfig`` from environment variables with
        eager validation of the required files.

        Raises ``RuntimeConfigError`` when ``DLAMP_EXP_CODE`` points to
        a model version that has no matching *standardization* or *data
        config* files on disk.
        """
        model_code = os.environ.get("DLAMP_EXP_CODE", "20250627")
        data_source = os.environ.get("DLAMP_DATA_SOURCE", "OP_ERA5")
        data_path = Path(os.environ.get("DLAMP_DATA_PATH", "/wk2/yaochu/CASE_DATA/Pool/"))

        from dlamp.const import REPO_ROOT

        standardization_path = REPO_ROOT / "assets" / "standardization" / f"z_score_3h_{model_code}.json"
        data_config_path = REPO_ROOT / "config" / "data" / f"rwrf_{model_code}.yaml"

        missing = []
        if not standardization_path.exists():
            missing.append(f"standardization: {standardization_path}")
        if not data_config_path.exists():
            missing.append(f"data config: {data_config_path}")

        if missing:
            raise RuntimeConfigError(
                f"DLAMP_EXP_CODE '{model_code}' requires:\n" + "\n".join(f"  {m} [NOT FOUND]" for m in missing)
            )

        return cls(
            model_code=model_code,
            data_source=data_source,
            data_path=data_path,
            standardization_path=standardization_path,
            data_config_path=data_config_path,
        )

    @property
    def standardization_json_path(self) -> Path:
        return self.standardization_path


_singleton: RuntimeConfig | None = None


def get_runtime_config() -> RuntimeConfig:
    """Return (or construct) the singleton RuntimeConfig for the current
    process. The config is built lazily: the first call to
    ``get_runtime_config()`` performs env-var reading, path construction,
    and file existence validation. Subsequent calls reuse the cached instance.

    .. note:: If multiple entrypoints are run in the same process
              (e.g. tests), the last call wins.
    """
    global _singleton
    if _singleton is None:
        _singleton = RuntimeConfig.from_env()
    return _singleton


def get_runtime_config_error() -> str | None:
    """Return the last validation error raised by
    ``RuntimeConfig.from_env()``. Only has a value after a failed
    instantiation."""
    return getattr(get_runtime_config, "_last_error", None)
```

## File: src/dlamp/train.py
```python
"""Model training entrypoint.

Exposes the Hydra-wrapped ``main`` used by the ``dlamp-train`` console
script.  The configuration root is anchored to the repository root via
``dlamp.const.REPO_ROOT`` so it is independent of the calling working
directory.
"""

import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from dlamp.const import REPO_ROOT
from dlamp.managers import DataManager
from dlamp.models import get_builder
from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import get_standardizer
from dlamp.utils import DataCompose

log = logging.getLogger(__name__)


@hydra.main(
    version_base=None,
    config_path=str(REPO_ROOT / "config"),
    config_name="train_pangu",
)
def main(cfg: DictConfig) -> None:
    """Runs the model training workflow for Pangu (or diffusion) models.

    Args:
        cfg (DictConfig): The Hydra configuration object loaded from
            ``config/train_pangu.yaml`` (override with ``--config-name``).

    Raises:
        RuntimeConfigError: If ``DLAMP_EXP_CODE`` has no matching
            standardization or data config files.
    """
    hydra_oup_dir = Path(hydra.core.hydra_config.HydraConfig.get().runtime.output_dir)
    log.info(f"Working directory: {Path.cwd()}")
    log.info(f"Output directory: {hydra_oup_dir}")

    # lightning ddp strategy doesn't need manual seed
    # https://github.com/Lightning-AI/pytorch-lightning/issues/12986
    # seed_everything(1000)

    # Build runtime config eagerly (validates model code paths)
    runtime_config = RuntimeConfig.from_env()
    # Construct standardizer to load stats + data_list once
    get_standardizer(runtime_config)
    log.info("Runtime config and standardizer initialized.")

    # prevent access to non-existing keys
    OmegaConf.set_struct(cfg, True)

    # prepare data
    data_list = DataCompose.from_config(cfg.data.train_data)
    data_manager = DataManager(data_list, **cfg.data, **cfg.lightning)
    data_manager.setup("test")

    # model
    model_builder = get_builder(cfg.model.model_name)(
        hydra_oup_dir,
        data_list,
        image_shape=data_manager.image_shape,
        add_time_features=cfg.data.add_time_features,
        **cfg.model,
        **cfg.lightning,
    )
    model = model_builder.build_model(data_manager.test_dataloader())

    # trainer
    wandb_logger = model_builder.wandb_logger()
    wandb_logger.watch(model, log="all")
    trainer = model_builder.build_trainer(wandb_logger)

    # start training
    trainer.fit(
        model,
        data_manager,
        ckpt_path=getattr(cfg.lightning, "resume_from_checkpoint", None),
    )


if __name__ == "__main__":
    main()
```

## File: config/data/rwrf_202409.yaml
```yaml
start_time: "2017-06-01 00:00"
end_time: "2022-10-31 00:00"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
add_time_features: False
train_data:
  Z:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa850
    - Hpa925
  T:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa850
    - Hpa925
  U:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa850
    - Hpa925
  V:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa850
    - Hpa925
  Radar:
    - NoRule
```

## File: config/data/rwrf_202412.yaml
```yaml
start_time: "2020-07-01 00:00"
end_time: "2024-08-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [336, 336]
add_time_features: False
train_data:
  Z:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  T:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter2
  U:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter10
  V:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter10
  W:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qv:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
    - Meter2
  Qr:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qs:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qg:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qc:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  Qi:
    - Hpa100
    - Hpa200
    - Hpa300
    - Hpa400
    - Hpa500
    - Hpa600
    - Hpa700
    - Hpa750
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa925
    - Hpa950
    - Hpa975
    - Hpa1000
  RH:
    - Meter2
  Td:
    - Meter2
  SLP:
    - SeaSurface
  SST:
    - SeaSurface
  PSFC:
    - Surface
  PW:
    - Surface
```

## File: config/data/rwrf_202502.yaml
```yaml
start_time: "2020-05-01 00:00"
end_time: "2024-10-31 23:59"
format: "%Y-%m-%d %H:%M"
time_interval: 
  hours: 1
data_shape: [450, 450]
image_shape: [224, 224]
add_time_features: True
use_Kth_hour_pred: 3
train_data:
  Z:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  T:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter2
  U:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter10
  V:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter10
  W:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  Qv:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
    - Meter2
  Qw:
    - Hpa200
    - Hpa500
    - Hpa700
    - Hpa800
    - Hpa850
    - Hpa900
    - Hpa950
    - Hpa1000
  SLP:
    - SeaSurface
  SST:
    - SeaSurface
  PSFC:
    - Surface
  SWDOWN:
    - Surface
  OLR:
    - NoRule
```

## File: config/lightning/diffusion_rwrf_202409.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [6, 2, 2]
  split_method: "sequential"
sampling_rate: 1
batch_size: 1
workers: 16
# LightningModule
regression_onnx_path: null
regressoin_ckpt_path: "./checkpoints/Pangu_240918_013632-epoch=870-val_loss_epoch=0.1731.ckpt"
loss_factor: 10
optim_config:
  name: AdamW
  args:
    lr: 1e-5
lr_schedule:
  name: linear_decay
  args:
    warmup_epochs: 3
    last_epoch: -1
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: null
max_steps: null
min_steps: 1e5 # 100k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
```

## File: config/lightning/pangu_rwrf_202409.yaml
```yaml
# LightningDatamodule
input_len: 1
output_len: 1
split_config:
  ratios: [6, 2, 2]
  split_method: "sequential"
sampling_rate: 2
batch_size: 1
workers: 8 # mpi proc = 32 num_gpus = 8 max_user_processes = 2048
# LightningModule
surface_alpha: 0.25
optim_config:
  name: AdamW
  args:
    lr: 2e-4
    weight_decay: 3e-6
lr_schedule:
  name: cosine
  args:
    warmup_steps: 1000
# lightning.Trainer
num_gpus: null
strategy: "auto"
fast_dev_run: False
max_epochs: null
max_steps: null
min_steps: 5e4 # 50k
limit_train_batches: null
limit_val_batches: null
early_stop_patience: 10
log_image_every_n_steps: 5e3
log_every_n_steps: 50 # default 50
resume_from_checkpoint: null
precision: "bf16-mixed"
```

## File: config/plot/pangu_rwrf.yaml
```yaml
# Settings for time framing.
figure_columns: 25
# Settings for plotting the unalignment gt-grids and pd-grids
grid_spacing:
  ground_truth_m: 2000.0
  forecast_m: 4000.0
# Settings for boundary swapping verification plots
test_bdy:
  # Set to true to generate and save verification plots during inference.
  plot_verification: true

  # The vertical level index to use for the debug plot.
  # For surface data (level=1), this should be 0.
  # For upper air data, it corresponds to the index in the pressure_lv list.
  debug_level_idx: 0

  # The variable/channel index to use for the debug plot.
  # Corresponds to the index in the surface_vars or upper_vars list.
  debug_channel_idx: 6
```

## File: config/train_diffusion.yaml
```yaml
hydra:
  run:  
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

defaults:
  - data: rwrf_202409
  - lightning: diffusion_rwrf_202409
  - model: diffusion_rwrf_202409
  - _self_
  - override hydra/job_logging: default
```

## File: config/train_diffusion_radar.yaml
```yaml
hydra:
  run:  
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

lightning:
  batch_size: 8

model:
  only_radar: True
  hidden_dim: 32

defaults:
  - data: rwrf_202409
  - lightning: diffusion_rwrf_202409
  - model: diffusion_rwrf_202409
  - _self_
  - override hydra/job_logging: default
```

## File: config/train_pangu.yaml
```yaml
# For more default settings and their description, please refer to:
# `../site-package/hydra/conf/__init__.py`
hydra:
  run:  
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S} # where to save the logs
  job:
    chdir: False # whether to move to log folder
  output_subdir: .hydra # .hydra log dir name
  job_logging:
    root:
      level: DEBUG # 1st filter
    handlers:
      console:
        level: INFO # 2nd filter
      file:
        level: DEBUG # 2nd filter
  # verbose: [src.managers.data_manager] 

defaults:
  - data: rwrf_202502
  - lightning: pangu_rwrf_202502
  - model: pangu_rwrf_202502
  - _self_
  - override hydra/job_logging: default # default/disabled/custom
```

## File: config/inference/pangu_rwrf_ckpt.yaml
```yaml
infer_type: "ckpt"
best_ckpt: "./checkpoints/Pangu_250310_214141-epoch=584-val_loss_epoch=0.3980.ckpt"
bdy_swap_method:
  name: "linear"
  n_of_grid: 44
output_itv:
  hours: 4
# Number of feedback iterations (used by predict_feedback.py only).
# null = disabled; set to a positive int for two-way feedback.
feedback_iters: null
```

## File: config/predict.yaml
```yaml
hydra:
  run:  
    dir: outputs/${now:%Y-%m-%d}/${now:%H:%M:%S}
  job:
    chdir: False
  output_subdir: .hydra
  job_logging:
    root:
      level: DEBUG
    handlers:
      console:
        level: INFO
      file:
        level: DEBUG

data:
  use_Kth_hour_pred: null

lightning:
  sampling_rate: 1
  batch_size: 1 # must be 1 !!!
  workers: 4

defaults:
  - data: rwrf_20250729
  - lightning: pangu_rwrf_20250729
  - model: pangu_rwrf_20250729
  - inference: pangu_rwrf_onnx
  - plot: pangu_rwrf
  - _self_
  - override hydra/job_logging: default # default/disabled/custom
```

## File: predict.py
```python
"""Repository-root wrapper delegating to the ``dlamp-predict`` entry point.

Usage::

    python predict.py
"""

import sys

from dlamp.analysis.prediction import main

if __name__ == "__main__":
    sys.exit(main())
```

## File: config/inference/pangu_rwrf_onnx.yaml
```yaml
infer_type: "onnx"
onnx_path: "./export/Pangu_model_20250729.onnx"
bdy_swap_method:
  name: "exp_decay"
  n_of_grid: 10
output_itv:
  hours: 1
gpu_id: 0
# Number of feedback iterations (used by predict_feedback.py only).
# null = disabled (one-way downscaling); set to a positive int for feedback.
feedback_iters: null
```

## File: train.py
```python
"""Repository-root wrapper delegating to the ``dlamp-train`` entry point.

Usage::

    python train.py
    python train.py --config-name train_diffusion
"""

import sys

import dlamp.train

if __name__ == "__main__":
    sys.exit(dlamp.train.main())
```
