# sfno_oneway.py

# deterministic_inference.py

import os
import re
from collections import OrderedDict
from datetime import datetime, timedelta # Added timedelta
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import torch
import xarray as xr
import yaml
from earth2studio.data import CDS, GFS, fetch_data
from earth2studio.io import NetCDF4Backend
from earth2studio.models.px import SFNO
from earth2studio.utils.coords import map_coords, split_coords
from earth2studio.utils.time import to_time_array
from loguru import logger
from tqdm import tqdm

#To-Do:
# 1. SFNO should produce the results for 6-hourly data in separated netCDF4 archives.
# 2. The hourly data in format netCDF4 => By interpolation to get the missing data interval

def _find_level_dim(ds: xr.Dataset, candidates: list[str] = None) -> str:
    """Return first matching vertical level dimension name or None."""
    if candidates is None:
        candidates = ['level', 'plev', 'pressure', 'isobaric']
    for c in candidates:
        if c in ds.dims:
            return c
    return None

def _parse_level_from_name(name: str) -> tuple[str, int]:
    """Try to split variable name into (base, level).
    returns (base, level) if matched, otherwise (None, None).

    Examples:
      't_1000' -> ('t', 1000)
      'temp-850' -> ('temp', 850)
      'q925' -> ('q', 925)
    """
    # common patterns: suffix with underscore or dash or trailing digits
    m = re.match(r'^(?P<base>.+?)[_\-]?((plev)?(?P<lvl>\d{2,4})|(?P<lvl2>\d{2,4}))$', name)
    if not m:
        return None, None
    base = m.group('base')
    lvl = m.group('lvl') or m.group('lvl2')
    if lvl is None:
        return None, None
    try:
        return base.rstrip('_-'), int(lvl)
    except ValueError:
        return None, None

def merge_vertical_layers(ds: xr.Dataset, level_dim_name: str = "level") -> xr.Dataset:
    """Merge variables that represent the same physical quantity at different pressure levels
    into a single variable along a vertical 'level' coordinate.

    - If a variable already has a vertical dimension (e.g., 'plev', 'level'), it will be normalized
      to the requested `level_dim_name`.
    - If multiple variables share the same base name with a numeric suffix indicating level
      (e.g., t_1000, t_925), they will be stacked (sorted by numeric level).
    Returns a new Dataset (does not modify input in-place).
    """
    ds = ds.copy()  # work on a copy to avoid in-place surprises

    # 1. Normalize existing vertical-dim variables
    existing_level_dim = _find_level_dim(ds)
    if existing_level_dim and existing_level_dim != level_dim_name:
        # rename dimension and coordinate
        ds = ds.rename({existing_level_dim: level_dim_name})
        if existing_level_dim in ds.coords:
            ds = ds.rename({existing_level_dim: level_dim_name})

    # 2. Group variables that use suffixes to indicate levels
    var_names = list(ds.data_vars.keys())
    groups = {}  # base -> list of (varname, level)
    for v in var_names:
        base, lvl = _parse_level_from_name(v)
        if base is not None and lvl is not None:
            groups.setdefault(base, []).append((v, lvl))

    # For each group with >1 member, create stacked variable
    for base, entries in groups.items():
        if len(entries) < 2:
            continue  # nothing to merge

        # sort by level (ascending). You may want descending depending on convention.
        entries_sorted = sorted(entries, key=lambda x: x[1])

        stacked_arrays = []
        levels = []
        for varname, lvl in entries_sorted:
            da = ds[varname]
            # ensure spatial & temporal dims order is consistent; we'll align via broadcast/transpose
            stacked_arrays.append(da)
            levels.append(lvl)

        # align all arrays (will broadcast if needed)
        stacked_aligned = xr.align(*stacked_arrays, join='override', copy=False)

        # expand each to include the new level dim (so stacking is straightforward)
        expanded = []
        for da in stacked_aligned:
            # ensure the DataArray has the same dims order - insert level as new axis
            # target dims: existing dims + (level_dim_name,)
            # new_dims = list(da.dims) + [level_dim_name]
            # add singleton level dimension
            da_exp = da.expand_dims({level_dim_name: [0]}, axis=len(da.dims))
            expanded.append(da_exp)

        # concat along level dimension
        combined = xr.concat(expanded, dim=level_dim_name)
        # set level coordinate to actual pressure values (int)
        combined = combined.assign_coords({level_dim_name: (f"{level_dim_name}", levels)}) \
                           .assign_coords({level_dim_name: levels})  # ensure simple coord

        # name the combined variable as base (replace existing if present)
        # if base already exists in ds, choose a safe name (base + "_vstack")
        target_name = base
        if target_name in ds.data_vars:
            target_name = f"{base}_vstack"

        combined.name = target_name

        # drop original per-level variables
        ds = ds.drop([v for v, _ in entries_sorted])

        # insert combined variable into dataset
        ds[target_name] = combined

    # 3. If there's any variable that already had vertical dimension but different name,
    #    ensure its coord is named properly (make sure level is numeric and sorted)
    if level_dim_name in ds.dims:
        try:
            lev_coord = ds.coords.get(level_dim_name)
            # if coordinate values are strings, try converting to numeric
            if lev_coord is not None and lev_coord.dtype.kind in {'U', 'S', 'O'}:
                try:
                    ds = ds.assign_coords({level_dim_name: [int(x) for x in lev_coord.values]})
                except Exception:
                    pass
            # sort level ascending
            ds = ds.sortby(level_dim_name)
        except Exception:
            pass

    return ds


