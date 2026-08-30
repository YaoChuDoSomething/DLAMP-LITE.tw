# Relocate Stray Tests out of src/dlamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all test code from the shipped `src/dlamp/` package so every test lives under `tests/` mirroring the package path.

**Architecture:** Delete 4 test files from `src/dlamp/` whose canonical (rewritten, CPU) forms already exist under `tests/dlamp/models/architectures/`; delete the broken `pangu_model_test.py` (per spec 11:35 it must be deleted, not migrated); relocate `src/dlamp/utils/test_data_type.py` to its mirrored `tests/dlamp/utils/` path (no tests/ copy exists yet). Nothing else changes — the already-correct `tests/dlamp/*` content is untouched.

**Tech Stack:** Python 3.11, pytest (pyproject `[tool.pytest.ini_options]` testpaths=`["tests"]`, pythonpath=`["src"]`), `make test` = `uv run pytest --cov=src/dlamp tests/`.

## Global Constraints

- All test code must live under `tests/`, mirroring the package path: `tests/dlamp/<path>` ↔ `src/dlamp/<path>`. Never under `src/`.
- `make test` must pass (currently a subset of tests already pass; the relocated `test_data_type` adds one passing test).
- `make check` (ruff + radon) must stay green.
- Test files use pytest style; new relocated file must carry a module docstring (GEMINI.md) and a `-> None` return annotation (GEMINI.md full type hints).
- Do NOT modify `tests/dlamp/models/architectures/test_*.py` or `tests/dlamp/data/*` content in this plan.
- Commit messages: short imperative summaries. AI commits include `Co-Authored-By: (agent byline)`.
- Run all commands from repo root (`which python` → `.venv/bin/python`; `src/` is on sys.path).

---

### Task 1: Delete three superseded architecture tests from src/

These three files have rewritten CPU copies already in `tests/dlamp/models/architectures/` (`test_unet.py`, `test_glide_unet.py`, `test_earth_3d_specifics.py`). The `src/` versions are the old GPU `.cuda()`/relative-import tests. `testpaths=["tests"]` never collects them — they are dead shipped code. Delete them; do not migrate (canonical form already exists).

**Files:**
- Delete: `src/dlamp/models/architectures/unet_test.py`
- Delete: `src/dlamp/models/architectures/glide_unet_test.py`
- Delete: `src/dlamp/models/architectures/earth_3d_specifics_test.py`
- Test: `tests/dlamp/models/architectures/test_unet.py`, `test_glide_unet.py`, `test_earth_3d_specifics.py` (existing — verify they still pass)

**Interfaces:**
- Consumes: the existing `tests/dlamp/models/architectures/test_*.py` files (already present at HEAD).
- Produces: nothing new — this task only removes files.

- [ ] **Step 1: Confirm the existing tests/ mirrors are tracked and pass before deleting**

```bash
git ls-files tests/dlamp/models/architectures/test_unet.py tests/dlamp/models/architectures/test_glide_unet.py tests/dlamp/models/architectures/test_earth_3d_specifics.py
uv run pytest tests/dlamp/models/architectures/ -q
```

Expected: all three paths listed (tracked); the three test files PASS. If a mirror is missing, STOP — a delete would lose coverage. Note: `test_unet.py` and `test_glide_unet.py` may report skip/failure unrelated to this change; only the three files listed here must PASS.

- [ ] **Step 2: Delete the three superseded src/ tests**

```bash
git rm src/dlamp/models/architectures/unet_test.py \
       src/dlamp/models/architectures/glide_unet_test.py \
       src/dlamp/models/architectures/earth_3d_specifics_test.py
```

Expected: three `rm 'src/dlamp/models/architectures/<file>'` lines printed.

- [ ] **Step 3: Verify no code references the deleted files**

```bash
grep -rn "architectures.unet_test\|architectures.glide_unet_test\|architectures.earth_3d_specifics_test" src tests
```

Expected: no output (exit 1). Only self-referential CLI comments existed before; confirm none remain that point at the deleted paths.

- [ ] **Step 4: Verify test suite still passes**

```bash
uv run pytest tests/dlamp/models/architectures/ -q
```

Expected: PASS on the three `test_*.py` files (same result as Step 1).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor(tests): delete superseded architecture tests from src/

