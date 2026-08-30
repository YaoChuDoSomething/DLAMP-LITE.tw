# 10 Decide regression strategy

Type: grilling
Status: resolved
Blocked by: 03, 09

## Question

Decide the regression strategy proving the refactor is behavior-preserving — a required section of the testing specification (locked in Q8):

- **Baseline/golden outputs**: what constitutes "golden" for a forecasting + data pipeline — existing dlamp-data fixtures (`test/fixtures/*.nc`), a fixed set of NetCDF outputs, or re-running the pre-move code to snapshot outputs?
- **Comparison policy**: exact equality vs tolerance (float comparisons for netcdf4/hdf5/zarr round-trips, interpolation, diagnostics); per-channel or per-variable tolerances.
- **Where checks live**: `tests/regression/`? A dedicated harness? How it fits the `tests/` layout from ticket 09.
- **Capture timing**: baselines snapshotted from the *pre-move* repos before execution starts — who/which ticket captures them and where they're stored (LFS? gitignored?).
- **Scope of regression**: every moved module, or a priority slice (e.g. pipeline IO + inference path first)?

## Answer

Grilled 5 branches, all confirmed. Approved regression strategy policy:

1. **Golden Baseline Outputs:** Pre-move code snapshot outputs (`e5dlamp_*` NetCDF files, regridded arrays, diagnostic calculation outputs, and `predict.py` model forecast NetCDFs) generated before restructuring starts.
2. **Comparison Policy:**
   - Float fields: `xarray.testing.assert_allclose` / `numpy.testing.assert_allclose` with `rtol=1e-5`, `atol=1e-6`.
   - Discrete/Integer fields: Exact array equality for binary masks (`land_sea_mask`, `topography_mask`) and dimension/coord header metadata.
3. **Location & Pytest Marking:** Dedicated `tests/regression/` directory tagged with `@pytest.mark.regression`. Skipped by default; executed explicitly via `make regression` (`pytest -m regression`).
4. **Capture Timing & Storage:** Baselines captured in Step 1 of execution (pre-move), stored in `DLAMP_DATA_PATH/regression_golden/` (gitignored, not committed). Script `tests/regression/generate_golden.py` provided for reproducibility.
5. **Scope:** Priority regression testing on Data Pipeline (`dlamp.data.preproc`, `dlamp.data.registry`) and Inference Pipeline (`predict.py` / `prediction.py`). Training loops covered by 1-step dry-run smoke test.

Inputs to: testing specification (ticket 09 supplement), handoff design doc (ticket 12).
