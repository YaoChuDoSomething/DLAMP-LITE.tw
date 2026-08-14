# DLAMP Deep Modules Design

## 1. Overview

This document outlines the deep-module design principles as they apply to the dlamp codebase, with specific references to the variable-registry redesign in progress. The aim is to achieve **depth** (small interface, large behaviour behind it), **locality** (changes concentrate in one place), and **testability** (testing natural through the interface).

---

## 2. Current State: Variable Registry as a Deep Module

The canonical variable registry (`DataType` enum + `DataCompose` + adapter layer) is the primary candidate for deep-module restructure in this session.

### 2.1 Desired Deep Shape

```
┌─────────────────────┐
│   Small Interface   │  ← DataType enum, DataCompose.get_combined_key(),
│                     │     DataCompose.from_config, alias mapping
├─────────────────────┤
│                     │
│  Deep Implementation│  ← nc_key resolution, CF-standard-name lookup,
│                     │     TH→θ conversion, WRF adapter mapping,
│     source_adapters, preproc, config aliases
│                     │
└─────────────────────┘
```

**Interface (small):**
- `DataType` enum members with `code`, `nc_key`, `description`
- `DataCompose` — `var_name`, `level`, `combined_key`, `basename`, `get_combined_key()`, `from_config()`
- Alias layer: `legacy_name → canonical_name` mapping

**Implementation (deep, hidden):**
- CF standard-name resolution (`air_potential_temperature`, `latitude`, `longitude`)
- TH potential-temperature conversion: θ = T·(p₀/p)^(R/cp), p₀=1000 hPa
- WRF adapter key mapping: our `XLON` → WRF's `XLONG`
- Source adapter diag functions (`diag_tk_p`, future `diag_th_p`)
- Preproc regridder target-grid lookup (`XLAT`/`XLONG`)
- Config alias mapping (rwrf_YYYYMMDD.yaml `Lat`/`Lon`/`TK` → canonical)

### 2.2 Depth Benefits

| Caller / Test | What they see (interface) | What's hidden (implementation) |
|----------------|---------------------------|--------------------------------|
| `DataCompose.from_config({"TK": [...]})` | Enum member `TK`, level list, combined_key string | Whether `nc_key` is `tk_p` or `th_p`; θ conversion formula; adapter key mapping |
| Test of `get_combined_key()` | Returns `tk_p` or `th_p` depending on `DataType` | How nc_key is chosen from enum; alias resolution |
| ForecastSaver writing `XLAT`/`XLONG` | Variable names in output NetCDF | That `XLAT`/`XLON` are self-defined, not WRF's; CF `latitude`/`longitude` identity |
| Adapter reading ERA5 `t` field | `DataType.TK` with `nc_key="tk_p"` | That θ is computed from `T` + `P`; R/cp = 0.286; p₀ = 1000 hPa |

**Leverage**: One change to the enum or alias layer propagates to all callers and tests without each needing to know the conversion details.

**Locality**: The Θ conversion, nc_key resolution, and WRF adapter mapping all live behind the interface in one place (adapters + `data_type.py` + `netcdf_meta.py`). Callers don't need to know these details.

### 2.3 Seam Placement

The **external seam** sits at the `DataType` enum + `DataCompose` interface. Callers interact through:
- `DataType.TK / DataType.Lat / DataType.Lon` — enum members
- `DataCompose(var_name, level)` — constructor
- `dc.combined_key` — derived string
- `DataCompose.from_config(config_dict)` — factory

The **internal seams** (private to implementation) include:
- Which nc_key each enum member maps to
- Whether θ conversion happens in adapter or preproc
- Whether `short_name` is a separate field

---

## 3. Design Levers for This Session

### 3.1 Add `short_name` Field to `DataType`

**Current**: `DataType` has `description`, `code`, `nc_key` (via `__new__`).

**Desired**: Add `short_name` — a separate field for encoder/decoder/dataloader mapping, distinct from `nc_key` (NetCDF key) and `name` (description).

**Example after change**:
```python
class DataType(Enum):
    def __new__(cls, description: str, code: str, nc_key: str, short_name: str):
        obj = object.__new__(cls)
        obj._value_ = description
        obj.code = code
        obj.nc_key = nc_key
        obj.short_name = short_name
        return obj

    PH = ("Geopotential Height", "000", "z_p", "PH")
    TK = ("Temperature", "100", "tk_p", "TH")   # short_name=TH, distinct from nc_key=tk_p
    XLAT = ("Latitude", "LAT", "XLAT", "XLAT")  # short_name=XLAT=nc_key
    XLON = ("Longitude", "LON", "XLON", "XLON")  # short_name=XLON=nc_key
    TH = ("Potential Temperature", "TH", "th_p", "TH")  # new
```

**Why this enables depth**: The caller (encoder/decoder/dataloader) only needs `short_name` to route variables. The `nc_key` resolution (is it `tk_p` or `th_p`?) and the θ conversion are hidden behind the interface. Callers don't need to know the conversion details — they just use `short_name="TH"` and the module resolves the rest.

### 3.2 Rename `Lat` → `XLAT`, `Lon` → `XLON` in Enum

