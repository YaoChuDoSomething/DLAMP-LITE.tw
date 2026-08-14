# DLAMP Weather Forecasting

Domain model for the Deep Learning Atmospheric Modeling Pipeline (DLAMP) — a PyTorch-based weather forecasting system that produces gridded atmospheric forecasts from reanalysis inputs.

## Language

### Core Concepts

**Forecast**:
A gridded atmospheric state prediction at a specific valid time, produced by the model. Distinct from *ground truth* (reanalysis).

**Prediction**:
Synonym for *forecast*. Used in code paths (`PredictionRunner`, `predict_step`).

**Reanalysis**:
Observationally constrained historical atmospheric data used as ground truth (e.g., ERA5, E2S). Also called *analysis* or *truth*.

**Variable**:
A meteorological quantity (temperature, wind components, moisture, etc.). Each has a unique `DataType` enum member with a NetCDF key and short code. Examples: `TK` (temperature), `UM`/`VM` (u/v wind), `Qt` (total hydrometeors), `PH` (geopotential height).

**Pressure Level**:
A constant-pressure vertical coordinate (e.g., 500 hPa, 850 hPa). Represented by `Level` enum. Upper-air variables exist at multiple pressure levels; surface variables do not.

**Surface Level**:
A vertical coordinate at or near the ground (2 m, 10 m, surface, sea surface, lowest model level). Represented by `Level` enum members where `is_surface()` returns true.

**Data Composition**:
A variable–level pair (e.g., `TK@Hpa500`, `PSFC@Surface`). The atomic unit of data I/O and standardization. String form: `"var@level"`.

**Model Code** (or **Experiment Code**):
The `DLAMP_EXP_CODE` environment variable (e.g., `20250729`). Selects the model version, which determines the standardization statistics file and the data config YAML. A mismatch silently loads wrong normalization — now fails fast via `RuntimeConfig`.

**Data Source**:
The origin of reanalysis inputs: `OP_ERA5`, `OP_E2S`, `CWA_RWRF`, `NEO171_RWRF`. Controls file naming convention and reading logic.

**Standardization**:
Per-variable z-score normalization (mean/std) applied during data loading. Statistics are precomputed per model code and stored in `assets/standardization/z_score_3h_{code}.json`. `Qt` uses log-transform: `log(array * 1e5 + 1)`.

**Standardizer**:
The module (`standardizer.py`) that loads statistics once and provides `standardize()` (per-variable, input side) and `destandardize()` (full stacked array, output side) through a single shared seam.

### Temporal Concepts

**Initial Time** (or **Start Time**):
The analysis time from which the forecast is initialized (the "00-hour" time).

**Valid Time**:
The calendar time for which the forecast is valid. `valid_time = initial_time + lead_time`.

**Lead Time** (or **Forecast Step**):
The forecast horizon in hours. `F000H` = initial time (ground truth), `F001H` = 1-hour forecast, etc. Indexed 0-based in arrays.

**Output Interval**:
The temporal spacing between saved forecast steps (configurable, e.g., 1 hour).

**Auto-regressive Inference**:
Iterative prediction where the model's output at step *t* becomes the input at step *t+1*. The core inference loop for both training and operational prediction.

**Time Features**:
Cyclical encodings of day-of-year and time-of-day injected as 4 additional surface input channels (sin/cos DoY, sin/cos ToD).

### Post-Processing

**Boundary Swapping** (or **Boundary Feedback**):
A technique that blends the model's boundary region with reanalysis data to reduce edge artifacts. Methods: `override`, `linear`, `exp_decay`, `fft_tukey`, `fft_tukey0`.

**Boundary Feedback Inference**:
A two-way coupling mode where reanalysis observations are re-injected at every model step (vs. one-way downscaling where they are only used at initialization).

### Static Assets

**Land-Sea Mask**:
Binary grid (1 = land, 0 = sea) derived from terrain height > 0.5. Stored as `land_sea_mask_4km.npy`.

**Topography Mask** (or **Terrain Mask**):
Terrain height grid in meters. Stored as `topography_mask_4km.npy`.

