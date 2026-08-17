# Canonical Variable Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform `DataType` into an active Canonical Variable Registry that encapsulates stable identities, NetCDF keys, CF descriptions, and validation logic.

**Architecture:** 
The `DataType` Enum will be expanded to include `short_name`, `description`, and `nc_key`. It will provide a `validate(data)` method for domain constraints. Variable identifiers for output/mapping will be constructed dynamically based on coordinate systems (Pressure vs AGL vs Other).

**Tech Stack:** Python 3.11, PyTorch, NetCDF (via xarray).

## Global Constraints

- **Identity**: Stable identity is `enum` or `short_name`.
- **Description**: Must follow CF-Conventions.
- **Naming Conventions**: 
  - Pressure: `{shortname}_{pressure_in_hPa}`
  - AGL: `{shortname}_{height_above_ground}m`
  - Other: `{shortname}`
- **Domain Truth**: `Lat`/`Lon` (1D) $\neq$ `XLAT`/`XLON` (2D). Only `XLAT`/`XLON` are used.
- **TH**: Read as `th_p` from datafiles.
- **No backward compatibility**.

---

### Task 1: Deepen `DataType` Enum Definition

**Files:**
- Modify: `src/dlamp/utils/data_type.py`
- Test: `src/dlamp/utils/test_data_type.py` (create if not exists)

**Interfaces:**
- Produces: `DataType` members with attributes `short_name`, `description`, `nc_key`.

- [ ] **Step 1: Write failing test for new attributes**

```python
from dlamp.utils.data_type import DataType

def test_data_type_attributes():
    # Test for a specific variable, e.g., TH
    assert DataType.TH.short_name == "TH"
    assert DataType.TH.nc_key == "th_p"
    assert "potential temperature" in DataType.TH.description.lower()
```

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: FAIL (AttributeError)

- [ ] **Step 3: Implement deepened `DataType`**

Update `DataType` members to use a tuple or a named tuple/class for values:
`(short_name, description, nc_key)`

Example members:
- `TH = ("TH", "air_potential_temperature", "th_p")`
- `XLAT = ("XLAT", "latitude", "XLAT")`
- `XLON = ("XLON", "longitude", "XLON")`

Add properties to the `DataType` enum class:
```python
@property
def short_name(self): return self.value[0]
@property
def description(self): return self.value[1]
@property
def nc_key(self): return self.value[2]
```

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: PASS

- [ ] **Step 5: Commit**
`git add src/dlamp/utils/data_type.py src/dlamp/utils/test_data_type.py`
`git commit -m "refactor: deepen DataType enum into canonical registry"`

---

### Task 2: Implement Variable Identity Construction

**Files:**
- Modify: `src/dlamp/utils/data_type.py`
- Test: `src/dlamp/utils/test_data_type.py`

**Interfaces:**
- Produces: `DataType.get_identity(level)` method.

- [ ] **Step 1: Write failing test for identity construction**

```python
from dlamp.utils.data_type import DataType, Level

def test_identity_construction():
    # Pressure level
    assert DataType.TH.get_identity(Level.Hpa500) == "TH_500"
    # AGL level
    assert DataType.U.get_identity(Level.H10m) == "U_10m"
    # Other/NoRule
    assert DataType.XLAT.get_identity(Level.NoRule) == "XLAT"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: FAIL (AttributeError)

- [ ] **Step 3: Implement `get_identity` logic in `DataType`**

```python
def get_identity(self, level):
    if level.is_pressure():
        return f"{self.short_name}_{level.value}" # e.g. TH_500
    if level.is_agl():
        return f"{self.short_name}_{level.value}m" # e.g. U_10m
    return self.short_name
```
(Note: Adjust `level.value` access based on actual `Level` enum implementation)

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: PASS

- [ ] **Step 5: Commit**
`git commit -m "feat: implement dynamic variable identity construction"`

---

### Task 3: Implement Active Validation

**Files:**
- Modify: `src/dlamp/utils/data_type.py`
- Test: `src/dlamp/utils/test_data_type.py`

**Interfaces:**
- Produces: `DataType.validate(data)` method.

- [ ] **Step 1: Write failing test for monotonicity validation**

```python
import numpy as np
from dlamp.utils.data_type import DataType

def test_lat_lon_validation():
    # Strictly increasing - should pass
    valid_data = np.array([10, 20, 30])
    assert DataType.XLAT.validate(valid_data) is True
    
    # Not strictly increasing - should fail
    invalid_data = np.array([10, 10, 30])
    assert DataType.XLAT.validate(invalid_data) is False
```

- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: FAIL

- [ ] **Step 3: Implement `validate` logic**

Add a `validate` method to `DataType`. Use a mapping of variable types to validation functions.

```python
def validate(self, data):
    if self in [DataType.XLAT, DataType.XLON]:
        # Check strict monotonicity
        return np.all(np.diff(data) > 0)
    return True # Default pass for other variables
```

- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest src/dlamp/utils/test_data_type.py`
Expected: PASS

- [ ] **Step 5: Commit**
`git commit -m "feat: add active validation to DataType registry"`

---

### Task 4: Update Consumers (ForecastSaver & DataCompose)

**Files:**
- Modify: `src/dlamp/analysis/forecast_saver.py`
- Modify: `src/dlamp/utils/data_compose.py`

**Interfaces:**
- Consumes: `DataType.get_identity(level)`

- [ ] **Step 1: Update `ForecastSaver` to use `get_identity`**
Replace hardcoded naming patterns (e.g., `var_type.name_{level_type.nc_key}hPa`) with `var_type.get_identity(level_type)`.

- [ ] **Step 2: Update `DataCompose` to use `get_identity`**
Replace `get_combined_key` logic with calls to `self.var_name.get_identity(self.level)`.

- [ ] **Step 3: Verify with existing model tests**
Run: `python -m pytest src/dlamp/models/architectures/unet_test.py`
Expected: PASS

- [ ] **Step 4: Commit**
`git commit -m "refactor: update consumers to use canonical registry identities"`
