# 10 Decide regression strategy

Type: grilling
Status: open
Blocked by: 03, 09

## Question

Decide the regression strategy proving the refactor is behavior-preserving — a required section of the testing specification (locked in Q8):

- **Baseline/golden outputs**: what constitutes "golden" for a forecasting + data pipeline — existing dlamp-data fixtures (`test/fixtures/*.nc`), a fixed set of NetCDF outputs, or re-running the pre-move code to snapshot outputs?
- **Comparison policy**: exact equality vs tolerance (float comparisons for netcdf4/hdf5/zarr round-trips, interpolation, diagnostics); per-channel or per-variable tolerances.
- **Where checks live**: `tests/regression/`? A dedicated harness? How it fits the `tests/` layout from ticket 09.
- **Capture timing**: baselines snapshotted from the *pre-move* repos before execution starts — who/which ticket captures them and where they're stored (LFS? gitignored?).
- **Scope of regression**: every moved module, or a priority slice (e.g. pipeline IO + inference path first)?

Grill one decision at a time; the answer records the regression strategy that goes into the testing spec.
