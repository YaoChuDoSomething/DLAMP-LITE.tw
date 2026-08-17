# DLAMP Canonical Variable Registry — Handoff Document

**Purpose**: Define a canonical registry for weather/Microphysical variables that maps between:
- Enum member names (internal Python identity)
- short_name (encoder/decoder/dataloader mapping)
- nc_key (NetCDF variable key in source files)
- CF standard_name (cross-ecosystem semantic)
- WRF adapter key (for WRF output generation)

This document captures all design decisions from the design session and lists pending items for the next agent.

---

## 1. Current Design Decisions (Agreed)

### 1.1 Variable Renaming Table

| Canonical Role | Old Name | New Name | CF standard_name | CF units | Notes |
|----------------|----------|----------|------------------|----------|-------|
| **XLAT** (Latitude) | `Lat` | `XLAT` | `latitude` | degree_north | enum member + short_name + nc_key all `XLAT` |
| **XLON** (Longitude) | `Lon` | `XLON` | `longitude` | degree_east | enum member + short_name + nc_key all `XLON` |
| **TH** (Potential Temperature) | `TK` | `TH` | `air_potential_temperature` | K | Requires θ = T·(p₀/p)^(R/cp) conversion; p₀=1000 hPa, R/cp≈0.286 |

### 1.2 Key Design Principles

