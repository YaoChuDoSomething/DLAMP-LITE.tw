"""Golden baseline fixtures for the DLAMP regression suite.

Baseline snapshots (``e5dlamp_*`` NetCDF outputs, regridded arrays,
predict forecast NetCDFs) are captured pre-move and stored in
``DLAMP_DATA_PATH/regression_golden/``.  These helpers locate that
directory and expose the shared comparison tolerances mandated by the
testing specification.

The golden directory is gitignored; it is not required for the fast
unit suite and missing baselines cause regression tests to be skipped.
"""

import os
from pathlib import Path

REGENC_RTOL: float = 1e-5
REGENC_ATOL: float = 1e-6


def golden_dir() -> Path:
    """Return the path to the golden baseline directory.

    The location is derived from ``DLAMP_DATA_PATH`` (default
    ``/wk2/yaochu/CASE_DATA/Pool/``), mirroring the regression strategy
    in ``docs/testing/testing-specification.md``.

    Returns:
        Path: The ``regression_golden`` subdirectory of the data path.
    """
    data_path = Path(os.environ.get("DLAMP_DATA_PATH", "/wk2/yaochu/CASE_DATA/Pool/"))
    return data_path / "regression_golden"


def golden_file(name: str) -> Path:
    """Return the path to a named golden baseline file.

    Args:
        name (str): Filename of the golden baseline inside
            ``DLAMP_DATA_PATH/regression_golden/``.

    Returns:
        Path: The resolved golden baseline path.
    """
    return golden_dir() / name
