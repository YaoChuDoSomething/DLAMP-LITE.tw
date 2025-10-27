# File: coupled_forecast.py
# Description: Main entry point for the one-way coupled SFNO-GFS forecast workflow.

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import xarray as xr
import yaml
from earth2studio.data import GFS, fetch_data
from earth2studio.models.px import SFNO

# Import from local project structure
from src.op.diag.diagnostics import run_diagnostics
from src.op.io.rwrf_io import save_hourly_rwrf_series
from src.op.regrid.regridding import to_rwrf_grid
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
        self.data_source: GFS = GFS()
        logger.info("Configurations and device initialized.")

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
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache/earth2studio")
        os.environ["EARTH2STUDIO_CACHE"] = cache_dir
        logger.info(f"Earth2Studio model cache is set to: {cache_dir}")
        logger.info("Model cache directory configured.")

        # API Call with full type annotations for loading the model
        package = SFNO.load_default_package()
        model = SFNO.load_model(package)
        self.model = model.to(self.device)

        logger.info("SFNO model loaded successfully and moved to target device.")

    def _fetch_initial_conditions(
        self, start_time: np.datetime64
    ) -> Tuple[torch.Tensor, Dict[str, np.ndarray]]:
        """Fetches initial conditions from the GFS data source."""
        if self.model is None:
            raise RuntimeError("Model is not set up. Call setup() first.")

        logger.info(f"Fetching initial conditions for forecast start: {start_time}")
        input_variables: List[str] = self.model.input_coords()["variable"]
        time_array = np.array([start_time])

        # API Call with full type annotations for fetching data
        x: torch.Tensor
        coords: Dict[str, np.ndarray]
        x, coords = fetch_data(
            source=self.data_source,
            time=time_array,
            variable=input_variables,
            device=self.device,
        )

        logger.info(f"Fetched data from GFS with tensor shape {x.shape}.")
        logger.info("Initial conditions successfully fetched from GFS.")
        return x, coords

    def _tensor_to_dataarray(
        self, tensor: torch.Tensor, coords: Dict[str, Any]
    ) -> xr.DataArray:
        """
        Converts an input or output tensor to a labeled xarray.DataArray,
        robustly handling different tensor dimensions.
        """
        # Squeeze leading dimensions of size 1 until the tensor is 3D
        # (variable, lat, lon)
        squeezed_tensor = tensor
        while squeezed_tensor.ndim > 3 and squeezed_tensor.shape[0] == 1:
            squeezed_tensor = squeezed_tensor.squeeze(0)

        if squeezed_tensor.ndim != 3:
            raise ValueError(
                "Tensor could not be squeezed to 3 dimensions "
                f"(variable, lat, lon). Final shape: {squeezed_tensor.shape}"
            )

        variable_names = self.model.variables
        return xr.DataArray(
            data=squeezed_tensor.cpu().numpy(),
            dims=("variable", "lat", "lon"),
            coords={
                "variable": variable_names,
                "lat": coords["lat"],
                "lon": coords["lon"],
            },
        )

    def run(self) -> None:
        """Executes the entire forecast and processing workflow."""
        self.setup()
        if self.model is None:
            raise RuntimeError("Model setup failed, cannot run forecast.")

        time_cfg = self.config["share"]["time_control"]
        start_dt = datetime.strptime(time_cfg["start"], time_cfg["format"])
        end_dt = datetime.strptime(time_cfg["end"], time_cfg["format"])
        one_step_hour = timedelta(hours=6)
        nsteps = int((end_dt - start_dt).total_seconds() // one_step_hour.total_seconds())
        start_time_np = np.datetime64(start_dt)
        logger.info(f"Forecast time range set from {start_dt} to {end_dt} for {nsteps} steps.")

        # --- PHASE 1: Data Acquisition & Inference ---
        logger.info("--- Starting Phase 1: Data Acquisition & Inference ---")
        x_ic, coords_ic = self._fetch_initial_conditions(start_time_np)

        raw_forecast_dataarrays: List[xr.DataArray] = []

        # Store initial condition (F000)
        ic_da = self._tensor_to_dataarray(x_ic, coords_ic)
        raw_forecast_dataarrays.append(ic_da)
        logger.info("Initial condition (F000) stored in raw model format.")

        # API Call for creating the forecast iterator
        model_iterator = self.model.create_iterator(x=x_ic, coords=coords_ic)
        logger.info("Forecast iterator created for sequential model inference.")
        logger.info("Starting sequential SFNO model inference.")

        for i, (x_step, coords_step) in enumerate(model_iterator):
            if i >= nsteps:
                break
            logger.info(f"Running SFNO inference for step {i + 1}/{nsteps}.")
            step_da = self._tensor_to_dataarray(x_step, coords_step)
            raw_forecast_dataarrays.append(step_da)
            logger.info(f"SFNO inference step {i + 1} completed and data stored.")

        logger.info("--- Phase 1: Inference Complete ---")

        # --- PHASE 2: Post-processing (Regrid, Transform, Diagnostics) ---
        # 1. Spatial Regridding (lat-lon grid -> RWRF south_north-west_east grid)
        # 2. Variable Transformation (Lexicon 73 -> RWRF variables with proper dimensions)
        # 3. Diagnostics (if enabled)
        # 4. Time dimension and variable preparation for RWRF format

        logger.info("--- Starting Phase 2: Post-Processing ---")
        processed_datasets_6h: List[xr.Dataset] = []
        logger.info("Beginning post-processing for 6-hourly forecast data.")
        
        # Process each 6-hourly timestep
        for i, raw_da in enumerate(raw_forecast_dataarrays):
            current_dt = np.datetime64(start_dt + i * one_step_hour)  # Use np.datetime64 consistently
            logger.info(f"Post-processing step {i} for time {current_dt}.")

            # 1. Spatial regridding to RWRF grid
            regridded_da = to_rwrf_grid(raw_da, self.config["rwrf"]["target_grid_path"])
            
            # 2. Transform variables to RWRF format (including proper dimension naming)
            rwrf_ds = transform_to_rwrf(regridded_da, self.config, self.gfs_config)
            
            # 3. Run diagnostics if enabled
            if self.config["diagnostics"]["enable"]:
                run_diagnostics(rwrf_ds, self.config["diagnostics"]["set"])
            
            # 4. Add time dimension using np.datetime64
            rwrf_ds = rwrf_ds.expand_dims(time=[current_dt])
            
            processed_datasets_6h.append(rwrf_ds)
            logger.info(f"Post-processing for time {current_dt} completed.")

        logger.info("--- Phase 2: Post-Processing Complete ---")
        logger.info("Preparing to generate final RWRF output files.")

        # --- PHASE 3: Final Output Generation ---
        if processed_datasets_6h:
            logger.info("--- Starting Phase 3: Output Generation ---")
            # Combine all 6-hourly datasets while preserving RWRF dimensions
            combined_ds = xr.concat(processed_datasets_6h, dim="time")
            logger.info("All 6-hourly datasets combined into a single xarray Dataset.")
            
            # Convert to hourly RWRF format and save individual files
            # The save_hourly_rwrf_series function handles:
            # - Linear time interpolation to hourly data
            # - RWRF-compliant file naming
            # - Proper dimension ordering (Time, pres_bottom_top, south_north, west_east)
            # - Times variable creation in RWRF format
            save_hourly_rwrf_series(
                ds6h=combined_ds,
                gattrs=self.gfs_config["share"]["global_attrs"],
                outdir=self.config["rwrf"]["output_dir"],
                bbox=self.config["rwrf"]["bbox"],
            )
            logger.info("Hourly RWRF series successfully saved to output directory.")
        else:
            logger.warning("No forecast steps were processed to save.")

        logger.info("Workflow finished successfully.")


def create_dummy_files() -> None:
    """Creates dummy config and asset files for a runnable example."""
    logger.info("Creating dummy configuration and asset files for demonstration.")
    os.makedirs("config/op/models", exist_ok=True)
    os.makedirs("config/op/data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)

    with open("config/op/models/sfno_config.yaml", "w") as f:
        yaml.safe_dump(
            yaml.safe_load("""
            model:
              name: SFNO
              variable_2d: [u10m, v10m, u100m, v100m, t2m, sp, msl, tcwv]
              variable_3d: [u, v, t, z, q]
              pressure_levels: [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
            share:
              time_control:
                start: "2023-01-01 00:00:00"
                end: "2023-01-01 12:00:00"
                format: "%Y-%m-%d %H:%M:%S"
            rwrf:
              output_dir: outputs/rwrf_processed
              target_grid_path: assets/target.nc
              bbox: {lat_min: 20.0, lat_max: 30.0, lon_min: 115.0, lon_max: 125.0}
            diagnostics: {enable: true, set: rwrf_default}
            """), f, default_flow_style=False
        )

    with open("config/op/data/gfs_config.yaml", "w") as f:
        yaml.safe_dump(
            yaml.safe_load("""
            registry:
              mappings: {u10m: U10, v10m: V10, t2m: T2, sp: PSFC, msl: MSLP, tcwv: PWAT, u: U, v: V, t: T, z: GHT, q: Q}
            share:
              global_attrs:
                model_name: "NVIDIA SFNO via Earth2Studio"
                initial_condition_source: "NOAA/NCEP GFS"
                processing_history: "Created by coupled_forecast.py workflow."
            """), f, default_flow_style=False
        )

    logger.info("Dummy files created successfully.")


if __name__ == "__main__":
    create_dummy_files()

    workflow = CoupledForecastWorkflow()
    try:
        workflow.run()
    except Exception as e:
        logger.error(f"An critical error occurred during workflow execution: {e}", exc_info=True)