class ModelLoader:
    """Handles ML model loading and device placement."""
    def __init__(self):
        self.device = self._get_device()
        self.model = self._load_model()

    def _get_device(self) -> torch.device:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        return device

    def _load_model(self):
        logger.info("Loading SFNO model package...")
        package = SFNO.load_default_package()
        model = SFNO.load_model(package)
        model = model.to(self.device)
        logger.success("Model loaded and moved to device")
        return model

class DataSource:
    """Manages data fetching from specified sources."""
    def __init__(self, source_name: str):
        self.source = self._get_source(source_name)

    def _get_source(self, name: str):
        if name.upper() == "GFS":
            logger.info("Using GFS data source")
            return GFS()
        if name.upper() == "CDS":
            logger.info("Using CDS data source")
            return CDS()
        raise ValueError(f"Unsupported data source: {name}")

    def fetch(self, model, init_time: list[datetime], device: torch.device):
        logger.info(f"Fetching initial conditions for {init_time[0]}")
        model_ic = model.input_coords()
        time_array = to_time_array(init_time)

        interp_to = model_ic if hasattr(model, "interp_method") else None
        interp_method = getattr(model, "interp_method", "nearest")

        x, coords = fetch_data(
            source=self.source,
            time=time_array,
            variable=model_ic["variable"],
            lead_time=model_ic["lead_time"],
            device=device,
            interp_to=interp_to,
            interp_method=interp_method,
        )
        logger.success(f"Fetched data from {self.source.__class__.__name__}")
        return x, coords

