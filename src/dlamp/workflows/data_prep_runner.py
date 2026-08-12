"""Data preparation workflow runner for the DLAMP pipeline.

Generates constant-mask artefacts (land-sea mask, topography mask) that
are required by downstream training and inference workflows.  Three mask
sources are supported, selected by ``cfg.data_prep.method``:

- ``extract_from_nc``  — extract masks from an existing WRF NetCDF file
  (default, recommended when model output is available)
- ``gen_tw_cn_terrain`` — interpolate from a GeoTIFF raster covering
  East Asia (requires ``assets/terrain_shp/gt30e100n40.tif``)
- ``gen_tw_only_terrain`` — interpolate from a Taiwan-specific shapefile
  (requires ``assets/terrain_shp/GIS_terrain.shp``)

Raises:
    ValueError: If ``cfg.data_prep.method`` is not one of the supported
        values listed above.
    FileNotFoundError: If a required source file cannot be located.
"""

import logging
from pathlib import Path
from typing import Any

from omegaconf import DictConfig

from dlamp.runtime_config import RuntimeConfig, get_runtime_config

logger = logging.getLogger(__name__)

_SUPPORTED_METHODS = frozenset(
    {"extract_from_nc", "gen_tw_cn_terrain", "gen_tw_only_terrain"}
)


class DataPrepRunner:
    """Runs the data-preparation (constant-mask generation) workflow.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        runtime_config (RuntimeConfig): The validated runtime configuration
            singleton for the current process.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the DataPrepRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain a ``data_prep.method`` key whose value is one of
                the supported mask-generation methods.

        Raises:
            ValueError: If ``cfg.data_prep.method`` is not supported.
        """
        self.cfg = cfg
        self.runtime_config: RuntimeConfig = get_runtime_config()

        method: str = cfg.data_prep.method
        if method not in _SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported data_prep.method '{method}'. "
                f"Choose from: {sorted(_SUPPORTED_METHODS)}"
            )
        self._method = method

    def run(self) -> dict[str, Any]:
        """Executes the mask-generation workflow.

        Dispatches to the appropriate helper based on
        ``self._method`` and logs the paths of artefacts written.

        Returns:
            dict[str, Any]: A summary containing:
                - ``method`` (str): The method used.
                - ``output_dir`` (str): Directory where masks were written.
                - ``artifacts`` (list[str]): Absolute paths of files written.

        Raises:
            FileNotFoundError: If a required source raster or NetCDF file
                is missing.
        """
        logger.info("DataPrepRunner: method=%s", self._method)

        if self._method == "extract_from_nc":
            artifacts = self._extract_from_nc()
        elif self._method == "gen_tw_cn_terrain":
            artifacts = self._gen_tw_cn_terrain()
        else:
            artifacts = self._gen_tw_only_terrain()

        out_dir = str(
            self.runtime_config.standardization_path.parent / "constant_masks"
        )
        logger.info(
            "DataPrepRunner: wrote %d artefact(s) to %s", len(artifacts), out_dir
        )
        return {"method": self._method, "output_dir": out_dir, "artifacts": artifacts}

    # ------------------------------------------------------------------
    # Private helpers — delegate to generate_const_masks functions
    # ------------------------------------------------------------------

    def _extract_from_nc(self) -> list[str]:
        """Extract land-sea and topography masks from a WRF NetCDF file.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.
        """
        import yaml
        import xarray as xr
        import numpy as np

        from dlamp.const import REPO_ROOT
        from dlamp.utils import gen_path

        rc = self.runtime_config
        with open(rc.data_config_path, "r") as fh:
            data_config = yaml.safe_load(fh)

        from datetime import datetime

        start_t = datetime.strptime(
            data_config["start_time"], data_config["format"]
        )
        filename = gen_path(start_t)
        if not Path(str(filename)).exists():
            raise FileNotFoundError(
                f"Source NetCDF not found: {filename}. "
                "Ensure DLAMP_DATA_PATH and DLAMP_EXP_CODE are correct."
            )

        data_shape = data_config["data_shape"]
        img_shape = data_config["image_shape"]

        dataset = xr.open_dataset(str(filename))
        terrain = dataset["HGT"].values.squeeze()
        landsea = dataset["LANDMASK"].values.squeeze()
        assert tuple(data_shape) == terrain.shape == landsea.shape, (
            f"Shape mismatch: data_shape={data_shape}, terrain={terrain.shape}"
        )

        terrain = terrain[1:-1, 1:-1]
        landsea = landsea[1:-1, 1:-1]
        terrain_mask = terrain[::2, ::2]
        landsea_mask = landsea[::2, ::2]
        assert tuple(img_shape) == terrain_mask.shape == landsea_mask.shape

        out_dir = REPO_ROOT / "assets" / "constant_masks"
        out_dir.mkdir(parents=True, exist_ok=True)
        topo_path = out_dir / "topography_mask_4km.npy"
        land_path = out_dir / "land_sea_mask_4km.npy"
        np.save(topo_path, terrain_mask)
        np.save(land_path, landsea_mask)
        return [str(topo_path), str(land_path)]

    def _gen_tw_cn_terrain(self) -> list[str]:
        """Interpolate masks from a GeoTIFF raster covering East Asia.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.

        Raises:
            FileNotFoundError: If the GeoTIFF raster is not present.
        """
        from dlamp.generate_const_masks import gen_TW_CN_terrain

        gen_TW_CN_terrain()
        rc = self.runtime_config
        out_dir = rc.standardization_path.parent / "constant_masks"
        return [
            str(out_dir / "topography_mask_4km.npy"),
            str(out_dir / "land_sea_mask_4km.npy"),
        ]

    def _gen_tw_only_terrain(self) -> list[str]:
        """Interpolate masks from a Taiwan-specific point shapefile.

        Returns:
            list[str]: Paths of the two ``.npy`` files written.

        Raises:
            FileNotFoundError: If the shapefile is not present.
        """
        from dlamp.generate_const_masks import gen_TW_only_terrain

        gen_TW_only_terrain()
        rc = self.runtime_config
        out_dir = rc.standardization_path.parent / "constant_masks"
        return [
            str(out_dir / "topography_mask_4km.npy"),
            str(out_dir / "land_sea_mask_4km.npy"),
        ]
