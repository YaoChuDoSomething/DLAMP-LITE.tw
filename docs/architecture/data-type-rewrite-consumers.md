# Variable reference changes after data_type.py rewrite

`src/dlamp/utils/data_type.py` rewritten to the 6-field CF-Conventions enum
(`short_name, standard_name, description, units, nc_key`) per
`docs/architecture/dlamp-output-variable-registry.md`. This changed/removed
enum member names and `nc_key` values. Consumers below were **not** updated in
this step (enum-only rewrite) — they now reference variables that changed
shape/meaning and need review in the venv-gated Q8 sweep.

## Member renames

| Old member      | New member | nc_key old → new             | notes                                   |
| --------------- | ---------- | ---------------------------- | --------------------------------------- |
| `PH`            | `Z`        | `z_p` → `Z`                  | geopotential height                     |
| `Radar`         | `dBZ`      | `MAX_REFL` → `REFL`          | column-max reflectivity, single layer   |
| `MASK`          | `MASKLAND` | `LANDMASK` → `LANDMASK`      | now bool (`true` land / `false` sea)    |
| `Td`            | `Td2m`     | `td` → `Td_2m`               | AGL dew point                           |
| `T` (2m temp)   | `T2m`      | — → `T_2m`                   | (T never existed as output, only in viz)|
| `U` / `V` (10m) | `U10m`/`V10m` | — → `U_10m`/`V_10m`       | (never existed as output, only in viz)  |
| `P`             | (kept)     | `pres_levels` (pressure)     | kept for level lookup                   |

## Dropped / reclassified

- `Qt`: kept as **model input** only. `file_util.py:100` currently computes it
  as a diagnostic sum (`Qr+Qc+Qi+Qs+Qg`) — violates the "read directly, no
  diagnostic" rule; must be moved to a `data/` plugin read, not the read path.

## Files referencing changed variables (need review)

All consumers were migrated in this sweep. Remaining mypy errors in
`plotter.py`/`data_manager.py` are pre-existing strict-mode debt (no-redef,
missing return types, `RuntimeConfig` indexing), unrelated to the enum rename.

| File                                        | fix applied                                     |
| ------------------------------------------- | ----------------------------------------------- |
| `src/dlamp/utils/data_compose.py`           | `Radar`→`dBZ`, `Td`→`Td2m`, `U/V`→`U10m/V10m`, `var_name.code` bug fixed |
| `src/dlamp/utils/file_util.py`              | `Qt` direct-read, `P` restored                  |
| `src/dlamp/utils/test_data_type.py`         | `PH`→`Z`, `tk_p`→`TK`, `Lat`→`lat`, + `XLAT`/`Qt`/`units`/`standard_name` asserts |
| `src/dlamp/analysis/plotter.py`             | `PH`→`Z` (8×); `Qt` kept (still a member)       |
| `src/dlamp/analysis/data_manager.py`        | no change needed (`Qt` still a member)          |
| `src/dlamp/analysis/forecast_saver.py`      | no change needed (`Qt` still a member)          |
| `src/dlamp/visual/viz_radar.py`             | `Radar`→`dBZ`, `Lat`→`XLAT`, `Lon`→`XLON`       |
| `src/dlamp/visual/viz_temp.py`              | `T`(Hpa850)→`TK`, `Lat`→`XLAT`, `Lon`→`XLON`    |
| `src/dlamp/visual/viz_vor.py`               | `U`→`UM`, `V`→`VM`, `Lat`→`XLAT`, `Lon`→`XLON`  |

## Caveats

- `data_compose.py:35` `var_name.code` pre-existing bug fixed → now uses
  `var_name.short_name`.
- Qt read path in `file_util.py` changed from diagnostic sum to **direct
  read** from source (`dc.combined_key`), per user decision.
- `DataType.P` restored as a pressure-coordinate-only member (not a model
  output) for level→index mapping.
- `runtime_config.py` singleton switched from function-attribute cache to
  module-level `_singleton` (mypy-strict clean).
- No venv: verified via `uvx mypy` (data_type module graph green),
  `uvx ruff`, and `py_compile`. plotter/data_manager pre-existing mypy debt
  left untouched (out of the enum-rename scope).
