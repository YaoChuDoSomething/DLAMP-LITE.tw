#!/bin/python

###===== Workflow Control ===========================================###
#
###==================================================================###
import logging
from src.opflows.manager import OpFlowsManager

# Configure logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define configuration paths
ERA5_CONFIG_PATH = "config/era5.yaml"
DOWNLOAD_CONFIG_PATH = "config/opflows/download.yaml"
REGRID_CONFIG_PATH = "config/opflows/regrid.yaml"
REGISTRY_CONFIG_PATH = "config/registry.yaml" # This was previously config/era5.yaml, but now it's a separate file

# Initialize and run the OpFlowsManager
if __name__ == "__main__":
    logger.info("Initializing OpFlowsManager...")
    manager = OpFlowsManager(
        era5_config_path=ERA5_CONFIG_PATH,
        download_config_path=DOWNLOAD_CONFIG_PATH,
        regrid_config_path=REGRID_CONFIG_PATH,
        registry_config_path=REGISTRY_CONFIG_PATH,
    )
    logger.info("OpFlowsManager initialized. Running full pipeline...")
    manager.run_full_pipeline()
    logger.info("Full pipeline execution completed.")