**County Shapefile**:
Taiwan administrative boundaries for plotting (`COUNTY_MOI_1090820.shp`).

### Evaluation

**Evaluation Case**:
A specific historical weather event (typhoon, front, etc.) with a known initial time, reserved for qualitative assessment. Defined in `EVAL_CASES` by category: `one_day`, `three_days`, `five_days`, `seven_days`.

**Blacklist**:
Datetimes excluded from training/validation due to missing or corrupted data files. Stored in `assets/blacklist_rwrf_3h.txt`.

### Model Architecture

**Pangu**:
The 3D transformer-based architecture (encoder-decoder with Earth-specific attention) for deterministic forecasting.

**Glide** (or **Diffusion Model**):
The conditional diffusion U-Net architecture for probabilistic forecasting. Uses DDPM or DDIM sampling.

**Backbone**:
The core neural network module (e.g., `PanguModel`, `GlideUNet`) distinct from the Lightning wrapper.

**Lightning Module**:
The `LightningModule` subclass that wraps the backbone, adds loss/optimizer/logging, and defines `training_step`, `validation_step`, `predict_step`.

### Data Flow

**Data Generator**:
The utility (`DataGenerator`) that reads NetCDF files, extracts variable/level data, and yields numpy arrays for a given datetime and `DataCompose`.

**Data Manager** (training):
`DataManager` (in `managers/data_manager.py`) orchestrates `DatetimeManager`, `DataGenerator`, and `CustomDataset` to produce PyTorch `DataLoader`s.

**Datetime Manager**:
Builds the initial time list, applies sanity checks (file existence), splits into train/valid/test, and constructs evaluation cases.

**Custom Dataset**:
PyTorch `Dataset` that yields standardized input/target pairs for a given initial time index.

**Inference Machine** (operational):
`BatchInferenceOnnx` or `BatchInferenceCkpt` runs the auto-regressive loop, applies boundary swapping, and collects predictions.

**Prediction Runner**:
High-level orchestrator (`PredictionRunner`) that wires the inference machine, data manager, and post-processing.

### Output

**Analysis Plot**:
A 12-panel figure comparing forecast vs. ground truth across variables/levels (wind, vorticity, theta-e, hydrometeors, etc.) at a specific lead time.

**NetCDF Forecast**:
WRF-compatible NetCDF file per forecast step, containing all variables at their native levels with CF-convention attributes.

### Avoid List

| Term | Avoid |
|------|-------|
| **Prediction** (as distinct from Forecast) | Use **Forecast** for the product, **Prediction** only in code identifiers |
| **Analysis** (as synonym for Reanalysis) | Use **Reanalysis** for data, **Analysis Plot** for the figure |
| **Level** (unqualified) | Say **Pressure Level** or **Surface Level** |
| **Config** (unqualified) | Say **Runtime Config** (env-driven), **Hydra Config** (YAML), or **Data Config** (train data YAML) |
| **Standardization** (the stats file) | Say **Standardization Statistics** or **Standardization JSON** |
| **Model** (unqualified) | Say **Backbone** (nn.Module), **Lightning Module**, or **Model Code** (experiment ID) |
| **Eval** | Say **Evaluation Case** |
| **Boundary** (unqualified) | Say **Boundary Swapping** (technique) or **Boundary Region** (spatial extent) |

### Subheadings

- **Core Concepts**: Forecast, Reanalysis, Variable, Pressure Level, Surface Level, Data Composition
- **Model Identity**: Model Code, Data Source
- **Preprocessing**: Standardization, Standardizer
- **Temporal**: Initial Time, Valid Time, Lead Time, Output Interval, Auto-regressive Inference, Time Features
- **Post-Processing**: Boundary Swapping, Boundary Feedback Inference
- **Static Assets**: Land-Sea Mask, Topography Mask, County Shapefile
- **Evaluation**: Evaluation Case, Blacklist
- **Architecture**: Pangu, Glide, Backbone, Lightning Module
- **Data Flow**: Data Generator, Data Manager, Datetime Manager, Custom Dataset, Inference Machine, Prediction Runner
- **Output**: Analysis Plot, NetCDF Forecast