**Current**: `Lat = ("Latitude", "LAT", "XLAT")`, `Lon = ("Longitude", "LON", "XLONG")`.

**Desired**: Rename enum members to `XLAT`/`XLON`. The `nc_key` stays `XLAT`/`XLONG` (self-defined names). The `short_name` = `XLAT`/`XLON`. CF `standard_name` = `latitude`/`longitude` is the **internal identity**, not part of the interface.

**Design decision** (from session): Our `XLAT`/`XLON` are **self-defined** names that happen to coincide with WRF's 2D field names. The CF `latitude`/`longitude` is the cross-ecosystem semantic. The interface presents `XLAT`/`XLON`; the CF names are internal.

### 3.3 Add `TH` Enum Member (Replace `TK`)

**Current**: `TK = ("Temperature", "100", "tk_p")` — bare temperature, no CF standard_name in the interface.

**Desired**: `TH = ("Potential Temperature", "TH", "th_p", "air_potential_temperature")` — or at minimum `TH` with `nc_key="th_p"` and `short_name="TH"`.

**Conversion detail** (hidden implementation): θ = T·(p₀/p)^(R/cp), p₀=1000 hPa, R/cp≈0.286. This lives in the adapter (`diag_th_p` or modified `diag_tk_p`). The interface just exposes `DataType.TH` with `short_name="TH"`.

### 3.4 Alias / Legacy Mapping Layer

**Current**: Configs use `{"Lat": ["NoRule"], "Lon": ["NoRule"]}`, `DataCompose.from_config({"TK": [...]})`.

**Desired**: An alias layer maps legacy names to canonical names, so callers don't need to change.

**Example alias layer** (could be a dict or a small function):
```python
LEGACY_ALIASES = {
    "Lat": "XLAT",
    "Lon": "XLON",
    "TK": "TH",
}

def alias_var_name(name: str) -> str:
    return LEGACY_ALIASES.get(name, name)
```

**Usage**: `DataCompose.from_config({alias_var_name(k): v for k, v in config.items()})` — or auto-alias at enum construction.

**Why this is deep**: The alias is a 3-line layer. All callers continue using `Lat`/`Lon`/`TK`. The module internally resolves to `XLAT`/`XLON`/`TH`. Change happens in one place.

### 3.5 WRF Adapter Key Mapping

**Current**: `ForecastSaver._save_single_step` writes `XLAT`, `XLONG` 2D fields hardcoded (lines 205-206). Variable names for upper-air use `var_type.name_{level_type.nc_key}hPa` pattern (line 110).

**Desired**: The adapter maps our canonical keys to WRF variable names. Our `XLON` → WRF's `XLONG`. The `TH` variable name in output should be configurable (or default to `TH`).

**Key question**: Should the output variable name be `TH_Hpa500` or `TK_Hpa500`? 

- If `TH` is the canonical name, output should probably use `TH`.
- But the existing pattern uses `var_type.name` which would be `DataType.TH.name` = `"Potential Temperature"` → output `Potential_Temperature_Hpa500` — perhaps not desired.

**Resolution**: The `short_name` field handles the encoder/decoder mapping. The WRF adapter can use either `name` or `short_name` for output variable naming. This is an implementation detail behind the interface.

---

## 4. Step-by-Step Restructure Plan

### Phase 1: Add `short_name` to `DataType` enum
1. Modify `DataType.__new__` to accept `short_name: str` as 4th parameter
2. Update all enum members with `short_name` values:
   - `PH = ("Geopotential Height", "000", "z_p", "PH")`
   - `TK = ("Temperature", "100", "tk_p", "TH")` (short_name=TH, nc_key stays tk_p for now)
   - `XLAT = ("Latitude", "LAT", "XLAT", "XLAT")`
   - `XLON = ("Longitude", "LON", "XLONG", "XLON")`
   - Add `TH = ("Potential Temperature", "TH", "th_p", "TH")` (new)
3. Update `DataCompose.__post_init__` if it references `var_name.nc_key` or `var_name.code` in ways that need `short_name` separation
4. Update `DataCompose.__str__` to optionally include `short_name`

### Phase 2: Rename enum members + add alias layer
1. Rename `Lat` → `XLAT`, `Lon` → `XLON` in `DataType` (already in code per session, but verify consistency)
2. Add `LEGACY_ALIASES = {"Lat": "XLAT", "Lon": "XLON", "TK": "TH"}`
3. Update `from_config` to auto-alias, or add alias step before `from_config`
4. Update all `from_config` call sites (generate_const_masks.py, prediction.py, etc.) — either change literals or rely on alias layer

### Phase 3: Add `TH` conversion adapter
1. In `externals/dlamp-data/src/registry/diagnostic_functions.py`:
   - Add `diag_th_p(source_dataset, ds)` that computes θ = T·(p₀/p)^(R/cp)
   - Or modify `diag_tk_p` to optionally return θ when source has `P` field
2. Update `DataType.TH.nc_key` — if using adapter, `nc_key` could stay `tk_p` and θ is computed on read; or change to `th_p` and adapter handles conversion
3. Update `netcdf_meta.py` — add `air_potential_temperature` entry or rename `tk_p` → `th_p`

