# 02 — DLAMP.data layout inventory

Source: `/wk2/yaochu/main/dlamp/externals/dlamp-data` (the **nested git repo** inside DLAMP.tw)
Inventory date: 2026-08-12
Status: feeds tickets 03 (submodule tree), 06 (dependency merge)

## TL;DR — divergence from the ticket's assumed layout

Ticket 02's Question describes a layout (`src/core/`, `src/dlamp/data`, `src/dlamp_data/`, `src/io/` with netcdf4/hdf5/zarr writers + channel_assembler + adapters, `src/tasks/` incl. satellite_processor, `src/tools/meta_refine`, `definition/`, `test/` with ~29 tests + fixtures, `uv.lock`) **that does not exist in this repo**. That layout matches the *other* copy, `github/dlamp-data` (uppercase `DLAMP.data` @ `dev`), which the user explicitly redirected away from.

What actually lives in the nested repo is a **separate, self-contained ERA5/SFNO preprocessing pipeline**: CDS download → regrid → diagnostic-variable registry, plus an SFNO-global-forecast stage. It has **no tests, no installable package source, no io/tasks/tools layers, no definition/ docs**.

Consequence for the effort: **the channel-registry / io / tasks layer of DLAMP.data has no inventoried source yet.** Either it lives only in `github/dlamp-data` (out of scope per redirect), or it must be found elsewhere. Flag for ticket 03 disposition and the map's Source-repos notes.

## Repository snapshot

- Git remote: `https://github.com/YaoChuDoSomething/dlamp.data.git` (lowercase), local branch `main`, **55 commits**.
- Remote branches: `main`, `dev`, `001-module-workflow-spec`, `features/sfno`, `sfno_pipes`.
- History shape: flat mainline (`git log` shows mostly `Add files via upload` + incremental `Update *` commits); no merge-heavy structure; SFNO work is the tip (`Implement SFNO Flows Start`).
- No Git LFS in use. `assets/target.nc` is a 4.9 MB plain file and is **gitignored** (local-only); `uv.lock` is also gitignored.
- Python: `.python-version` = **3.12**; `pyproject.toml` declares `requires-python = ">=3.12"` — conflicts with DLAMP.tw's pin to 3.11 (already in the map's fog).

## File tree (complete, 22 files)

```
.
├── DLAMPreproc.py            # ERA5 pipeline runner (flags-gated workflow)
├── SFNOPreproc.py            # SFNO pipeline runner (staged workflow + argparse)
├── main.py                   # uv "hello from dlamp-data" stub
├── updated.py                # enhanced diagnostic-functions module (multi-source)
├── README.md                 # primary docs (ERA5 pipeline, registry mechanism)
├── README.SFNO.md            # SFNO integration docs
├── LICENSE
├── pyproject.toml            # uv; name dlamp-data; earth2studio git dep
├── requirements.txt          # ERA5-pipeline deps (CDS/cdo stack)
├── .python-version           # 3.12
├── .gitignore                # standard; adds target.nc + uv.lock
├── assets/
│   ├── search_keyword.sh     # grep helper over ERA5 GRIB
│   ├── target.nc             # (gitignored, 4.9MB) regrid target grid
│   └── validate_vars.py      # ad-hoc ERA5 vs RWRF vs dlamp output comparison
├── config/
│   ├── era5.yaml             # ERA5 pipeline config (download/regrid/registry)
│   ├── sfno.yaml             # SFNO pipeline config
│   └── dataDownloader.yaml   # older/standalone downloader-only config
└── src/
    ├── preproc/
    │   ├── cds_downloader.py     # CDSDataDownloader
    │   ├── dlamp_regridder.py    # DataRegridder
    │   └── sfno_processor.py     # SFNODataProcessor (earth2studio)
    └── registry/
        ├── diagnostic_functions.py   # 31 diagnostic functions + helper
        └── diagnostic_registry.py    # loader + dependency sort
```

## Component inventory

