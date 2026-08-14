# DLAMP Monorepo Testing Specification

**Document Version:** 1.0.0  
**Status:** Approved & Locked  

---

## 1. Overview & Test Hierarchy

This specification defines the testing framework, standards, and regression strategy for the DLAMP monorepo.

### Test Directory Structure

```text
tests/
├── dlamp/                          # Mirrors src/dlamp/
│   ├── analysis/
│   ├── inference/
│   ├── models/
│   │   └── architectures/          # test_unet.py, test_glide_unet.py, test_earth_3d_specifics.py
│   ├── utils/
│   └── data/                       # Mirrors src/dlamp/data/
│       ├── preproc/                # test_cds_downloader.py, test_dlamp_regridder.py
│       └── registry/               # test_diagnostic_functions.py, test_diagnostic_registry.py
├── regression/                     # Regression test suite (@pytest.mark.regression)
│   ├── test_pipeline_regression.py
│   └── test_inference_regression.py
└── fixtures/                       # Shared synthetic fixtures & helpers
```

---

## 2. Coding Standards & Docstring Rules

- **Module Naming:** Test files must be named `test_<module>.py` (or `<module>_test.py` for legacy compatibility).
- **Docstrings:** All test functions, modules, and fixtures must include Google-style docstrings complying with `GEMINI.md`.
- **Module Docstring Header:**

  ```python
  """Unit tests for <module_name>.

  Usage:
      pytest tests/dlamp/path/to/test_<module>.py
  """
  ```

---

## 3. Test Markers & Execution Policy

1. **Default Fast Unit Tests:**

   ```bash
   pytest -m "not integration and not regression"
   ```

2. **Integration Tests (`@pytest.mark.integration`):**
   - Requires real sample ERA5 data in `DLAMP_DATA_PATH`.
   - Skipped by default. Run via:

     ```bash
     pytest -m integration
     ```

3. **Regression Tests (`@pytest.mark.regression`):**
   - Compares refactored code outputs against pre-move golden baseline snapshots.
   - Run via:

     ```bash
     make regression
     ```

---

## 4. Regression Strategy & Tolerances

- **Baseline Storage:** Baseline snapshots generated from pre-move repos live in `DLAMP_DATA_PATH/regression_golden/` (gitignored).
- **Floating-Point Comparisons:** `xarray.testing.assert_allclose` / `numpy.testing.assert_allclose` with:
  - `rtol = 1e-5`
  - `atol = 1e-6`
- **Integer/Discrete Comparisons:** Exact equality (`assert_array_equal`) for binary masks (`land_sea_mask`, `topography_mask`) and NetCDF dimension metadata headers.
