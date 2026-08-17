"""Data ingestion and loader interfaces for meteorological datasets in FCN-RegPGW.

Provides abstract data source abstractions and implementations for loading
NPY arrays, NetCDF files, and operational initial conditions.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import xarray as xr

from fcn_regpgw.const import (
    DEFAULT_LAT_SIZE,
    DEFAULT_LON_SIZE,
    VARIABLES_73,
)
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class BaseDataIngestion(ABC):
    """Abstract base class for atmospheric data ingestion."""

    @abstractmethod
    def load(
        self,
        source_path: str | Path,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
    ) -> np.ndarray:
        """Load atmospheric field data from source.

        Args:
            source_path (Union[str, Path]): Path to data source.
            lat_size (int): Expected latitude dimension.
            lon_size (int): Expected longitude dimension.

        Returns:
            np.ndarray: Loaded array of shape (num_channels, lat_size, lon_size).
        """
        raise NotImplementedError


class NumpyDataIngestion(BaseDataIngestion):
    """Data ingestion loader for pre-processed numpy array files (.npy)."""

    def load(
        self,
        source_path: str | Path,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
    ) -> np.ndarray:
        """Load .npy atmospheric field array and conform to expected grid shape.

        Args:
            source_path (Union[str, Path]): Path to .npy file.
            lat_size (int): Target latitude dimension size.
            lon_size (int): Target longitude dimension size.

        Returns:
            np.ndarray: Formatted atmospheric field array.

        Raises:
            FileNotFoundError: If source file does not exist.
        """
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"Data file not found: {path}")

        logger.info("Loading numpy data from %s", path)
        data = np.load(path)

        # Handle leading batch dimension (1, C, H, W) -> (C, H, W)
        if data.ndim == 4 and data.shape[0] == 1:
            data = data[0]

        # Handle 721 vs 720 latitude grid points
        if data.shape[1] > lat_size:
            data = data[:, :lat_size, :]
        if data.shape[2] > lon_size:
            data = data[:, :, :lon_size]

        return data.astype(np.float32)


class NetCDFDataIngestion(BaseDataIngestion):
    """Data ingestion loader for NetCDF datasets (.nc)."""

    def __init__(self, variables: Sequence[str] = VARIABLES_73) -> None:
        """Initialize NetCDF loader.

        Args:
            variables (Sequence[str]): List of atmospheric variables to extract.
        """
        self.variables = list(variables)

    def load(
        self,
        source_path: str | Path,
        lat_size: int = DEFAULT_LAT_SIZE,
        lon_size: int = DEFAULT_LON_SIZE,
    ) -> np.ndarray:
        """Load NetCDF dataset variables into structured array.

        Args:
            source_path (Union[str, Path]): Path to NetCDF dataset.
            lat_size (int): Target latitude dimension.
            lon_size (int): Target longitude dimension.

        Returns:
            np.ndarray: Formatted multi-channel atmospheric array.

        Raises:
            FileNotFoundError: If source NetCDF does not exist.
        """
        path = Path(source_path)
        if not path.is_file():
            raise FileNotFoundError(f"NetCDF file not found: {path}")

        logger.info("Loading NetCDF dataset from %s", path)
        with xr.open_dataset(path) as ds:
            channels = []
            for var in self.variables:
                if var in ds:
                    val = ds[var].values.astype(np.float32)
                    if val.ndim == 3 and val.shape[0] == 1:
                        val = val[0]
                    channels.append(val[:lat_size, :lon_size])
                else:
                    logger.warning("Variable %s missing from %s, using zeros", var, path)
                    channels.append(np.zeros((lat_size, lon_size), dtype=np.float32))

            return np.stack(channels, axis=0)


class DataIngestionFactory:
    """Factory to instantiate data ingestion loaders based on file extensions."""

    @staticmethod
    def create(file_path: str | Path) -> BaseDataIngestion:
        """Create ingestion loader matching file extension.

        Args:
            file_path (Union[str, Path]): File path or format identifier.

        Returns:
            BaseDataIngestion: Appropriate ingestion loader instance.
        """
        suffix = Path(file_path).suffix.lower()
        if suffix in [".nc", ".netcdf"]:
            return NetCDFDataIngestion()
        return NumpyDataIngestion()
