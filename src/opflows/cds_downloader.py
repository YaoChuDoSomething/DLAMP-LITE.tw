import yaml
import cdsapi
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
# from cdo import Cdo # Removed
import os
import tempfile # New import
from typing import Dict, Any, List, Optional # Added for type hints


class CDSDataDownloader:
    """
    Handles downloading ERA5 data from the Copernicus Data Store (CDS).

    This class supports downloading both pressure-level and surface-level data,
    merging them into a single xarray.Dataset, and saving them as a NetCDF4 file.
    It uses a configuration dictionary for setup rather than a YAML file path.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the CDSDataDownloader with a configuration dictionary.

        Args:
            config (Dict[str, Any]): A dictionary containing the configuration
                                     for data download, including 'share',
                                     'download', and 'output_control' sections.
        """
        self.cfg = config

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

        self.output_control = self.cfg["output_control"]
        self.output_dir = self.output_control["output_dir"]
        self.output_filename_prefix = self.output_control["filename_prefix"]
        self.output_timestr_fmt = self.output_control["timestr_format"]
        os.makedirs(self.output_dir, exist_ok=True)

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

    # Removed _load_config method
    # def _load_config(self, yaml_path):
    #     with open(yaml_path, "r") as f:
    #         return yaml.safe_load(f)

    def create_timeline(self) -> List[datetime]: # Added type hint
        """
        Generates a list of datetime objects representing the timeline for data download.

        Returns:
            List[datetime]: A list of datetime objects.
        """
        return [
            self.start_t + t * self.a_timestep
            for t in range(self.total_steps)
        ]

    def _build_request(self, dataset: str, variables: List[str], curr_time: datetime, levels: Optional[List[int]] = None) -> Dict[str, Any]: # Added type hints and Optional
        """
        Builds the request dictionary for the CDS API.

        Args:
            dataset (str): The title of the dataset (e.g., "reanalysis-era5-pressure-levels").
            variables (List[str]): A list of variables to request.
            curr_time (datetime): The current datetime for the request.
            levels (Optional[List[int]]): Optional list of pressure levels.

        Returns:
            Dict[str, Any]: A dictionary representing the CDS API request.
        """
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

    def process_download(self, curr_time: datetime) -> None: # Added type hint
        """
        Downloads pressure-level and surface-level ERA5 data for a given timestep,
        merges them, and saves the result as a single NetCDF4 file.

        Args:
            curr_time (datetime): The current datetime for which to download data.
        """
        self.pl_cfg = self.cfg["download"]["dataset_upper"]
        self.sl_cfg = self.cfg["download"]["dataset_surface"]

        with tempfile.NamedTemporaryFile(suffix=".grib", delete=True) as pl_grb_file, \
             tempfile.NamedTemporaryFile(suffix=".grib", delete=True) as sl_grb_file:
            
            pl_grb_path = pl_grb_file.name
            sl_grb_path = sl_grb_file.name

            req_pl = self._build_request(self.pl_cfg['title'], self.pl_cfg['variables'], curr_time, self.pl_cfg.get('levels'))
            print(f"Downloading upper-level data for {curr_time.strftime(self.timestr_fmt_grib)} to {pl_grb_path}")
            self.client.retrieve(self.pl_cfg['title'], req_pl).download(pl_grb_path)
            
            req_sl = self._build_request(self.sl_cfg['title'], self.sl_cfg['variables'], curr_time)
            print(f"Downloading surface-level data for {curr_time.strftime(self.timestr_fmt_grib)} to {sl_grb_path}")
            self.client.retrieve(self.sl_cfg['title'], req_sl).download(sl_grb_path)

            print(f"Loading {pl_grb_path} into xarray")
            ds_pl = xr.open_dataset(pl_grb_path, engine="cfgrib")
            print(f"Loading {sl_grb_path} into xarray")
            ds_sl = xr.open_dataset(sl_grb_path, engine="cfgrib")

            print("Merging pressure-level and surface-level datasets")
            merged_ds = xr.merge([ds_pl, ds_sl], compat='override')

            print("Sorting merged dataset by latitude")
            for lat_name in ["latitude", "lat"]:
                if lat_name in merged_ds.dims:
                    merged_ds = merged_ds.sortby(lat_name, ascending=True)
                    break
            
            output_filename = os.path.join(
                self.output_dir,
                f"{self.output_filename_prefix}_{curr_time.strftime(self.output_timestr_fmt)}.nc"
            )

            print(f"Saving merged dataset to {output_filename}")
            merged_ds.to_netcdf(output_filename, format="netcdf4")
            print(f"Successfully saved merged NetCDF to {output_filename}")
