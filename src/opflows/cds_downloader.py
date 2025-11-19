import yaml
import cdsapi
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
# from cdo import Cdo # Removed
import os
import tempfile # New import


class CDSDataDownloader:
    def __init__(self, yaml_path):
        self.cfg = self._load_config(yaml_path)

        self.cfg_time = self.cfg["share"]["time_control"]
        self.start_t = datetime.strptime(
            self.cfg_time["start"],
            self.cfg_time["format"]
        )
        self.end_t = datetime.strptime(
            self.cfg_time["end"],
            self.cfg_time["format"]
        )
        self.a_timestep = timedelta(
            hours=self.cfg_time["base_step_hours"]
        )
        self.total_steps = ((self.end_t - self.start_t) // self.a_timestep) + 1

        # Updated I/O Control logic from download.yaml
        self.output_control = self.cfg["output_control"]
        self.output_dir = self.output_control["output_dir"]
        self.output_filename_prefix = self.output_control["filename_prefix"]
        self.output_timestr_fmt = self.output_control["timestr_format"]
        os.makedirs(self.output_dir, exist_ok=True) # Ensure output directory exists

        # Prefix for temporary GRIB files (if needed, otherwise can be simplified)
        self.prefix_grib = self.cfg["share"]["io_control"]["prefix"]
        self.timestr_fmt_grib = self.prefix_grib['timestr_fmt']

        self.area = self.cfg["download"]["area"]
        self.area_list = [
            self.area['north'],
            self.area['west'],
            self.area['south'],
            self.area['east'],
        ]

        self.client = cdsapi.Client()
        # cdo is no longer used for invertlat, as xarray handles it.
        # Keeping Cdo instance just in case it's used elsewhere or for future features.
        # self.cdo = Cdo(tempdir="./.cdo_tmp") # Removed
        # self.cdo.debug = True # Removed

    def _load_config(self, yaml_path):
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    def create_timeline(self):
        return [
            self.start_t + t * self.a_timestep
            for t in range(self.total_steps)
        ]

    def _build_request(self, dataset, variables, curr_time, levels=None):
        req = {
            "product_type": "reanalysis",
            "year": [curr_time.strftime('%Y')],
            "month": [curr_time.strftime('%m')],
            "day": [curr_time.strftime('%d')],
            "time": [curr_time.strftime('%H:%M')],
            "variable": variables,
            "format": "grib"
        }
        if levels:
            req["pressure_level"] = [str(l) for l in levels]
        if self.area_list:
            req["area"] = self.area_list
        return req

    # The invertlat_to_netcdf function is no longer needed as its logic
    # is integrated directly into process_download.
    # def invertlat_to_netcdf(self, input_grib: str, output_netcdf: str):
    #    ...

    def process_download(self, curr_time):
        self.pl_cfg = self.cfg["download"]["dataset_upper"]
        self.sl_cfg = self.cfg["download"]["dataset_surface"]

        # Use temporary files for grib data
        with tempfile.NamedTemporaryFile(suffix=".grib", delete=True) as pl_grb_file, \
             tempfile.NamedTemporaryFile(suffix=".grib", delete=True) as sl_grb_file:
            
            pl_grb_path = pl_grb_file.name
            sl_grb_path = sl_grb_file.name

            # Download pressure level data
            req_pl = self._build_request(self.pl_cfg['title'], self.pl_cfg['variables'], curr_time, self.pl_cfg.get('levels'))
            print(f"Downloading upper-level data for {curr_time.strftime(self.timestr_fmt_grib)} to {pl_grb_path}")
            self.client.retrieve(self.pl_cfg['title'], req_pl).download(pl_grb_path)
            
            # Download surface level data
            req_sl = self._build_request(self.sl_cfg['title'], self.sl_cfg['variables'], curr_time)
            print(f"Downloading surface-level data for {curr_time.strftime(self.timestr_fmt_grib)} to {sl_grb_path}")
            self.client.retrieve(self.sl_cfg['title'], req_sl).download(sl_grb_path)

            # Load grib files into xarray datasets
            print(f"Loading {pl_grb_path} into xarray")
            ds_pl = xr.open_dataset(pl_grb_path, engine="cfgrib")
            print(f"Loading {sl_grb_path} into xarray")
            ds_sl = xr.open_dataset(sl_grb_path, engine="cfgrib")

            # Merge datasets
            # Use compat='override' to handle cases where attributes or coordinates might differ
            print("Merging pressure-level and surface-level datasets")
            merged_ds = xr.merge([ds_pl, ds_sl], compat='override')

            # Invert latitude and sort if necessary
            print("Sorting merged dataset by latitude")
            for lat_name in ["latitude", "lat"]:
                if lat_name in merged_ds.dims:
                    merged_ds = merged_ds.sortby(lat_name, ascending=True)
                    break
            
            # Construct output filename
            output_filename = os.path.join(
                self.output_dir,
                f"{self.output_filename_prefix}_{curr_time.strftime(self.output_timestr_fmt)}.nc"
            )

            # Save to NetCDF4
            print(f"Saving merged dataset to {output_filename}")
            merged_ds.to_netcdf(output_filename, format="netcdf4")
            print(f"Successfully saved merged NetCDF to {output_filename}")

            # Temporary grib files are automatically deleted when 'with' block exits.
            # xarray datasets are automatically closed when they go out of scope.
