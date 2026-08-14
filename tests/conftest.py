"""Pytest configuration for the DLAMP test suite.

Registers the integration and regression markers used to partition
fast unit tests (default) from tests requiring real data.
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers used by the DLAMP test suite."""
    config.addinivalue_line(
        "markers",
        "integration: tests requiring real sample ERA5 data in DLAMP_DATA_PATH (skipped by default).",
    )
    config.addinivalue_line(
        "markers",
        "regression: tests comparing against pre-move golden baselines "
        "in DLAMP_DATA_PATH/regression_golden (run via `make regression`).",
    )