### Phase 4: Update all downstream files
1. `generate_const_masks.py`: `DataCompose.from_config({"Lat": ...})` → use alias or change to `{"XLAT": ...}`
2. `prediction.py`: `{"Lat": ["NoRule"], "Lon": ["NoRule"]}` → alias or `{"XLAT": [...], "XLON": [...]}`
3. `forecast_saver.py`: Verify variable naming with `TH`; if `short_name` is used for output naming, may need adjustment
4. `dlamp/config/...` rwrf YAML configs: Update `Lat`/`Lon`/`TK` patterns, or rely on alias layer
5. `externals/dlamp-data/src/preproc/dlamp_regridder.py`: Already uses `XLAT`/`XLONG` as tgtlon/tgtlat — consistent, no change needed unless target-key naming changes

### Phase 5: Verification
```bash
# Check enum values with short_name
python -c "
from dlamp.utils.data_type import DataType
for d in DataType:
    print(f'{d.name}: value={d.value}, code={d.code}, nc_key={d.nc_key}, short_name={d.short_name}')
"

# Check DataCompose with new vars
python -c "
from dlamp.utils.data_type import DataType
from dlamp.utils.data_compose import DataCompose
dc = DataCompose(DataType.XLAT, Level.NoRule)
print(f'XLAT str={dc}, combined_key={dc.combined_key}')
dc2 = DataCompose(DataType.TH if hasattr(DataType, 'TH') else DataType.TK, Level.NoRule)
print(f'TH/TK str={dc2}, combined_key={dc2.combined_key}')
"

# Run existing tests
python -m pytest src/dlamp/models/architectures/unet_test.py -v
"
```

---

## 5. Glossary Reference (from design skill)

| Term | Meaning in this doc |
|------|---------------------|
| **Module** | The variable registry (`DataType`, `DataCompose`, adapters) — anything with an interface + implementation |
| **Interface** | `DataType` enum members, `DataCompose` constructor + methods, alias layer — *everything a caller must know* |
| **Implementation** | nc_key resolution, CF standard-name lookup, TH→θ conversion, WRF adapter mapping, source adapters, preproc, config aliases |
| **Depth** | Small interface (enum + DataCompose) + large behaviour hidden (conversions, adapter mappings, alias resolution) |
| **Seam** | `DataType` enum + `DataCompose` interface — where callers cross, and where adapters sit |
| **Adapter** | Source adapter functions (`diag_tk_p`, future `diag_th_p`); WRF adapter (key mapping); alias layer (legacy→canonical) |
| **Leverage** | One change to enum/alias → propagates to all callers/tests without each knowing conversion details |
| **Locality** | Conversions/adapters concentrated in one place (adapters + data_type.py) rather than spread across callers |
| **Depth is a property of the interface** | The `DataType`/`DataCompose` interface depth is what delivers leverage/locality; internal implementation can be composed of mockable parts |
| **The deletion test** | If we delete the registry module, complexity should vanish from the interface and reappear across callers only if the module earns its keep |
| **One adapter = hypothetical seam, two = real one** | We have multiple adapters: source adapters (ERA5/GFS/RWRF), WRF adapter, alias layer — these are real seams because behaviour actually varies across them |

---

## 6. Files Affected (Comprehensive)

```
src/dlamp/utils/data_type.py                   # Add short_name to __new__ + all members
src/dlamp/utils/data_compose.py               # Update if needed for short_name
src/dlamp/analysis/netcdf_meta.py             # Add air_potential_temperature entry
src/dlamp/analysis/forecast_saver.py          # Verify TH variable naming
src/dlamp/generate_const_masks.py             # Update from_config calls (alias or literals)
src/dlamp/analysis/prediction.py              # Update Lat/Lon → XLAT/XLON (alias or literals)
externals/dlamp-data/src/registry/            # Add diag_th_p or modify diag_tk_p
externals/dlamp-data/src/preproc/             # May need th_p handling
dlamp/config/... (rwrf_*.yaml)                # Update Lat/Lon/TK patterns or alias
```

---

## 7. Minimal Viable Deep Module (if time is short)

If the full restructure can't be completed in one session, the **minimal deep-module change** that still delivers depth+leverage+locality is:

1. **Add `short_name` field to `DataType`** (4th parameter to `__new__`, update all members)
2. **Add `TH` enum member** with `short_name="TH"`, `nc_key="th_p"` (or keep `tk_p` and compute θ in adapter)
3. **Add alias layer** `LEGACY_ALIASES = {"Lat": "XLAT", "Lon": "XLON", "TK": "TH"}` and auto-alias in `from_config`
4. **Update `from_config` call sites** to use the alias (or change literals to canonical names)

This 4-step minimal change already delivers:
- **Depth**: callers use `short_name`; conversions/adapters hidden
- **Leverage**: one `short_name` change propagates everywhere
- **Locality**: alias layer + adapter layer = 2 small places vs N callers

The remaining phases (full CF standard_name integration, WRF adapter key mapping, etc.) can be incrementally added.

---
*End of DLAMP deep modules design document.*