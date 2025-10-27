import xarray as xr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Attempting to open assets/target.nc with xarray")
    ds = xr.open_dataset("assets/target.nc", engine="netcdf4")
    logger.info("Successfully opened assets/target.nc")
    logger.info(ds)
except Exception as e:
    logger.error(f"Failed to open assets/target.nc: {e}", exc_info=True)
