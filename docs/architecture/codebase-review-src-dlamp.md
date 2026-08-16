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