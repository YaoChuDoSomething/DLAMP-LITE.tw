# Codebase Review — `externals/fcn-regpgw/`

**Scope:** full review of `externals/fcn-regpgw/` — external, **untracked** content
(`git status` shows `?? externals/fcn-regpgw/`; the 4 `.ipynb` notebooks are gitignored via
`*.ipynb`). Contents: `modAFNO_test/` (user driver `inference.py`, vendored NVIDIA
`modAFNO_model/*`, modified `inference_helper.py`), 4 coupling notebooks, 2 pptx.
**Method:** two axes — **Standards** (repo rules where they apply + Fowler smell baseline)
and **Spec** (no formal PRD; de-facto spec = the 4 notebooks' stated FCNv2/RegPGW/FCNV1
coupling flows). Key claims re-verified against source.

---

## Standards

### Hard

- **`safe_members` filter is inverted (security)** — `inference.py:13-24`. It `yield`s a
  member when `".." in name OR os.path.isabs(name) OR realpath(join(local_path,name)).startswith(realpath(local_path))` —
  so path-traversal (`../evil`) and absolute-path members are **extracted**, not skipped;
  only members *outside* the target dir are skipped. Correct predicate:
  `not (".." in name or isabs(name)) and realpath(...).startswith(realpath(local_path))`.
  Additionally `startswith` is a substring match (`model_weight_evil` passes) — use
  `os.path.commonpath`.
- **`@staticmethod` at module level** — `inference.py:12`; not inside a class, does nothing.
- **`torch.load` without `weights_only`** — `inference.py:40`; pickle RCE vector on torch 2.4.
- **Hardcoded absolute path** — `inference.py:82` `/wk2/yungyun/code_space/FCNV2_test/...`
  (someone else's home dir; won't exist on this box).
- **Top-level script, no `__main__` guard** — importing `inference` runs the whole pipeline.
- **`# ignore_header_test` leftover** — `inference_helper.py:1`.

### Judgement — hygiene + smells

- **Not runnable as-shipped:** `modAFNO_weight/` missing (`inference.py:10,93-97` references
  `fcinterp-modafno-2x2.mdlus`, `model.pt`, `global_means/stds.npy`, `land_sea_mask.nc`,
  `orography.nc` — none present). 73 MB + 16 MB pptx untracked in the tree.
- **Duplicated Code:** 720/1440 lat-lon meshgrid rebuilt in `inference_helper.py:54-57` and
  `inference.py:74-77`; the ~41-line plotting cell is verbatim across all 4 notebooks
  (oneway/2way/v1/v2 differ only in weight download, predict command, IC time —
  oneway `2025110900` vs others `2025072400`); `modafno.py` `ModAFNO2DLayer`/`Block`
  near-verbatim copies of `afno.py` (and a real divergence: `total_modes = H//2+1` in
  `afno.py:171` vs `min(H,W)//2+1` in `modafno.py:218`).
- **Repeated Switches:** `scale_shift_mode` if/elif in both `afno.py`/`modafno.py`; `method`
  string switched twice in `ModEmbedNet` (`modembed.py`).
- **Primitive Obsession:** `embed_model={...}` dict config in `inference.py:49-51`.
- **Dead code:** `compute_sza` (`inference_helper.py:80`), `irradiance`/`toa_*` unused;
  `files`/`os.listdir` at `inference.py:83-84` never used; debug `print(t)` at
  `inference_helper.py:90`; `timezone` imported unused at `inference.py:4`.
- **Mysterious Name:** `dtype` module-global in `inference_helper.py`.
- **Stale artifacts:** `__pycache__/cpython-310.pyc` present (repo is Python 3.11).
- **Notebook reproducibility:** notebooks pull `/content/couple_model` (scripts + weights)
  from Colab/gdown — not reproducible from this repo; the 2-way notebook never executed
  (`execution_count` all `None`).

---

## Spec (de-facto = the 4 notebooks)

The notebooks implement FCNv2 autoregressive forecasting + RegPGW one-way / two-way coupling
+ FCNV1 precip coupling (cells call `inference_FCNV2.py`, `inference_PGW_one_way_test.py`,
`inference_PGW_two_way_test.py`, `inference_precip_v1/v2.py`, and flip lat with
`np.flip(IC_data, axis=1)`).