### Top-level scripts (workflow runners — the repo's real entry points)

- **`DLAMPreproc.py`** — ERA5 workflow: boolean flags `do_cds_downloader` / `do_dlamp_regridder`; builds `CDSDataDownloader` from `config/era5.yaml`, then `DataRegridder` (regrid + diagnostics). Run from repo root; imports are `from src.preproc...`.
- **`SFNOPreproc.py`** — SFNO workflow with `argparse`, staged: (1) `run_sfno_forecast` (earth2studio SFNO, GFS/CDS initial conditions), (2) `convert_sfno_format` → ERA5-like naming, (3) `run_regridding_and_diagnostics` (reuses the same `DataRegridder`), (4) `initialize_feedback_interface` — explicitly marked *future / two-way coupling stub*.
- **`updated.py`** — standalone enhanced diagnostic-functions module supporting `ERA5` / `ERA5_r` / `RWRF` / `SFNO` source-specific naming + unit conversion. Overlaps `src/registry/diagnostic_functions.py` (likely a newer iteration, not wired into the runners).
- **`main.py`** — uv-generated placeholder, no logic.

### `src/preproc/`

- **`cds_downloader.py`** → `CDSDataDownloader(yaml_path)`: loads CDS API config (era5.yaml `download:` section: area box ~lat 17–31, lon 114–128), downloads reanalysis pressure-level + single-level data, uses `cdsapi` + `cdo`; writes `era5pl_*` / `era5sl_*` GRIB/netCDF to `./ncdb/Pool`.
- **`dlamp_regridder.py`** → `DataRegridder`: the pipeline core. Builds timeline from time_control, regrids horizontally (`scipy.interpolate.griddata`, `linear`, with a `_interpolate_with_fallback`), interpolates vertical levels, copies static vars (XLONG/XLAT/HGT/LANDMASK) from the target grid (`assets/target.nc`), then runs diagnostics via `src.registry.diagnostic_registry`. Writes `e5dlamp_<timestr>.nc`. Methods: `build_timeline`, `gen_io_filename`, `interp_horizontal`, `interp_horizontal_v2`, `process_single_time`, `main_process`.
- **`sfno_processor.py`** → `SFNODataProcessor`: wraps `earth2studio` (`fetch_data`, `map_coords`, `to_time_array`, models.px `SFNO`); runs 6-hourly global forecast, converts to ERA5-like split files (`sfnopl_*`/`sfnosl_*`).

### `src/registry/`

- **`diagnostic_functions.py`** — 31 `diag_*` functions (+ `_create_dataarray` helper and `sat_vapor_pressure_water`): `z_p, tk_p, umet_p, vmet_p, QVAPOR_p, QRAIN_p, QCLOUD_p, QSNOW_p, QICE_p, QGRAUP_p, QTOTAL_p, wa_p`, 2 m (`T2, Q2, rh2, td2`), 10/100 m wind (`umet10, vmet10, umet100, vmet100`), `slp, SST, PSFC, pw, PBLH, RAINNC, SWDOWN, OLR, REFL, MAX_REFL`. Each takes `(source_dataset: str, ds: xr.Dataset) -> xr.DataArray`, using `source_dataset` to pick source-specific variable names/unit handling.
- **`diagnostic_registry.py`** — `load_diagnostics(yaml_path)`: reads `config/era5.yaml` `registry:` section, `importlib`-loads each `function:` name; `sort_diagnostics_by_dependencies`: topological sort over `requires:` lists (outputs of one diagnostic feed others). This is the extension mechanism README documents.

### `config/`