class OutputHandler:
    """Handles writing output files."""
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.combined_output_file = os.path.join(output_dir, "combined_forecast.nc")
        os.makedirs(self.output_dir, exist_ok=True)

    def save_timestep(self, ds_step: xr.Dataset, init_time: np.datetime64, lead_time: np.timedelta64):
        """Saves a single timestep to a separate NetCDF file."""
        valid_time = init_time + lead_time
        # Convert numpy.datetime64 to a Python datetime object for formatting
        valid_time_dt = valid_time.astype('datetime64[s]').astype(datetime)
        timestamp_str = valid_time_dt.strftime('%Y%m%d_%H')
        output_filename = os.path.join(self.output_dir, f"sfno_gfs_{timestamp_str}.nc")

        ds_step.to_netcdf(output_filename)
        logger.success(f"Saved timestep to {output_filename}")

    def process_and_save(self, hourly: bool = False):
        """Reads the combined forecast file, optionally interpolates to hourly data,
        and saves each timestep to a separate file.
        """
        logger.info(f"Processing combined forecast file: {self.combined_output_file}")
        try:
            with xr.open_dataset(self.combined_output_file) as ds:
                if hourly:
                    logger.info("Performing hourly interpolation...")
                    # Get the total forecast duration in hours, assuming lead_time is in hours
                    total_hours = int(ds['lead_time'][-1].values)
                    # Create a new lead_time coordinate with 1-hour intervals as integers
                    hourly_lead_time = np.arange(total_hours + 1)
                    # Interpolate the dataset to the new hourly coordinate
                    ds = ds.interp(lead_time=hourly_lead_time, method="linear")
                    logger.success("Interpolation to hourly data complete.")

                ds = merge_vertical_layers(ds, level_dim_name="level")

                init_time = ds["time"].values[0]
                lead_times = ds["lead_time"].values

                logger.info(f"Saving {len(lead_times)} timesteps...")
                for i, lead_time_val in enumerate(tqdm(lead_times, desc="Saving timesteps")):
                    ds_step = ds.isel(lead_time=i)
                    # Create a valid timedelta object for the save_timestep function
                    lead_time_td = np.timedelta64(int(lead_time_val), 'h')
                    self.save_timestep(ds_step, init_time, lead_time_td)
        except FileNotFoundError:
            logger.error(f"Combined forecast file not found: {self.combined_output_file}")
            raise

class InferenceEngine:
    """Orchestrates the deterministic inference workflow."""
    def __init__(self, config: dict[str, Any]):
        self.params = config
        self.model_loader = ModelLoader()
        self.data_source = DataSource(self.params.get("datasource", "GFS"))
        self.output_handler = OutputHandler(self.params.get("output_dir", "outputs"))
        self.io_backend = NetCDF4Backend(
            file_name=self.output_handler.combined_output_file,
            backend_kwargs={"mode": "w"}
        )

    def _prepare_io(self, model, time_array: np.ndarray, nsteps: int):
        total_coords = model.output_coords(model.input_coords()).copy()
        for key, value in list(total_coords.items()):
            if value.shape == (0,):
                del total_coords[key]

        total_coords["time"] = time_array
        total_coords["lead_time"] = np.asarray(
            [model.output_coords(model.input_coords())["lead_time"] * i for i in range(nsteps + 1)]
        ).flatten()
        total_coords.move_to_end("lead_time", last=False)
        total_coords.move_to_end("time", last=False)

        var_names = total_coords.pop("variable")
        self.io_backend.add_array(total_coords, var_names)
        logger.info("I/O backend prepared.")

    def run(self):
        nsteps = self.params["nsteps"]
        init_time_str = self.params["init_time"]
        time_format = self.params["time_format"]
        init_time = [datetime.strptime(init_time_str, time_format)]

        model = self.model_loader.model
        device = self.model_loader.device

        x, coords = self.data_source.fetch(model, init_time, device)

        self._prepare_io(model, to_time_array(init_time), nsteps)

        x, coords = map_coords(x, coords, model.input_coords())

        iterator = model.create_iterator(x, coords)

        logger.info("Inference starting!")
        with tqdm(total=nsteps + 1, desc="Running inference") as pbar:
            for step, (x_step, coords_step) in enumerate(iterator):
                x_out, coords_out = map_coords(x_step, coords_step, OrderedDict({}))
                self.io_backend.write(*split_coords(x_out, coords_out))
                pbar.update(1)
                if step == nsteps:
                    break

        logger.success("Inference complete.")

        # The splitting will be handled by the main function after interpolation.
        # self.output_handler.split_forecast_to_timesteps()

