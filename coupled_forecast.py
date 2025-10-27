# coupled_forecast.py
# File: coupled_forecast.py
# Description: Main entry point for the one-way coupled SFNO-GFS forecast workflow.

import asyncio
import logging
import os
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import xarray as xr
import yaml
from earth2studio.data import GFS, fetch_data
from earth2studio.io import NetCDF4Backend
from earth2studio.models.px import SFNO

# Import from local project structure
from src.op.diag.diagnostics import run_diagnostics
from src.op.io.rwrf_io import save_hourly_rwrf_series
from src.op.regrid.regridding import to_rwrf_grid
from src.op.utils.time_interp import to_hourly_linear
from src.op.utils.variables_conversion import transform_to_rwrf

# Module-level logger setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


class CoupledForecastWorkflow:
    """
    Manages and executes a coupled SFNO-GFS weather forecast workflow.
    This class handles configuration loading, model setup, data fetching,
    forecast execution, and post-processing into an RWRF-compatible format.
    """

    def __init__(
        self,
        config_path: str = "config/op/models/sfno_config.yaml",
        gfs_config_path: str = "config/op/data/gfs_config.yaml",
    ):
        """Initializes the workflow by loading configurations."""
        logger.info("Initializing CoupledForecastWorkflow.")
        self.config: Dict[str, Any] = self._load_yaml(config_path)
        self.gfs_config: Dict[str, Any] = self._load_yaml(gfs_config_path)
        self.device: torch.device = self._get_device()
        self.model: Optional[SFNO] = None
        # Data source can be configured here if needed, defaults to GFS.
        self.data_source: GFS = GFS()

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Loads a YAML configuration file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found at: {path}")
            raise

    def _get_device(self) -> torch.device:
        """Selects and logs the torch device for model inference."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Inference will run on device: {device}")
        return device

    def setup(self) -> None:
        """Sets up the SFNO model for the workflow."""
        logger.info("Setting up the SFNO prognostic model.")
        # Earth2Studio uses a cache directory for model weights.
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache/earth2studio")
        os.environ["EARTH2STUDIO_CACHE"] = cache_dir
        logger.info(f"Earth2Studio model cache is set to: {cache_dir}")

        package = SFNO.load_default_package()
        self.model = SFNO.load_model(package).to(self.device)
        logger.info("SFNO model loaded successfully and moved to target device.")
        logger.info(
            "🚨 USAGE ALERT: Verify the function name, parameter order, and "
            "expected input/output format for 'SFNO.load_model'. Refer to the "
            "official Earth2Studio documentation."
        )

    async def _fetch_initial_conditions(
        self, start_time: np.datetime64
    ) -> Tuple[torch.Tensor, Dict[str, np.ndarray]]:
        """Fetches initial conditions from the GFS data source."""
        if self.model is None:
            raise RuntimeError("Model is not set up. Call setup() first.")

        logger.info(f"Fetching initial conditions for forecast start: {start_time}")
        input_variables: list[str] = self.model.variables
        coords: Dict[str, np.ndarray] = self.model.input_coords()
        time_array = np.array([start_time])

        # API Call with full type annotations
        x: torch.Tensor
        coords: Dict[str, np.ndarray]
        x, coords = fetch_data(
            source=self.data_source,
            time=time_array,
            variable=input_variables,
        )

        logger.info(
            f"Fetched data from GFS with tensor shape {x.shape}."
        )
        logger.info(
            "🚨 USAGE ALERT: Verify the function name, parameter order, and "
            "expected input/output format for 'earth2studio.data.fetch_data'. "
            "Refer to the official Earth2Studio documentation."
        )
        return x, coords

    def _tensor_to_dataarray(
        self,
        tensor: torch.Tensor,
        coords: Dict[str, Any],
        variable_names: List[str],
    ) -> xr.DataArray:
        """Converts an output tensor to a labeled xarray.DataArray."""
        if tensor.shape[0] != 1:
            raise ValueError(f"Expected batch size of 1, but got {tensor.shape[0]}")

        return xr.DataArray(
            data=tensor.squeeze(0).cpu().numpy(),
            dims=("variable", "lat", "lon"),
            coords={
                "variable": variable_names,
                "lat": coords["lat"],
                "lon": coords["lon"],
            },
        )

    async def run(self) -> None:
        """Executes the entire forecast and processing workflow."""
        self.setup()
        if self.model is None:
            raise RuntimeError("Model setup failed, cannot run forecast.")

        # Extract configuration parameters
        time_cfg = self.config["share"]["time_control"]
        start_dt = datetime.strptime(time_cfg["start"], time_cfg["format"])
        end_dt = datetime.strptime(time_cfg["end"], time_cfg["format"])
        one_step_hour = 6
        nsteps = int((end_dt - start_dt).total_seconds() / (3600 * one_step_hour))
        start_time_np = np.datetime64(start_dt)

        # Fetch initial conditions
        x_ic, coords_ic = await self._fetch_initial_conditions(start_time_np)
        
        rwrf_datasets_6h = []

        # Process initial condition (Forecast hour 0)
        logger.info("Processing initial condition (F000).")
        ic_da = self._tensor_to_dataarray(
            x_ic, coords_ic, self.model.input_coords()["variable"]
        )
        
        # Post-process for RWRF compatibility
        regridded_ic = to_rwrf_grid(ic_da, self.config["rwrf"]["target_grid_path"])
        rwrf_ic_ds = transform_to_rwrf(regridded_ic, self.config, self.gfs_config)
        
        if self.config["diagnostics"]["enable"]:
            run_diagnostics(rwrf_ic_ds, self.config["diagnostics"]["set"])
        
        rwrf_datasets_6h.append(rwrf_ic_ds.expand_dims(time=[start_dt]))
        
        # Run forecast iterator
        logger.info(f"Starting forecast for {nsteps} steps of {one_step_hour} hours each.")
        model_iterator = self.model.create_iterator(x_ic, coords_ic)
        logger.info(
            "🚨 USAGE ALERT: Verify the function name, parameter order, and "
            "expected input/output format for 'model.create_iterator'. "
            "Refer to the official Earth2Studio documentation."
        )

        for i, (x_step, coords_step) in enumerate(model_iterator):
            if i >= nsteps:
                break
            
            current_dt = start_dt + (i + 1) * self.model.time_step
            logger.info(f"Processing forecast step {i + 1}/{nsteps} for time {current_dt}.")

            step_da = self._tensor_to_dataarray(
                x_step, coords_step, self.model.output_coords()["variable"]
            )
            
            regridded_step = to_rwrf_grid(step_da, self.config["rwrf"]["target_grid_path"])
            rwrf_step_ds = transform_to_rwrf(regridded_step, self.config, self.gfs_config)

            if self.config["diagnostics"]["enable"]:
                run_diagnostics(rwrf_step_ds, self.config["diagnostics"]["set"])
            
            rwrf_datasets_6h.append(rwrf_step_ds.expand_dims(time=[current_dt]))

        logger.info("Forecast iteration complete.")

        # Final RWRF output generation
        if rwrf_datasets_6h:
            combined_ds = xr.concat(rwrf_datasets_6h, dim="time")
            
            save_hourly_rwrf_series(
                ds6h=combined_ds,
                var_map=self.gfs_config["registry"]["mappings"],
                gattrs=self.gfs_config["share"]["global_attrs"],
                outdir=self.config["rwrf"]["output_dir"],
                bbox=self.config["rwrf"]["bbox"],
            )
        else:
            logger.warning("No forecast steps were processed to save.")

        logger.info("Workflow finished successfully.")


if __name__ == "__main__":

    target_grid_path = "assets/target_grid.nc"
    if not os.path.exists(target_grid_path):
        target_ds = xr.Dataset(
            coords={
                "XLAT": (("y", "x"), np.random.rand(50, 50) * 10 + 20),
                "XLONG": (("y", "x"), np.random.rand(50, 50) * 10 + 115),
            }
        )
        target_ds.to_netcdf(target_grid_path)
        logger.info(f"Dummy target grid created at: {target_grid_path}")

    workflow = CoupledForecastWorkflow()
    try:
        # Execute the asynchronous run method.
        asyncio.run(workflow.run())
    except Exception as e:
        logger.error(f"An critical error occurred during workflow execution: {e}", exc_info=True)