- **`era5.yaml`** — sections: `share` (exp_code `E5_FANAPI`, data_path `${DATA_PATH}`, time_control start/end, io_control with `base_dir: /wk2/yaochu/DLAMP_model/DLAMP.data/` and `prefix.output = e5dlamp`), `download` (area box, `reanalysis-era5-pressure-levels`, levels 1000→30), `regrid` (target_nc, adopted_varlist), `registry` (source_dataset `ERA5`, varname list).
- **`sfno.yaml`** — same `share` shape (exp_code `SFNO_FANAPI`), `sfno:` model config (initial_condition_source `GFS`, model_step_hours 6, output_variables), prefix.output `sfnodlamp`.
- **`dataDownloader.yaml`** — older standalone downloader config (no registry/regrid section). Likely superseded by era5.yaml.

### `assets/`

- `target.nc` (gitignored) — the regrid target grid (RWRF-style XLAT/XLONG/pres_levels).
- `search_keyword.sh` — grep helper for ERA5 GRIB metadata.
- `validate_vars.py` — ad-hoc comparison of `era5sl_*` vs RWRF `wrfinput_d01_*_interp` vs `e5dlamp_*`.

## Dependencies

`pyproject.toml` (uv):
- `name = "dlamp-data"`, `version = "0.1.0"`, `requires-python = ">=3.12"`
- deps: `earth2studio[data,sfno]` (git `NVIDIA/earth2studio`, rev `0.9.0`), `pip>=25.3`
- `[tool.uv.sources]` pins the earth2studio git source.
- No `[project.scripts]` / build-system for an installable package — run from repo root.

`requirements.txt` (ERA5 pipeline stack): `pyyaml, cdsapi, xarray, cftime, cfgrib, matplotlib, numpy, scipy, pandas, netCDF4, eccodes, pyproj`.

Cross-cutting: **two overlapping dep specs** (uv pyproject for the SFNO stage, requirements.txt for the CDS stage); no lockfile committed. `cdo` is needed via conda (README install instructions) but absent from requirements.txt.

## Tests

**None.** No `test/` directory, no pytest config, no fixtures. (The ~29-test suite + `test/fixtures/*.nc` + `generate_fixtures.py` described in the ticket belong to `github/dlamp-data`, not here.)

## Integration surface with DLAMP.tw

- Output naming is a **contract**: config `prefix.output = e5dlamp` matches `src/utils/file_util.py:209` `e5dlamp_%Y%m%d_%H%M.nc` for `OP_ERA5`; the SFNO pipeline's `sfnodlamp` corresponds to the `e2s_sfno_dlamp_*` pattern (`src/utils/file_util.py:214`, `OP_E2S`, and `src/const.py:15` default `DLAMP_DATA_SOURCE=OP_ERA5`).
- Data handoff via `DLAMP_DATA_PATH` (default `/wk2/yaochu/CASE_DATA/Pool/`); regridded output goes to `./ncdb/Pool`.
- README "Condition 2" documents the experimental combined env: DLAMP.tw + DLAMP.data + physicsnemo on Python 3.11 (`python-eccodes`, `python-cdo`), `hydra-core --upgrade`, `onnxruntime-gpu==1.20.0` — the DLAMP.tw runtime dependency set this pipeline feeds.

## What tickets 03 / 06 should consume

- Map `src/preproc/*` → `dlamp.data.preproc` (or fold as `dlamp.data.{download,regrid,sfno}`); `src/registry/*` → `dlamp.data.registry`.
- The runner scripts (`DLAMPreproc.py`, `SFNOPreproc.py`) are the `[project.scripts]` candidates for the data side.
- Merged dep set must reconcile: uv pyproject (earth2studio git) vs requirements.txt (CDS stack) vs DLAMP.tw pins (`numpy<2.0`, `torch==2.4.0`, py3.11). `cdo`/`eccodes` are conda-only.
- **Gap to resolve (ticket 03):** where is the channel-registry/io/tasks/tools layer and its tests? Not in this repo, not to be read in `github/dlamp-data` per redirect. Candidate answers: (a) that layer is a *future* design not yet implemented anywhere; (b) it lives in an unexamined copy (e.g. `worktree/`, upstream forks); (c) the nested repo + a different source are meant to be reconciled in the monorepo. Needs a human decision.
