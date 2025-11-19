"""
Manager for orchestrating ERA5 data download, regridding, and diagnostics.

This module defines the OpFlowsManager class, which controls the workflow
for processing ERA5 data, including downloading from CDS, interpolating
to a target grid, and calculating diagnostic variables.
"""

import logging
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.opflows.cds_downloader import CDSDataDownloader
from src.opflows.dlamp_regridder import DataRegridder

# Configure logging for the module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OpFlowsManager:
    """
    Orchestrates the ERA5 data processing workflow.

    This includes downloading data from the Copernicus Data Store (CDS),
    regridding (interpolating) the data to a specified target grid,
    and calculating various diagnostic variables.

    Attributes:
        era5_config_path (str): Path to the main ERA5 configuration file.
        download_config_path (str): Path to the download-specific configuration file.
        regrid_config_path (str): Path to the regridding-specific configuration file.
        registry_config_path (str): Path to the diagnostic registry configuration file.
        _era5_cfg (Dict[str, Any]): Loaded content of the main ERA5 configuration.
        _download_cfg (Dict[str, Any]): Loaded content of the download configuration.
        _regrid_cfg (Dict[str, Any]): Loaded content of the regridding configuration.
        _registry_cfg (Dict[str, Any]): Loaded content of the registry configuration.
        downloader (CDSDataDownloader): Instance of the CDS data downloader.
        regridder (DataRegridder): Instance of the data regridder.
    """

    def __init__(
        self,
        era5_config_path: str,
        download_config_path: str,
        regrid_config_path: str,
        registry_config_path: str,
    ) -> None:
        """
        Initializes the OpFlowsManager with paths to configuration files.

        Args:
            era5_config_path (str): Path to the main ERA5 configuration file.
            download_config_path (str): Path to the download-specific configuration file.
            regrid_config_path (str): Path to the regridding-specific configuration file.
            registry_config_path (str): Path to the diagnostic registry configuration file.
        """
        self.era5_config_path = era5_config_path
        self.download_config_path = download_config_path
        self.regrid_config_path = regrid_config_path
        self.registry_config_path = registry_config_path

        self._era5_cfg = self._load_config(self.era5_config_path)
        self._download_cfg = self._load_config(self.download_config_path)
        self._regrid_cfg = self._load_config(self.regrid_config_path)
        self._registry_cfg = self._load_config(self.registry_config_path)

        # Merge configurations for downloader and regridder initialization
        # The downloader and regridder expect a single YAML structure.
        # We need to reconstruct this for their __init__ methods.
        downloader_full_cfg = {
            "share": self._era5_cfg["share"],
            "download": self._download_cfg,
        }
        regridder_full_cfg = {
            "share": self._era5_cfg["share"],
            "regrid": self._regrid_cfg,
            "registry": self._registry_cfg, # Regridder needs registry for diagnostics
        }

        # Temporarily write merged configs to pass to the initializers
        # This is a workaround because CDSDataDownloader and DataRegridder
        # currently expect a single YAML file path.
        # A better long-term solution would be to refactor CDSDataDownloader
        # and DataRegridder to accept config dictionaries directly.
        temp_downloader_config_path = "/tmp/downloader_config.yaml"
        temp_regridder_config_path = "/tmp/regridder_config.yaml"

        with open(temp_downloader_config_path, "w") as f:
            yaml.safe_dump(downloader_full_cfg, f)
        with open(temp_regridder_config_path, "w") as f:
            yaml.safe_dump(regridder_full_cfg, f)

        self.downloader = CDSDataDownloader(temp_downloader_config_path)
        self.regridder = DataRegridder(temp_regridder_config_path)

        logger.info("OpFlowsManager initialized successfully.")

    def _load_config(self, yaml_path: str) -> Dict[str, Any]:
        """
        Loads a YAML configuration file.

        Args:
            yaml_path (str): The path to the YAML file.

        Returns:
            Dict[str, Any]: The loaded configuration as a dictionary.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        try:
            with open(yaml_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {yaml_path}")
            raise e
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {yaml_path}: {e}")
            raise e

    def run_regional_preprocessing_pipeline(self) -> None: # New method
        """
        Executes the regional model data preprocessing pipeline.
        This pipeline involves downloading data, regridding, and calculating diagnostics.
        """
        logger.info("Starting regional model data preprocessing pipeline.")
        # Download data
        logger.info("Initiating data download...")
        timeline = self.downloader.create_timeline()
        for curr_time in timeline:
            logger.info(f"Downloading data for: {curr_time}")
            self.downloader.process_download(curr_time)
        logger.info("Data download completed.")

        # Regrid and calculate diagnostics
        logger.info("Initiating data regridding and diagnostic calculation...")
        self.regridder.main_process()
        logger.info("Data regridding and diagnostic calculation completed.")
        logger.info("Regional model data preprocessing pipeline completed.")

    def run_regridding_pipeline(self) -> None:
        """
        Executes the data regridding and diagnostic calculation pipeline.
        """
        logger.info("Starting data regridding and diagnostic pipeline.")
        self.regridder.main_process()
        logger.info("Data regridding and diagnostic pipeline completed.")

    def run_full_pipeline(self) -> None:
        """
        Executes the full data processing pipeline: download, regridding, and diagnostics.
        """
        logger.info("Starting full data processing pipeline.")
        self.run_download_pipeline()
        self.run_regridding_pipeline()
        logger.info("Full data processing pipeline completed.")