Co-Authored-By: (agent byline)"
```

---

### Task 2: Delete broken pangu_model_test.py

`src/dlamp/models/architectures/pangu_model_test.py` crashes at import because it opens `config/model/dlamp_train.yaml`, which does not exist (config/model holds only dated yamls). Spec `.archived/dlamp-monorepo-refactor/issues/11-module-test-plans.md` explicitly says *"Delete: ... `pangu_model_test.py` (import crash)"*. Delete it; do not migrate.

**Files:**
- Delete: `src/dlamp/models/architectures/pangu_model_test.py`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing.

- [ ] **Step 1: Confirm the file is the broken one**

```bash
head -20 src/dlamp/models/architectures/pangu_model_test.py
```

Expected: a top-of-file `open("config/model/dlamp_train.yaml")` (or `yaml.load(...)` of that path) causing an import-time crash.

- [ ] **Step 2: Delete it**

```bash
git rm src/dlamp/models/architectures/pangu_model_test.py
```

Expected: `rm 'src/dlamp/models/architectures/pangu_model_test.py'` printed.

- [ ] **Step 3: Verify nothing imports it**

```bash
grep -rn "pangu_model_test\|pangu_model" src tests --include='*.py'
```

Expected: matches only legitimate references to the `Pangu`/`PanguModel` architecture (e.g. `from ... import PanguModel`), NOT the `pangu_model_test` module path. Confirm there is no `import pangu_model_test` or `from ... import pangu_model_test`.

- [ ] **Step 4: Verify test suite still collects cleanly**

```bash
uv run pytest tests/ -q
```

Expected: collection completes without the previous import-crash on `pangu_model_test`. (Individual test failures unrelated to this change are out of scope.)

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "test: delete broken pangu_model_test from src/

Import-crashes on missing config/model/dlamp_train.yaml; superseded by ONNX workflow (spec 11:35).

Co-Authored-By: (agent byline)"
```

---

### Task 3: Relocate test_data_type.py to tests/dlamp/utils/

`src/dlamp/utils/test_data_type.py` is the only stray test with no `tests/` mirror. It tests the `DataType` enum in `src/dlamp/utils/data_type.py` (the 6-field CF metadata scheme). Move it to the mirrored path `tests/dlamp/utils/test_data_type.py`, create the `tests/dlamp/utils/` package, and fix the file to meet GEMINI.md (module docstring, `-> None` annotation, `test_`-prefixed functions). Keep the assertions as-is — they target the real `DataType` members.

**Files:**
- Create: `tests/dlamp/utils/__init__.py`
- Create: `tests/dlamp/utils/test_data_type.py`
- Delete: `src/dlamp/utils/test_data_type.py`
- Test: `tests/dlamp/utils/test_data_type.py`

