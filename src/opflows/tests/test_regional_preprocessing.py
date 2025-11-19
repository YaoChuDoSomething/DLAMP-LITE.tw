import os
import pytest
import yaml
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.opflows.manager import OpFlowsManager
from src.opflows.cds_downloader import CDSDataDownloader
from src.opflows.dlamp_regridder import DataRegridder

# Define a temporary config directory for testing
TEST_CONFIG_DIR = "src/opflows/tests/test_configs"
TEST_OUTPUT_DIR = "src/opflows/tests/test_outputs"

# --- Setup for mock configuration files ---
@pytest.fixture(scope="module", autouse=True)
def setup_test_configs():
    os.makedirs(TEST_CONFIG_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    # Mock share.yaml
    share_cfg = {
        "exp_code": "TEST_EXP",
        "data_path": "/tmp/test_data",
        "time_control": {
            "start": "2024-01-01_00:00",
            "end": "2024-01-01_00:00",
            "format": "%Y-%m-%d_%H:%M",
            "base_step_hours": 1
        },
        "io_control": {
            "base_dir": "/tmp/test_io",
            "prefix": {
                "upper": "test_upper",
                "surface": "test_surface",
                "output": "test_output",
                "timestr_fmt": "%Y%m%d_%H%M"
            }
        }
    }
    with open(os.path.join(TEST_CONFIG_DIR, "share.yaml"), "w") as f:
        yaml.safe_dump(share_cfg, f)

    # Mock download.yaml
    download_cfg = {
        "area": {
            "north": 31, "south": 17, "west": 114, "east": 128
        },
        "dataset_upper": {
            "title": "reanalysis-era5-pressure-levels",
            "variables": ["temperature"],
            "levels": [1000]
        },
        "dataset_surface": {
            "title": "reanalysis-era5-single-levels",
            "variables": ["2m_temperature"]
        },
        "output_control": {
            "output_dir": TEST_OUTPUT_DIR,
            "filename_prefix": "test_era5_merged",
            "timestr_format": "%Y%m%d_%H%M"
        }
    }
    with open(os.path.join(TEST_CONFIG_DIR, "download.yaml"), "w") as f:
        yaml.safe_dump(download_cfg, f)

    # Mock regrid.yaml
    regrid_cfg = {
        "target_nc": "assets/target.nc", # This might need a mock file or skip test if not present
        "target_lat": "XLAT",
        "target_lon": "XLONG",
        "target_pres": "pres_levels",
        "source_lat": "lat",
        "source_lon": "lon",
        "source_pres": "plev",
        "levels": [1000],
        "adopted_varlist": ["XLONG", "XLAT"],
        "write_regrid": False,
        "regrid_output_dir": TEST_OUTPUT_DIR,
        "regrid_output_prefix": "test_regrid_",
        "diagnostic_output_dir": TEST_OUTPUT_DIR
    }
    with open(os.path.join(TEST_CONFIG_DIR, "regrid.yaml"), "w") as f:
        yaml.safe_dump(regrid_cfg, f)

    # Mock registry.yaml
    registry_cfg = {
        "source_dataset": "ERA5",
        "varname": {
            "diag_t2": {"requires": ["2t"], "function": "diag_T2"}
        }
    }
    with open(os.path.join(TEST_CONFIG_DIR, "registry.yaml"), "w") as f:
        yaml.safe_dump(registry_cfg, f)

    yield # This runs the tests

    # --- Teardown: Clean up test files and directories ---
    import shutil
    if os.path.exists(TEST_CONFIG_DIR):
        shutil.rmtree(TEST_CONFIG_DIR)
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)

# --- Test cases ---
def test_opflows_manager_initialization(setup_test_configs):
    manager = OpFlowsManager(config_dir=TEST_CONFIG_DIR)
    assert manager.downloader is not None
    assert manager.regridder is not None
    assert isinstance(manager.downloader, CDSDataDownloader)
    assert isinstance(manager.regridder, DataRegridder)

# Mock CDS API call and xarray operations for process_download
@patch('src.opflows.cds_downloader.cdsapi.Client')
@patch('src.opflows.cds_downloader.xr.open_dataset')
@patch('src.opflows.cds_downloader.os.makedirs')
@patch('src.opflows.cds_downloader.os.path.exists', return_value=True) # Mock exists for output_dir
def test_regional_preprocessing_pipeline_download_only(mock_exists, mock_makedirs, mock_open_dataset, mock_cds_client, setup_test_configs):
    # Mock behavior for cdsapi.Client
    mock_cds_client.return_value.retrieve.return_value.download.return_value = None

    # Mock behavior for xr.open_dataset to return a dummy dataset
    mock_ds = MagicMock(spec=xr.Dataset)
    mock_ds.dims = {'latitude': 1, 'longitude': 1} # Mock some dimensions for sortby
    mock_ds.sortby.return_value = mock_ds
    mock_ds.to_netcdf.return_value = None
    mock_open_dataset.return_value.__enter__.return_value = mock_ds
    mock_open_dataset.return_value.__exit__.return_value = False

    manager = OpFlowsManager(config_dir=TEST_CONFIG_DIR)
    
    # Run the pipeline, but we will patch DataRegridder.main_process to do nothing
    with patch('src.opflows.dlamp_regridder.DataRegridder.main_process'):
        manager.run_regional_preprocessing_pipeline()

    mock_cds_client.return_value.retrieve.assert_called() # Check if download was attempted
    mock_open_dataset.assert_called() # Check if datasets were opened
    mock_ds.to_netcdf.assert_called_once() # Check if merged dataset was saved
