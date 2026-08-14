# Canonical Variable Registry Design Spec

**Date:** 2026-08-14
**Status:** Finalized
**Scope:** Refactoring `src/dlamp/utils/data_type.py` and its consumers to implement a deep registry for atmospheric variables.

## 1. Purpose
To replace the shallow `DataType` Enum with an active registry that provides a single source of truth for variable identities, storage keys, CF-standard semantics, and domain-specific validation. This removes "magic" string manipulation from orchestration modules and concentrates variable logic within the registry.

## 2. Domain Model

### 2.1 Variable Identity
The registry defines a stable identity for every meteorological quantity, regardless of its source or storage format.

- **Identity**: Defined by the `enum` member or `short_name`.
- **Storage Key**: The `nc_key` used to retrieve the variable from NetCDF datafiles.
- **Semantic Description**: A description following CF-Conventions.

### 2.2 Coordinate Systems & Naming
Identifiers for variables are constructed dynamically based on the coordinate system to ensure unambiguous mapping in output files and internal lookups.

| Coordinate System | Naming Pattern | Example |
| :--- | :--- | :--- |
| **Pressure Levels** | `{shortname}_{pressure_in_hPa}` | `TH_500` |
| **AGL (Above Ground)** | `{shortname}_{height_above_ground}m` | `U_10m` |
| **Other / Global** | `{shortname}` | `XLAT` |

### 2.3 Domain Truths
- **Axis vs. Field**: `Lat`/`Lon` (1D coordinate axes) are conceptually distinct from `XLAT`/`XLON` (2D distributions). For this implementation, only `XLAT`/`XLON` (2D) are utilized.
- **Potential Temperature**: The variable `TK` is renamed to `TH`. It is treated as a distinct physical quantity provided via preprocessed `th_p` files.

## 3. Architecture

### 3.1 The Deepened `DataType` Registry
The `DataType` Enum is expanded to include the following attributes and methods:

- **Attributes**:
  - `short_name`: Stable identity used by the model and encoder.
  - `description`: CF-Convention compliant description.
  - `nc_key`: The field key in the source NetCDF file.
- **Methods**:
  - `get_identity(level)`: Returns the formatted identity string based on the naming patterns in Section 2.2.
  - `validate(data)`: Enforces domain-specific constraints. For `XLAT`/`XLON`, it verifies strict monotonicity.

### 3.2 Integration Points
- **`DataCompose`**: Instead of calculating combined keys via string manipulation, it calls `self.var_name.get_identity(self.level)`.
- **`ForecastSaver`**: Uses `get_identity(level)` to name output variables in NetCDF files.
- **`DataProvider`**: Calls `var.validate(data)` during the loading process to ensure data integrity.

## 4. Constraints & Requirements
- **No Backward Compatibility**: Legacy alias layers are removed. All configs must be updated to canonical names.
- **Strict Monotonicity**: `XLAT` and `XLON` must be strictly increasing.
- **External Logic**: The conversion of temperature to potential temperature ($\theta$) is handled in `dlamp-data` (preprocessing); the registry only manages the resulting `TH` identity.