### (a) Missing / partial vs notebooks

- `modAFNO_test/inference.py` implements **ModAFNO "fcinterp" temporal interpolation** — a
  model referenced in **zero** of the four notebooks (keyword scan: no
  `modAFNO`/`fcinterp`). It is neither FCNV2 autoregressive, nor PGW one-way, nor two-way
  (which re-injects PGW→FCNV2 each step), nor precip v1/v2. No regional/PGW model, no
  boundary re-injection, no lat flip.
- Data assets absent: entire `modAFNO_weight/` dir missing; hardcoded input
  `/wk2/yungyun/.../output_IFS_2025072400` unreachable.

### (b) Not asked for (scope creep)

- Entire ModAFNO driver is extraneous to the notebook flows: tar-extraction + `safe_members`
  wrapper, 3-channel cos-zenith + static channel stack, hourly `intro_i`/`t_norm`
  interpolation grid (6 outputs per 6 h pair).

### (c) Implemented but wrong

1. **`inference.py:74-78`** — `sincos_latlon = np.sin/cos(grid)` on **degrees**, no
   `deg2rad`; static features are corrupted on every forward pass. The same file's helper
   `cos_zenith_angle` does it right (`inference_helper.py:130-131` uses `np.deg2rad`), and
   `cos_zenith` (`inference_helper.py:53`) correctly hands degrees to it — the inline
   `sincos_latlon` path does not.
2. **`inference.py:105/110` vs `:131`** — reads unpadded `output_weather_0h.npy`, writes
   3-digit-padded `output_weather_000h`; self-inconsistent. Loop at `:103` iterates
   `range(len(files))` over arbitrary folder contents and reads `(len)*6h` at the last `i`
   (off-by-one / name-drift risk).
3. **`inference.py:107-108,112-113`** — RH→q converted pre-standardization, but the
   de-standardized output is saved as **q in RH-named channels** (notebook cell 8 ordering
   `r50..r1000`); no inverse q→RH. T/RH index hardcodes (`47:60`/`60:73`) assume that
   ordering.
4. **`inference.py:116-132`** — `intro_i=0` rewrites anchor time t0 already present as input;
   `model.to(device)` + `model.eval()` inside the per-intro loop; `out.detach().numpy()`
   without `.cpu()` breaks on non-CPU devices.
5. Channel math itself reconciles (73+73+3+6=155; de-std `out*scale+center` matches the std
   direction); `rh_to_q` formula/units correct.

---

## Improvement plan (ranked)

1. **Fix `safe_members` inversion** (`inference.py:13-24`) and add `weights_only=True` to
   `torch.load` — security.
2. **`deg2rad` before the sincos static features** (`inference.py:78`) — corrupts every
   forward pass otherwise.
3. **Decide what this directory is for**: implement the notebook flow (FCNV2 + PGW one/two-way
   coupling, incl. lat flip + boundary re-injection) or keep the ModAFNO interpolation as a
   separate experiment — right now `inference.py` matches neither the notebooks nor any spec.
4. **Parametrize paths/device/IC** via CLI args or config; drop `/wk2/yungyun`; unify
   read/write filenames and drive the loop from an actual lead-time file list.
5. **Make it runnable/reproducible**: commit `modAFNO_weight/` (or a fetch script), add a
   README, add a `__main__` guard, move `.to(device)`/`.eval()` out of the loop, add `.cpu()`
   before `.numpy()`.
6. **Dedupe notebooks** (shared plotting cell; unify IC time) and either vendor or clearly
   fork the NVIDIA model files (the `total_modes` divergence in `afno.py` vs `modafno.py`
   needs a decision).
7. **Track it**: the directory is entirely untracked and notebooks gitignored — nothing is
   version-controlled.

**One-line summary:** Standards — 5 hard + ~10 judgement findings, worst = inverted
`safe_members` tar filter (security) + un-runnable/un-tracked dir; Spec — ModAFNO driver
matches none of the 4 notebook flows (missing + scope-creep), worst = degree-units `sincos`
corrupting static features + read/write filename mismatch.