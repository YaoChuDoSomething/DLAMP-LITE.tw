"""Generate golden regression baselines for the DLAMP regression suite.

This script is executed BEFORE the refactor (pre-move) to snapshot the
current outputs of the data pipeline and inference pipeline into
``DLAMP_DATA_PATH/regression_golden/``.  After the move, the regression
suite re-runs the same code and compares against these snapshots using
``rtol=1e-5`` and ``atol=1e-6``.

Storage is intentionally *not* committed (per the regression strategy,
ticket 10); the directory lives under ``DLAMP_DATA_PATH`` and is
gitignored.  Baselines may be regenerated at any time by re-running
this script against a known-good tree.

Usage::

    python tests/regression/generate_golden.py
"""

import shutil
from pathlib import Path

from tests.regression.conftest import golden_dir


def _copy(src: Path, dst_name: str) -> None:
    """Copy ``src`` into the golden directory under ``dst_name``."""
    dst = golden_dir() / dst_name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[golden] {dst_name} <- {src}")


def generate_pipeline_golden(data_path: Path) -> None:
    """Snapshot data-pipeline outputs (regridded e5dlamp + diagnostics).

    Args:
        data_path (Path): Root of the ``DLAMP_DATA_PATH`` source pool.
    """
    # e5dlamp_* regridded output (produced by the data pipeline)
    for nc in sorted(data_path.glob("e5dlamp_*.nc")):
        _copy(nc, nc.name)

    # diagnostic calculation outputs (produced by diagnostic_registry)
    for npy in sorted(data_path.glob("diagnostic_*.npy")):
        _copy(npy, npy.name)

    # discrete masks live in the repo assets dir
    masks_root = Path(__file__).resolve().parents[3] / "assets" / "constant_masks"
    for mask in ("land_sea_mask_4km.npy", "topography_mask_4km.npy"):
        mask_path = masks_root / mask
        if mask_path.exists():
            _copy(mask_path, mask.name)


def generate_inference_golden(data_path: Path) -> None:
    """Snapshot inference-pipeline forecast NetCDF outputs.

    Args:
        data_path (Path): Root of the ``DLAMP_DATA_PATH`` source pool.
    """
    for pattern in ("forecast_*_upper.nc", "forecast_*_surface.nc"):
        for nc in sorted(data_path.glob(pattern)):
            _copy(nc, nc.name)


def main() -> None:
    """Generate all golden baselines under ``DLAMP_DATA_PATH/regression_golden/``."""
    import os

    data_path = Path(os.environ.get("DLAMP_DATA_PATH", "/wk2/yaochu/CASE_DATA/Pool/"))
    out = golden_dir()
    print(f"[golden] writing baselines to {out}")
    generate_pipeline_golden(data_path)
    generate_inference_golden(data_path)


if __name__ == "__main__":
    main()
