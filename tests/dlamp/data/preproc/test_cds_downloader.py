"""Tests for CDS Downloader module.

Verifies CDSDataDownloader construction by patching all I/O and
external client calls (cdsapi, cdo, os.makedirs).
"""

import unittest
from unittest.mock import MagicMock, patch

from dlamp.data.preproc.cds_downloader import CDSDataDownloader


def _make_cfg() -> dict:
    """Return a complete valid config dict matching CDSDataDownloader."""
    return {
        "share": {
            "time_control": {
                "start": "2020-01-01 00:00",
                "end": "2020-01-01 03:00",
                "format": "%Y-%m-%d %H:%M",
                "base_step_hours": 3,
            },
            "io_control": {
                "base_dir": "/tmp/test_cds",
                "grib_subdir": "grib",
                "netcdf_subdir": "netcdf",
                "prefix": {"timestr_fmt": "%Y%m%d%H"},
            },
        },
        "download": {
            "area": {
                "north": 40,
                "west": 110,
                "south": 20,
                "east": 130,
            },
        },
    }


@patch("dlamp.data.preproc.cds_downloader.os.makedirs")
@patch("dlamp.data.preproc.cds_downloader.Cdo")
@patch("dlamp.data.preproc.cds_downloader.cdsapi.Client")
@patch(
    "dlamp.data.preproc.cds_downloader.CDSDataDownloader._load_config",
    return_value=None,
)
class CDSDataDownloaderTest(unittest.TestCase):
    """Unit tests for CDSDataDownloader."""

    def test_constructor_sets_time_range(
        self,
        mock_load: MagicMock,
        mock_client: MagicMock,
        mock_cdo: MagicMock,
        mock_makedirs: MagicMock,
    ) -> None:
        """CDSDataDownloader counts timesteps from start to end."""
        mock_load.return_value = _make_cfg()
        downloader = CDSDataDownloader(yaml_path="/fake/path.yaml")
        # 00:00 → 03:00 @ 3h = 2 steps (0, 3)
        self.assertEqual(downloader.total_steps, 2)

    def test_constructor_stores_base_dir(
        self,
        mock_load: MagicMock,
        mock_client: MagicMock,
        mock_cdo: MagicMock,
        mock_makedirs: MagicMock,
    ) -> None:
        """CDSDataDownloader stores io_control.base_dir."""
        mock_load.return_value = _make_cfg()
        downloader = CDSDataDownloader(yaml_path="/fake/path.yaml")
        self.assertEqual(downloader.base_dir, "/tmp/test_cds")

    def test_create_timeline_length(
        self,
        mock_load: MagicMock,
        mock_client: MagicMock,
        mock_cdo: MagicMock,
        mock_makedirs: MagicMock,
    ) -> None:
        """create_timeline returns list of length total_steps."""
        mock_load.return_value = _make_cfg()
        downloader = CDSDataDownloader(yaml_path="/fake/path.yaml")
        timeline = downloader.create_timeline()
        self.assertEqual(len(timeline), downloader.total_steps)


if __name__ == "__main__":
    unittest.main()
