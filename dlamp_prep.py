#!/bin/python

###===== Workflow Control ===========================================###
#
###==================================================================###
from src.preproc.cds_downloader import CDSDataDownloader
from src.preproc.dlamp_regridder import DataRegridder

do_cds_downloader = False
do_dlamp_regridder = True

DLAMP_DATA_DIR = "./"
yaml_config = f"config/sfno_gfs.yaml"


###===== ERA5 Dataset Downloading ===================================###
#   Downloading process is fully controled by YAML configure file
###==================================================================###


if do_cds_downloader True: 
    downloader = CDSDataDownloader(yaml_config)
    timeline = downloader.create_timeline()
    
for curr in timeline:
    downloader.process_download(curr)


###===== DataRegridder and Variables Registry =======================###
#   Data Regridding can be controled by YAML configure file
#   Variables Registry can be controled by YAML configure file
#   Variables Diagnostics can be controled by module script:
#       src/registry/diagnostics_functions
###==================================================================###


yaml_config = f"{DLAMP_DATA_DIR}/config/era5.yaml"
regridder = DataRegridder(yaml_config)
    #regridder.process_single_time(curr)
    
regridder.main_process()