- **enum member / short_name / nc_key**: All use the canonical names `XLAT`/`XLON`/`TH`. These are **self-defined** names for this codebase; they happen to coincide with WRF's `XLAT`/`XLONG` 2D field names, but the canonical identity is independent of WRF's implementation.
- **CF standard_name**: Provides the shared semantic that resolves integration conflicts across ecosystems (e.g., WRF vs ERA5 vs GFS). `latitude`/`longitude` / `air_potential_temperature` are the canonical CF names.
- **WRF adapter mapping**: The WRF adapter layer maps our canonical keys to WRF's actual variable names:
  - `XLAT` ↔ `XLAT` (identity, no translation needed)
  - `XLON` ↔ `XLONG` (our `XLON` → WRF's `XLONG`)
  - `TH` → computed from `T` + `P` via θ = T·(p₀/p)^(R/cp) (no existing `th_p` field in source data)

### 1.3 Alias / Legacy Mapping (Backward Compatibility)

All legacy config keys, stats keys, and `from_config` calls must be mapped through an alias layer:

| Legacy Key | Canonical Key | Action |
|------------|---------------|--------|
| `Lat` → `XLAT` | config `{"Lat": [...]}` → `{"XLAT": [...]}` | alias layer or pre-processing |
| `Lon` → `XLON` | config `{"Lon": [...]}` → `{"XLON": [...]}` | alias layer or pre-processing |
| `TK` → `TH` | config `{"TK": [...]}` → `{"TH": [...]}` | alias layer or pre-processing |
| `tk_p` → `th_p` (if preprocessed TH files exist) | stats/adapter I/O | may need new conversion pipeline |

### 1.4 Code Locations Affected

| File | Current State | Required Change |
|------|---------------|-----------------|
| `src/dlamp/utils/data_type.py:38-39` | `Lat=("Latitude","LAT","XLAT")`, `Lon=("Longitude","LON","XLONG")` | Rename enum members to `XLAT`/`XLON` (already are), add `short_name` field if needed |
| `src/dlamp/utils/data_type.py` | No `short_name` field currently | Add `short_name` attribute to `DataType` (and `Level` if applicable) |
| `src/dlamp/utils/data_compose.py:30` | `if self.var_name in [DataType.Radar, DataType.Lat, DataType.Lon]` | Works as-is since `Lat`/`Lon` already match |
| `src/dlamp/analysis/netcdf_meta.py:25-32` | Has `"XLAT"` and `"XLONG"` in `VARIABLE_ATTRIBUTES` | Add `air_potential_temperature` entry (or rename `tk_p` → `th_p` with new CF name) |
| `src/dlamp/analysis/forecast_saver.py:205-206` | Writes `XLAT`, `XLONG` 2D fields | Already uses `XLAT`/`XLONG`; no change needed if nc_key stays `XLAT`/`XLON` |
| `src/dlamp/generate_const_masks.py:27,89` | `DataCompose.from_config({"Lat": ["NoRule"], "Lon": ["NoRule"]})` | Update to `{"XLAT": [...], "XLON": [...]}` or alias |
| `src/dlamp/analysis/prediction.py:110` | `{"Lat": ["NoRule"], "Lon": ["NoRule"], "MASK": ["NoRule"]}` | Update to `{"XLAT": [...], "XLON": [...]}` or alias |
| `externals/dlamp-data/src/registry/diagnostic_functions.py:86-108` | `diag_tk_p` uses `nc_key="tk_p"` | Change to `th_p` or add `diag_th_p` with θ conversion |
| `externals/dlamp-data/src/preproc/dlamp_regridder.py:80-81` | `self.XLONG = tgtds[self.tgtlon].values`; `self.XLAT = tgtds[self.tgtlat].values` | Already uses `XLAT`/`XLONG` as tgtlon/tgtlat keys; consistent |
| `dlamp/config/...` (rwrf configs) | `{"Lat":["NoRule"],"Lon":["NoRule"]}` patterns | Update to `{"XLAT":["NoRule"],"XLON":["NoRule"]}` or alias |

### 1.5 Pending Clarifications (Hold Points)

| Question | Context | Options |
|----------|---------|---------|
| **TH adapter key & conversion** | `DataType.TK` currently has `nc_key="tk_p"`. If changed to `TH` with CF `air_potential_temperature`, what is the new `nc_key`? Do we: (a) compute θ = T·(p₀/p)^(R/cp) on-the-fly from `T` + `P` in the adapter, or (b) expect preprocessed `th_p` files? | (a) No preprocessed TH needed; adapter computes θ from `tk_p` + pres_levels. (b) Requires new preprocessed data source. |
| **WRF adapter `TH` key** | ForecastSaver uses `var_type.name_{level_type.nc_key}hPa` pattern (line 110). If `nc_key` changes from `tk_p` to `th_p`, the output variable name changes from `TK_Hpa500` to `TH_Hpa500`. Is this desired? | Yes (canonical rename) / No (keep `TK` as output name). |
| **short_name field** | Should `DataType` carry a `short_name` separate from `nc_key` and `name`? `short_name` maps to encoder/decoder/dataloader; `nc_key` is the NetCDF key; `name` is the description. | Add `short_name` / keep single field. |

### 1.6 Suggested Implementation Order

1. **Add `short_name` field to `DataType` enum** (and `Level` if applicable). This is the foundational change enabling encoder/decoder mapping.
2. **Rename `Lat` → `XLAT`, `Lon` → `XLON`** in `DataType` enum (already done in code; verify config/alias mappings).
3. **Add `TH` enum member** replacing `TK`, with `nc_key="th_p"`, `short_name="TH"`, `cf_standard_name="air_potential_temperature"`.
4. **Implement TH→θ conversion in source adapters** (`externals/dlamp-data/src/registry/diagnostic_functions.py:diag_tk_p` → add `diag_th_p` or modify to compute θ from `T` + `P`).
5. **Update alias layer** for config `Lat`/`Lon`/`TK` → `XLAT`/`XLON`/`TH`.
6. **Update all `from_config` calls** and legacy config patterns.
7. **Update `VARIABLE_ATTRIBUTES`** in `netcdf_meta.py` if needed.
8. **Test** with `python -m pytest src/dlamp/models/architectures/unet_test.py` etc.

### 1.7 Files to Modify (Comprehensive List)

```
src/dlamp/utils/data_type.py            # Add short_name to DataType/Level
src/dlamp/utils/data_compose.py        # May need short_name usage
src/dlamp/analysis/netcdf_meta.py      # Add air_potential_temperature entry
src/dlamp/analysis/forecast_saver.py   # Verify variable naming with TH
src/dlamp/generate_const_masks.py      # Update Lat/Lon → XLAT/XLON in from_config
src/dlamp/analysis/prediction.py       # Update Lat/Lon → XLAT/XLON
externals/dlamp-data/src/registry/    # Add diag_th_p or modify diag_tk_p
externals/dlamp-data/src/preproc/     # May need th_p preprocessing
dlamp/config/...                        # Update rwrf_*.yaml configs
```

### 1.8 Verification Commands (when ready)

```bash
# Run existing tests (note: most tests are broken per AGENTS.md, but these work)
python -m pytest src/dlamp/models/architectures/{glide_unet,unet,earth_3d_specifics}_test.py

# Verify DataType enum values
python -c "from dlamp.utils.data_type import DataType; [print(f'{d.name}: desc={d.value}, code={d.code}, nc_key={d.nc_key}') for d in DataType]"

# Check DataCompose with new variables
python -c "
from dlamp.utils.data_type import DataType
from dlamp.utils.data_compose import DataCompose
from dlamp.utils.data_generator import DataGenerator
# Test XLAT/Lon/TH creation
dc = DataCompose(DataType.XLAT, Level.NoRule)
print(f'XLAT combined_key={dc.combined_key}, str={dc}')
dc2 = DataCompose(DataType.TH if hasattr(DataType, 'TH') else DataType.TK, Level.NoRule)
print(f'TK/TH combined_key={dc2.combined_key}, str={dc2}')
"
```

---

## 2. Next Session Focus

The next agent should:

1. **Resolve the TH adapter key question** — decide whether θ conversion happens in-adapter (compute from T+P) or requires preprocessed `th_p` files, and set the corresponding `nc_key` in `DataType`.
2. **Add `short_name` field to `DataType`** enum, following the pattern `code` + new `short_name`. Update all references.
3. **Rename `Lat` → `XLAT`, `Lon` → `XLON`** enum members (already in code; verify consistency across all files).
4. **Add `TH` enum member** with `nc_key="th_p"`, `short_name="TH"`, `cf_standard_name="air_potential_temperature"`.
5. **Update alias/mapping layer** for config `Lat`/`Lon`/`TK` → canonical names.
6. **Update all `from_config` calls** and legacy references across the codebase.
7. **Update `VARIABLE_ATTRIBUTES`** if `tk_p` is renamed to `th_p` or new `air_potential_temperature` entry added.
8. **Run verification** to ensure no breakage.

---

## 3. Suggested Skills for Next Agent

The following skills are relevant for continuing this work:

- **implement** — for making the actual code changes (adding enum members, fields, updating aliases)
- **systematic-debugging** — for diagnosing any breakage when enum names change across the codebase
- **research** — for verifying CF standard name `air_potential_temperature` conventions and any needed pressure-conversion formulas
- **question** — for confirming decisions with the user (especially the TH adapter key question)
- **tdd** / **tdd-workflows** — if the team wants test-driven development for the registry changes (note: existing tests are largely broken per AGENTS.md, but the working test pattern is `python -m pytest src/dlamp/models/architectures/*_test.py`)

If the next agent needs to fetch up-to-date CF documentation, they can use the Context7 skill to look up `air_potential_temperature` standard name details.

---

*End of handoff document.*