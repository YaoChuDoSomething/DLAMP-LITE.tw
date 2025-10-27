# roadmap.md

Nice—this is a clean, opinionated split of **acquisition → inference → post-processing**. I walked it against your earlier constraints (RWRF quirks, np.datetime64 time, no InterpModAFNO/pandas, linear interp) and it’s very close. Below are the small-but-important fixes I recommend so it’s bullet-proof for DLAMP/RWRF.

---

# What to keep (already correct)

* Strict phase separation ✅
* Pure **linear** time interpolation (no InterpModAFNO) ✅
* No pandas ✅
* Regridding via bilinear + nearest fill ✅
* Hourly file-per-time output ✅
* Diagnostics isolated in `diag/diagnostics.py` ✅

---

# Gaps to patch (RWRF specifics)

## 1) Pressure dimension & `pres_levels` variable

RWRF expects:

* A **dimension** named `pres_bottom_top`
* A **1D variable** named `pres_levels` with dims `('pres_bottom_top',)`
* All 3-D fields shaped as `('Time','pres_bottom_top','south_north','west_east')`
  (Your current `transform_to_rwrf()` renames to `pressure` and doesn’t emit `pres_levels`.)

### Patch — `src/op/workflows/transformations.py`

Replace the 3-D block build with this (drop-in):

```python
# After you collect data_subset for prefix_3d...
# Ensure dims ('pressure','south_north','west_east') → rename to RWRF names
data_subset = data_subset.rename({"variable": "pres_bottom_top"})
data_subset = data_subset.assign_coords(
    pres_bottom_top=("pres_bottom_top", pressure_levels)
)
# Keep data_vars with dims ('pres_bottom_top','south_north','west_east')
rwrf_name = mappings[prefix_3d]  # e.g., U, V, T, GHT, Q
rwrf_vars[rwrf_name] = data_subset
```

After building `rwrf_ds = xr.Dataset(rwrf_vars)`, **add** the coordinate variable:

```python
rwrf_ds = rwrf_ds.assign(
    pres_levels=("pres_bottom_top", pressure_levels)
)
rwrf_ds["pres_levels"].attrs.update(
    long_name="Pressure levels",
    units="hPa"
)
```

> Note: keep **2-D** fields as `('south_north','west_east')` for now; we’ll add the `Time` dim at write time.

---

## 2) Ensure `np.datetime64` everywhere

* You’re already using `np.datetime64` for internal times. Keep it that way and **avoid converting to Python datetime** right before writing.
* When constructing the **Times** char var, derive from the `np.datetime64` scalar you’re saving.

---

## 3) Add a proper `Time` dimension on write

RWRF conventions want a `Time` dim, even when you save “one time per file.”
In `_write_rwrf_file()`, wrap all data variables to include a leading `Time` dimension of length 1.

### Patch — `src/op/io/rwrf_io.py` → `_write_rwrf_file`

Right before `to_netcdf(...)`, add:

```python
# Ensure a 'Time' dimension across all data_vars (length 1)
if "Time" not in ds_to_write.dims:
    ds_to_write = ds_to_write.expand_dims(Time=[0])

# For each var, if it lacks 'Time', prepend it (keeping var dims order RWRF-style)
new_vars = {}
for v in ds_to_write.data_vars:
    da = ds_to_write[v]
    if "Time" not in da.dims:
        da = da.expand_dims(Time=[0])
        # Reorder typical dims for 3D fields: ('Time','pres_bottom_top','south_north','west_east')
        desired = ["Time"]
        if "pres_bottom_top" in da.dims: desired += ["pres_bottom_top"]
        if "south_north" in da.dims:     desired += ["south_north"]
        if "west_east" in da.dims:       desired += ["west_east"]
        # Fall back to current order if some dims missing
        remaining = [d for d in da.dims if d not in desired]
        da = da.transpose(*(desired + remaining))
    new_vars[v] = da
ds_to_write = ds_to_write.assign(**new_vars)
```

This guarantees **every** field matches RWRF expectations without touching your earlier logic.

---

## 4) `Times` char variable from `np.datetime64`

Your current code is close; make it robust for scalar time:

```python
time_val = ds["time"].item() if ds["time"].ndim == 0 else ds["time"].values
# Convert to second resolution, "YYYY-MM-DD_HH:MM:SS"
time_str = np.datetime_as_string(time_val, unit="s").replace("T", "_")
times_char_array = np.array([list(time_str)], dtype="S1")
ds_to_write["Times"] = (("Time", "DateStrLen"), times_char_array)
```

