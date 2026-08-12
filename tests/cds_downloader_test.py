"""Tests for CDS Downloader module."""

from unittest.mock import patch

import torch
from dlamp.downloader import CDSDownloader


def test_cds_downloader_loads_data() -> None:
    """Test CDS Downloader loads data correctly."""
    downloader = CDSDownloader()
    # Mock the download process
    with patch('dlamp.downloader._download_from_url') as mock_download:
        mock_download.return_value = torch.randn(10, 3, 64, 64)
        result = downloader.load()
        assert result is not None
        assert result.shape == (10, 3, 64, 64)