**Interfaces:**
- Consumes: `dlamp.utils.data_type.DataType` with members `TK`, `Z`, `Lat`, `XLAT`, `Qt` — each exposing `.short_name`, `.nc_key`, and where applicable `.units`, `.standard_name`, `.description`. (Verify these against `src/dlamp/utils/data_type.py` in Step 1; if a member or attribute differs, adjust the assertions to match the enum's actual values.)
- Produces: a passing test file under `tests/dlamp/utils/`.

- [ ] **Step 1: Verify DataType members and attributes match the assertions**

```bash
grep -nE "TK|^    Z|Lat|XLAT|Qt|short_name|nc_key|units|standard_name|description" src/dlamp/utils/data_type.py | head -40
```

Expected: `DataType` defines `TK`, `Z`, `Lat`, `XLAT`, `Qt` with `short_name`, `nc_key`, `units`, `standard_name`, `description` fields, and the values asserted in the existing test (e.g. `TK.nc_key == "TK"`, `TK.units == "K"`, `TK.standard_name == "air_temperature"`). If a value differs from the existing test, note it — you will adjust the relocated assertions to the real enum.

- [ ] **Step 2: Create the tests/dlamp/utils/ package**

```bash
mkdir -p tests/dlamp/utils
touch tests/dlamp/utils/__init__.py
```

Expected: `tests/dlamp/utils/` directory and empty `__init__.py` created.

- [ ] **Step 3: Write the relocated test file**

Write `tests/dlamp/utils/test_data_type.py`:

```python
"""Unit tests for the DataType variable metadata enum.

Verifies the 6-field CF metadata scheme on select members (TK, Z, Lat,
XLAT, Qt): short_name, nc_key, units, standard_name, and description.
"""

from dlamp.utils.data_type import DataType


def test_tk_temperature_metadata() -> None:
    """TK exposes air-temperature metadata."""
    assert DataType.TK.short_name == "TK"
    assert DataType.TK.nc_key == "TK"
    assert DataType.TK.units == "K"
    assert DataType.TK.standard_name == "air_temperature"
    assert "temperature" in DataType.TK.description.lower()


def test_z_geopotential_height_metadata() -> None:
    """Z exposes geopotential-height metadata."""
    assert DataType.Z.short_name == "Z"
    assert DataType.Z.nc_key == "Z"
    assert "geopotential height" in DataType.Z.description.lower()


def test_lat_coordinate_metadata() -> None:
    """Lat is a 1-D latitude coordinate."""
    assert DataType.Lat.short_name == "lat"
    assert DataType.Lat.nc_key == "lat"
    assert "latitude" in DataType.Lat.description.lower()


def test_xlat_meshgrid_metadata() -> None:
    """XLAT is the 2-D latitude meshgrid."""
    assert DataType.XLAT.short_name == "XLAT"
    assert DataType.XLAT.nc_key == "XLAT"


def test_qt_model_input_metadata() -> None:
    """Qt is read directly as a model input."""
    assert DataType.Qt.nc_key == "Qt"
```

Note: these are the original assertions restructured into per-member test functions with docstrings. If Step 1 showed a member/attribute value differs from above, fix the affected assertion to the enum's actual value.

- [ ] **Step 4: Run the new test to verify it passes**

```bash
uv run pytest tests/dlamp/utils/test_data_type.py -v
```

Expected: 5 PASS (`test_tk_temperature_metadata`, `test_z_geopotential_height_metadata`, `test_lat_coordinate_metadata`, `test_xlat_meshgrid_metadata`, `test_qt_model_input_metadata`). If any FAIL, the enum value differs — fix the assertion to the real enum (from Step 1) and re-run until PASS.

- [ ] **Step 5: Delete the original from src/**

```bash
git rm src/dlamp/utils/test_data_type.py
```

Expected: `rm 'src/dlamp/utils/test_data_type.py'` printed.

- [ ] **Step 6: Verify no code imports the old path**

```bash
grep -rn "utils.test_data_type\|import test_data_type" src tests
```

Expected: no output (exit 1).

- [ ] **Step 7: Run the full suite + lint gate**

```bash
uv run pytest tests/ -q
make check
```

Expected: pytest collects and runs `tests/dlamp/utils/test_data_type.py` (5 PASS among the suite); `make check` (ruff + radon) exits 0. Fix any ruff issues in `tests/dlamp/utils/test_data_type.py` (e.g. line length) and re-run.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "test: relocate data_type test to tests/dlamp/utils/

Move src/dlamp/utils/test_data_type.py to the mirrored tests/ path per test-isolation invariant.

Co-Authored-By: (agent byline)"
```

---

## Verification / Definition of Done

- [ ] `find src -name '*test*.py'` returns **nothing** (all test code gone from `src/`).
- [ ] `uv run pytest tests/ -q` completes collection with no import-crash and `tests/dlamp/utils/test_data_type.py` passes.
- [ ] `make check` (ruff + radon) exits 0.
- [ ] `git log --oneline -4` shows the three commits: delete superseded arch tests, delete broken pangu test, relocate data_type test.
- [ ] `CONTEXT.md` Testing section invariants hold: no test under `src/dlamp/`; `tests/dlamp/utils/` mirrors `src/dlamp/utils/`.

## Self-Review

1. **Spec coverage:** The test-isolation invariant (all tests under `tests/`, mirrored paths) is fully served — Task 1 removes 3 superseded, Task 2 removes 1 broken, Task 3 relocates the 1 with no mirror. No test coverage lost: the 3 arch tests keep their `tests/` copies; pangu is intentionally deleted per spec 11:35; data_type gains a collected home. No gaps.
2. **Placeholder scan:** All steps contain concrete commands/code. No "TBD"/"handle edge cases". The only conditional is a documented, specific branch (Step 1 enum-value check → fix the named assertion), which is a real verification step, not a placeholder.
3. **Type consistency:** `DataType` members/attributes are referenced identically across Step 1 and Step 3 (`TK`, `Z`, `Lat`, `XLAT`, `Qt`; `.short_name`, `.nc_key`, `.units`, `.standard_name`, `.description`). `test_data_type.py` path is consistent (Task 3 Create/Delete/Test all `tests/dlamp/utils/test_data_type.py`). No name drift.