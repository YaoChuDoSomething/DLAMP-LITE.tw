#!/bin/python

###===== Workflow Control ===========================================###
#
###==================================================================###
import logging
from src.opflows.manager import OpFlowsManager

# Configure logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the base directory for all workflow configuration files
OPFLOWS_CONFIG_DIR = "config/opflows"

# Initialize and run the OpFlowsManager
if __name__ == "__main__":
    logger.info("Initializing OpFlowsManager for Regional Preprocessing Workflow...")
    manager = OpFlowsManager(config_dir=OPFLOWS_CONFIG_DIR) # Pass config_dir directly
    logger.info("OpFlowsManager initialized. Running regional preprocessing pipeline...")
    manager.run_regional_preprocessing_pipeline() # Call the specific pipeline
    logger.info("Regional preprocessing pipeline execution completed.")