---

## 5) BBox crop stability

Your crop via boolean mask on `XLAT`/`XLONG` is fine. To keep grid integrity, it’s a bit safer to slice by **index ranges** if the target grid is rectangular. If your `XLAT/XLONG` are monotone 2-D (typical WRF), the mask is OK. Keep as-is unless you see ragged borders after `drop=True`.

---

## 6) File naming vs. true time

Right now you name files `F000..Fnnn`. If DLAMP expects timestamps, switch to:

```python
ts = np.datetime_as_string(time_step, unit="m").replace("T", "_")  # minute precision
filename = f"sfno_rwrf_{ts}.nc"
```

If `F###H` is preferred, you can keep your counter; both patterns can be supported with a flag.

---

## 7) Minor Earth2Studio ergonomics

* Your use of `asyncio` around `fetch_data` and the iterator likely isn’t necessary (most E2S calls are sync). If you’ve verified async works in your env, fine; otherwise simplifying to sync avoids event-loop surprises.
* `_tensor_to_dataarray(...)`: confirm `self.model.output_coords()["variable"]` exists and matches the returned tensor’s channel order. If not, fall back to `self.model.input_coords()["variable"]` for IC and `output_coords()` for forecast steps (some builds differ).

---

# Minimal diffs (copy-paste)

### `src/op/workflows/transformations.py` (tail end)

```python
# ... inside transform_to_rwrf after building rwrf_vars for 2D and 3D:

rwrf_ds = xr.Dataset(rwrf_vars)

# Add RWRF pressure coordinate/variable
rwrf_ds = rwrf_ds.assign(
    pres_levels=("pres_bottom_top", pressure_levels)
)
rwrf_ds["pres_levels"].attrs.update(
    long_name="Pressure levels",
    units="hPa"
)

return rwrf_ds
```

…and earlier in the 3-D block, replace your `rename({"variable": "pressure"})` with:

```python
data_subset = data_subset.rename({"variable": "pres_bottom_top"})
data_subset = data_subset.assign_coords(
    pres_bottom_top=("pres_bottom_top", pressure_levels)
)
```

### `src/op/io/rwrf_io.py` (`_write_rwrf_file`)

```python
time_val = ds["time"].item() if ds["time"].ndim == 0 else ds["time"].values
time_str = np.datetime_as_string(time_val, unit="s").replace("T", "_")
times_char_array = np.array([list(time_str)], dtype="S1")

ds_to_write = ds.copy()
# Guarantee Time dimension for all variables
if "Time" not in ds_to_write.dims:
    ds_to_write = ds_to_write.expand_dims(Time=[0])

new_vars = {}
for v in ds_to_write.data_vars:
    da = ds_to_write[v]
    if "Time" not in da.dims:
        da = da.expand_dims(Time=[0])
        desired = ["Time"]
        if "pres_bottom_top" in da.dims: desired += ["pres_bottom_top"]
        if "south_north" in da.dims:     desired += ["south_north"]
        if "west_east" in da.dims:       desired += ["west_east"]
        remaining = [d for d in da.dims if d not in desired]
        da = da.transpose(*(desired + remaining))
    new_vars[v] = da
ds_to_write = ds_to_write.assign(**new_vars)

ds_to_write["Times"] = (("Time", "DateStrLen"), times_char_array)
ds_to_write.attrs.update(global_attrs)

encoding = {}
for var in ds_to_write.data_vars:
    if ds_to_write[var].dtype in (np.float32, np.float64):
        encoding[var] = {"dtype": "float32", "_FillValue": -9999.0}

ds_to_write.to_netcdf(path, engine="netcdf4", format="NETCDF4", encoding=encoding)
logger.info(f"Successfully wrote RWRF file: {path}")
```

---

# Quick validation checklist (for your next run)

* [ ] `ncdump -h` of any hourly file shows:

  * `dimensions: Time = 1; DateStrLen = 19; pres_bottom_top = 13; south_north, west_east`
  * `variables: char Times(Time, DateStrLen); float U(Time, pres_bottom_top, south_north, west_east); ...`
  * `float pres_levels(pres_bottom_top)` with units `hPa`
* [ ] All timestamps derive from `np.datetime64` (no tz surprises).
* [ ] 2-D vars have shape `(Time, south_north, west_east)`.
* [ ] 3-D vars have shape `(Time, pres_bottom_top, south_north, west_east)`.

If you want, I can fold these patches directly into your files and add a tiny smoke test that writes one step and asserts dimensions/vars.

