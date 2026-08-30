"""Tests for DLAMP Regridder module.

Verifies DataRegridder construction by patching filesystem I/O,
xarray.open_dataset, and diagnostic loading.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np


def _make_cfg() -> dict:
    """Return a complete config dict matching DataRegridder.__init__."""
    return {
        "share": {
            "time_control": {
                "start": "2020-01-01 00:00",
                "end": "2020-01-01 06:00",
                "format": "%Y-%m-%d %H:%M",
                "base_step_hours": 3,
            },
            "io_control": {
                "base_dir": "/tmp/test_regridder",
                "grib_subdir": "grib",
                "netcdf_subdir": "netcdf",
                "prefix": {
                    "upper": "pl",
                    "surface": "sl",
                    "output": "out",
                    "timestr_fmt": "%Y%m%d%H",
                },
            },
        },
        "regrid": {
            "target_nc": "/fake/target.nc",
            "target_lon": "XLONG",
            "target_lat": "XLAT",
            "target_pres": "pres",
            "source_lon": "longitude",
            "source_lat": "latitude",
            "source_pres": "level",
            "levels": [1000, 850, 500],
            "adopted_varlist": ["XLONG", "XLAT"],
            "write_regrid": False,
        },
        "registry": {
            "source_dataset": "ERA5",
        },
    }


def _make_fake_dataset() -> MagicMock:
    """Return a MagicMock that quacks like an xr.Dataset context manager."""
    ds = MagicMock()
    ds.__enter__ = MagicMock(return_value=ds)
    ds.__exit__ = MagicMock(return_value=False)
    ds.__getitem__ = MagicMock(side_effect=lambda key: MagicMock(values=np.zeros((10, 10))))
    return ds


class DataRegridderConstructorTest(unittest.TestCase):
    """Unit tests for DataRegridder constructor."""

    def _build(self) -> "DataRegridder":  # noqa: F821
        from dlamp.data.preproc.dlamp_regridder import DataRegridder

        return DataRegridder(yaml_path="/fake/path.yaml")

    def _patch_all(self):
        """Return a list of context-manager patches for the constructor."""
        import dlamp.data.preproc.dlamp_regridder as mod

        return [
            patch.object(mod.DataRegridder, "_load_config", return_value=_make_cfg()),
            patch("dlamp.data.preproc.dlamp_regridder.os.makedirs"),
            patch("dlamp.data.preproc.dlamp_regridder.xr.open_dataset", return_value=_make_fake_dataset()),
            patch("dlamp.data.preproc.dlamp_regridder.load_diagnostics", return_value={}),
        ]

    def test_constructor_sets_total_steps(self) -> None:
        """DataRegridder counts timesteps from start to end."""
        patches = self._patch_all()
        for p in patches:
            p.start()
        try:
            regridder = self._build()
            # 00:00 → 06:00 @ 3h = 3 steps
            self.assertEqual(regridder.total_steps, 3)
        finally:
            for p in reversed(patches):
                p.stop()

    def test_constructor_stores_base_dir(self) -> None:
        """DataRegridder stores io_control.base_dir."""
        patches = self._patch_all()
        for p in patches:
            p.start()
        try:
            regridder = self._build()
            self.assertEqual(regridder.base_dir, "/tmp/test_regridder")
        finally:
            for p in reversed(patches):
                p.stop()

    def test_build_timeline_length(self) -> None:
        """build_timeline returns list of length total_steps."""
        patches = self._patch_all()
        for p in patches:
            p.start()
        try:
            regridder = self._build()
            timeline = regridder.build_timeline()
            self.assertEqual(len(timeline), regridder.total_steps)
        finally:
            for p in reversed(patches):
                p.stop()


if __name__ == "__main__":
    unittest.main()
