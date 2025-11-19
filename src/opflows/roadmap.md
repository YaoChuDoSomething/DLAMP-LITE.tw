# OpFlows Roadmap

This document outlines the planned development phases and goals for the `opflows` module, focusing on modularity, clear responsibility separation, and the integration of new meteorological data processing workflows.

## Current Status:
- Initial refactoring of `cds_downloader.py`, `dlamp_regridder.py`, `diagnostic_registry.py`, and `manager.py` for improved modularity and configuration handling.
- Configuration parameters are now passed as dictionaries, removing temporary file workarounds.
- Introduction of `config/opflows/share.yaml` for shared configurations.
- `dlamp_prep.py` updated to drive the regional preprocessing pipeline using the refactored `OpFlowsManager`.

## Phase 1: Regional Model Data Preprocessing Workflow (Complete)
**Goal:** Establish a robust and modular pipeline for regional model data preprocessing, including data download, spatio-temporal interpolation, and RWRF variable diagnostics.

**Components Refactored:**
- `src/opflows/cds_downloader.py`: Data Download (資料下載)
- `src/opflows/dlamp_regridder.py`: Spatio-temporal Interpolation (時空間內插)
- `src/opflows/diagnostic_registry.py`: Controls diagnostic order (控制診斷的順序)
- `src/opflows/diagnostic_functions.py`: Actual diagnostic methods (實際診斷的方法函數)
- `src/opflows/manager.py`: Central Workflow Orchestrator (流程控制 & 共同時間配置)
- `dlamp_prep.py`: Entry Script for this workflow.

**Key Achievements:**
- Clearer separation of concerns for each processing step.
- Configuration managed through dedicated YAML files and passed as dictionaries.
- Basic unit tests for `OpFlowsManager` initialization and download pipeline flow.

## Phase 2: Global Model Forecasting Workflow Integration (Next)
**Goal:** Integrate the global model forecasting capabilities, particularly driven by `src/opflows/sfno_oneway_1.py`, into the `OpFlowsManager` as a distinct workflow.

**Key Tasks:**
- **Refactor `src/opflows/sfno_oneway_1.py`**:
    - Modify its `__init__` to accept a configuration dictionary directly, similar to `CDSDataDownloader` and `DataRegridder`.
    - Adjust internal configuration access within the class.
    - Ensure it can operate independently given its specific configuration.
- **Update `src/opflows/manager.py`**:
    - Add a new method, e.g., `run_global_forecasting_pipeline()`, to orchestrate the SFNO model execution.
    - This method will initialize `sfno_oneway_1.py` with its specific configuration.
- **Create/Update `config/opflows/sfno.yaml`**:
    - Ensure it contains all necessary configurations for `sfno_oneway_1.py` to run, possibly externalizing more parameters if identified during refactoring.
- **Update `dlamp_prep.py`**:
    - Add logic to select and execute either the regional preprocessing pipeline or the global forecasting pipeline based on command-line arguments or another configuration.
- **Add Tests**:
    - Create `src/opflows/tests/test_global_forecasting.py` with basic tests for SFNO model integration and execution flow.

## Phase 3: Bidirectional Coupling and Feedback (Future)
**Goal:** Implement advanced workflows involving bidirectional coupling and feedback mechanisms between regional and global models.

**Key Considerations:**
- Defining interfaces for data exchange between different model outputs.
- Developing synchronization and feedback logic within the `OpFlowsManager`.
- Performance optimization for coupled simulations.

## Testing Strategy:
- **Unit Tests**: For individual components (`cds_downloader.py`, `dlamp_regridder.py`, `diagnostic_registry.py`, `sfno_oneway_1.py`) to ensure their logic works as expected.
- **Integration Tests**: For the overall pipelines (`run_regional_preprocessing_pipeline`, `run_global_forecasting_pipeline`) within `OpFlowsManager` to verify correct component interaction.
- **End-to-End Tests**: Executing `dlamp_prep.py` with various configurations to validate full workflow execution.

## Directory Structure (Planned):
- `src/opflows/`: Contains all Python modules for different operational flows.
    - `__init__.py`
    - `cds_downloader.py`
    - `dlamp_regridder.py`
    - `diagnostic_functions.py`
    - `diagnostic_registry.py`
    - `manager.py` (or `workflow_manager.py`)
    - `sfno_oneway_1.py`
    - `roadmap.md` (this file)
    - `tests/`: Unit and integration tests for `opflows` modules.
        - `__init__.py`
        - `test_regional_preprocessing.py`
        - `test_global_forecasting.py` (future)
- `config/opflows/`: Contains configuration YAML files for different components and workflows.
    - `share.yaml` (shared configurations like time control, base I/O)
    - `download.yaml` (CDS download specific parameters)
    - `regrid.yaml` (Regridding specific parameters)
    - `registry.yaml` (Diagnostic variable definitions)
    - `sfno.yaml` (SFNO model specific parameters, workflow, plotting)
