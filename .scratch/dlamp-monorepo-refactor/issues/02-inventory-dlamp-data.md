# 02 Inventory DLAMP.data layout

Type: research
Status: resolved
Blocked by:

## Question

Read `/wk2/yaochu/main/dlamp/externals/dlamp-data` — the **nested git repo** embedded in DLAMP.tw (remote `https://github.com/YaoChuDoSomething/dlamp.data.git`, branch `main`, 55 commits). This is the DLAMP.data source for the monorepo effort (redirected from `github/dlamp-data` by the user). Produce a markdown inventory — linked as an asset in this issue's resolution — that documents:

- `src/` components: `src/core/` (context, pipeline), `src/dlamp/data`, `src/dlamp_data/` (the installable package), `src/io/` (netcdf4_reader/writer, hdf5_writer, zarr_writer, channel_assembler, adapters), `src/registry/` (channel_definitions, channel_registry, diagnostic_functions, diagnostic_registry), `src/tasks/` (convert, diagnostics, download, regrid, satellite_processor), `src/tools/` (meta_refine).
- `definition/` (variable_spec.md, metadata_template.json), `config/`, `docs/` (channel_registry_api.md, plans/, testing_specification.md), `oop_structure_doc.md`, `scripts/`, top-level `main.py` / `dlamp_prep.py`.
- The **test suite** (`test/`): the ~29 tests and their fixtures (`test/fixtures/*.nc`, `test_config.yaml`, `generate_fixtures.py`), how they run (pytest config, python version — the pycache shows 3.11 and 3.12).
- The dependency list from `pyproject.toml` / `uv.lock` (netcdf4, h5py, zarr, cdo, xarray, etc.).
- Which components talk to each other (pipeline → tasks → registry/io), and which are externally-facing CLI/tools.

Also capture git facts: branch/history shape, LFS or fixture size considerations for `test/fixtures/*.nc`.

Output: an inventory markdown doc (path recorded in the resolution comment) that tickets 03 and 06 consume to map components into `dlamp.data.*` and to plan the merged dependency set.

## Answer

Inventory: `assets/02-dlamp-data-inventory.md`.

Key finding: the ticket's assumed layout belongs to the other copy (`github/dlamp-data`). The nested repo is a **separate ERA5/SFNO preprocessing pipeline** — `src/preproc/` (CDS downloader, regridder, SFNO processor) + `src/registry/` (31 diagnostic functions, importlib loader, dependency-sorted execution), driven by `config/{era5,sfno,dataDownloader}.yaml` and runners `DLAMPreproc.py`/`SFNOPreproc.py` (no `[project.scripts]`; run from repo root). 55 commits, flat mainline + sfno feature branches; no tests; no LFS; `target.nc`/`uv.lock` gitignored; Python 3.12 (conflicts with DLAMP.tw 3.11 pin).

Consequences:
- `src/preproc/*` → `dlamp.data.{download,regrid,sfno}`, `src/registry/*` → `dlamp.data.registry`; runners are the `[project.scripts]` candidates.
- Merged deps must reconcile uv pyproject (`earth2studio[data,sfno]` git) vs `requirements.txt` (CDS stack) vs DLAMP.tw pins; `cdo`/`eccodes` are conda-only.
- Output naming is a contract with DLAMP.tw: `e5dlamp_%Y%m%d_%H%M.nc` ↔ `src/utils/file_util.py:209`; `sfnodlamp`/`e2s_sfno_dlamp` ↔ `file_util.py:214`.
- **Open gap (escalate to ticket 03):** the channel-registry/io/tasks/tools layer + its ~29 tests exist only in `github/dlamp-data` (redirected away). Needs a human decision on where that layer actually lives.
