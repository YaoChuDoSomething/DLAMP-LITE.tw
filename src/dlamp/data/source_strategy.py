"""Data-source strategies: one module per source owns path and sanity logic.

Converges the three previously scattered ``match data_source`` dispatch
tables (``gen_data``/``gen_path`` in ``file_util`` and ``sanity_check`` in
``datetime_manager``) into a single strategy per data source. Adding a new
data source means writing one strategy module, not editing three sites.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

from ..runtime_config import RuntimeConfig
from ..utils.data_compose import DataCompose


class DataSourceStrategy(Protocol):
    """Resolve paths and sanity checks for one data source."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        """Return the file path for ``target_time`` under this source."""

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        """Return True if the data for ``dt`` is usable (files exist)."""


class NEO171RwrDataSource(DataSourceStrategy):
    """Binary ``.raw`` radar files stored per-hour directories on neo171."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        if data_compose is None:
            raise ValueError("data_compose is required for NEO171_RWRF")
        return (
            config.data_path
            / f"rwf_{target_time.strftime('%Y%m')}"
            / f"{target_time.strftime('%Y%m%d%H%M')}0000"
            / data_compose.basename
        )

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        if data_compose is None:
            return gen_path(dt).exists()
        return gen_path(dt, data_compose).exists()


class CwaRwrDataSource(DataSourceStrategy):
    """WRF-interpolated NetCDF files on the CWA HPC."""

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        predict_dt = target_time + timedelta(hours=use_Kth_hour_pred) if use_Kth_hour_pred is not None else target_time
        return config.data_path / f"wrfout_d01_{predict_dt.strftime('%Y-%m-%d_%H')}_interp"

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        return gen_path(dt).exists()


class OpEra5DataSource(DataSourceStrategy):
    """ERA5-derived NetCDF files (OP_ERA5 naming)."""

    _filename = "e5dlamp_{ts}.nc"

    def gen_path(
        self,
        target_time: datetime,
        config: RuntimeConfig,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> Path:
        return config.data_path / self._filename.format(ts=target_time.strftime("%Y%m%d_%H%M"))

    def sanity_check(
        self,
        dt: datetime,
        data_compose: DataCompose | None = None,
        use_Kth_hour_pred: int | None = None,
    ) -> bool:
        from ..utils import gen_path

        return gen_path(dt).exists()


class OpE2sDataSource(OpEra5DataSource):
    """E2S-derived sfno NetCDF files."""

    _filename = "e2s_sfno_dlamp_{ts}.nc"


def get_data_source(data_source: str) -> DataSourceStrategy:
    """Return the strategy registered for ``data_source``.

    Args:
        data_source: One of ``"NEO171_RWRF"``, ``"CWA_RWRF"``,
            ``"OP_ERA5"``, ``"OP_E2S"``.

    Returns:
        The matching ``DataSourceStrategy``.

    Raises:
        ValueError: If ``data_source`` is not registered.
    """
    strategies: dict[str, DataSourceStrategy] = {
        "NEO171_RWRF": NEO171RwrDataSource(),
        "CWA_RWRF": CwaRwrDataSource(),
        "OP_ERA5": OpEra5DataSource(),
        "OP_E2S": OpE2sDataSource(),
    }
    try:
        return strategies[data_source]
    except KeyError as exc:
        raise ValueError(
            f"Unknown data source: '{data_source}'. "
            f"Available: {', '.join(sorted(strategies))}"
        ) from exc