class Plotter:
    """Handles plotting of the forecast results."""
    def __init__(self, config: dict[str, Any], output_dir: str, init_time: datetime): # Added init_time
        self.params = config
        self.output_dir = output_dir
        self.init_time = init_time # Store init_time

    def plot(self):
        if not self.params.get("enabled", False):
            logger.info("Plotting is disabled in the configuration.")
            return

        variables = self.params.get("variables", []) # Use .get with default empty list
        roi = self.params.get("roi", []) # Use .get with default empty list
        colormap = self.params.get("colormap", "Spectral_r") # Use .get with default

        # This assumes the combined file exists and is accessible via the backend
        combined_file = os.path.join(self.output_dir, "combined_forecast.nc")

        try:
            with xr.open_dataset(combined_file) as ds:
                logger.info("Starting post-processing plots...")
                for step in range(len(ds['lead_time'])):
                    for var in variables: # Loop over configured variables
                        plt.close("all")
                        fig, ax = plt.subplots(figsize=(10, 6))

                        lead_time_hours = int(ds['lead_time'][step].values)
                        
                        plot_title_time = self.init_time + timedelta(hours=lead_time_hours)
                        plot_title = f"{plot_title_time.strftime('%Y-%m-%d %H:%M')} - {var.upper()} - Lead time: {lead_time_hours}hrs"

                        im = ax.pcolormesh(
                            ds["lon"][:],
                            ds["lat"][:],
                            ds[var].isel(time=0, lead_time=step),
                            cmap=colormap, # Use configured colormap
                        )

                        if roi and len(roi) == 4: # Check if roi is not empty and has 4 elements
                            ax.axis(roi)

                        ax.set_title(plot_title) # Use generated plot_title
                        plt.colorbar(im, ax=ax)

                        plot_filename = os.path.join(self.output_dir, f"{var}_f{lead_time_hours:03d}H.png")
                        plt.savefig(plot_filename)
                        logger.success(f"Saved plot: {plot_filename}")

        except FileNotFoundError:
            logger.error(f"Cannot generate plots. Combined forecast file not found: {combined_file}")
        except Exception as e:
            logger.error(f"An error occurred during plotting: {e}")


def main():
    """Main function to run the workflow."""
    logger.remove()
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

    config_path = "config/sfno.yaml"
    try:
        # Step 1: Load config
        logger.info(f"Loading configuration from {config_path}")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.success("Configuration loaded successfully")

        # Step 2: Parse parameters
        time_control = config["share"]["time_control"] # Access time_control under 'share'
        workflow_config = config["workflow"] # New workflow section
        plotting_config = config.get("plotting", {}) # New plotting section

        start_time_str = time_control['start']
        time_format = time_control['format']
        
        start_time_dt = datetime.strptime(start_time_str, time_format)
        end_time_dt = datetime.strptime(time_control['end'], time_control['format'])
        duration_hours = (end_time_dt - start_time_dt).total_seconds() / 3600

        model_step_hours = workflow_config["model_step_hours"] # From new workflow config
        nsteps = int(duration_hours / model_step_hours)

        workflow_params = {
            "init_time": start_time_str, # Use start_time_str for init_time
            "time_format": time_format,
            "nsteps": nsteps,
            "output_dir": workflow_config["output_directory"], # From new workflow config
            "datasource": workflow_config["datasource"], # From new workflow config
        }
        
        hourly_interpolation_enabled = workflow_config["hourly_interpolation"] # From new workflow config

        # Step 3: Run workflow to generate combined 6-hourly forecast
        engine = InferenceEngine(workflow_params)
        engine.run()

        # Step 4: Interpolate to hourly and save individual files
        output_handler = engine.output_handler
        output_handler.process_and_save(hourly=hourly_interpolation_enabled)

        # Step 5: Plot results (if enabled)
        plotter = Plotter(plotting_config, workflow_params["output_dir"], init_time=start_time_dt) # Pass start_time_dt
        plotter.plot()

        # Step 6: Clean up combined forecast file
        combined_file = os.path.join(workflow_params["output_dir"], "combined_forecast.nc")
        if os.path.exists(combined_file):
            logger.info(f"Removing temporary combined forecast file: {combined_file}")
            os.remove(combined_file)
            logger.success(f"Removed {combined_file}")

    except Exception as e:
        logger.error(f"The workflow failed with an error: {e}", exc_info=True)

if __name__ == "__main__":
    main()


