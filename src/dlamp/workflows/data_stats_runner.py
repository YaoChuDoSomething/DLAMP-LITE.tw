"""Data-statistics workflow runner for the DLAMP pipeline.

Computes per-variable z-score statistics (mean and standard deviation)
from a random sample of raw NetCDF data and writes the results to the
standardization JSON file specified by ``RuntimeConfig``.

The computation is delegated to ``dlamp.standardizer.Standardizer.
calc_standardization``.  If a variable already exists in the JSON it is
skipped, so the script can be re-run safely after interruption.

Raises:
    RuntimeConfigError: If the model code does not match an existing
        data-config or standardization file on disk.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from omegaconf import DictConfig

from dlamp.runtime_config import RuntimeConfig
from dlamp.standardizer import Standardizer, get_standardizer

logger = logging.getLogger(__name__)


class DataStatsRunner:
    """Runs the z-score standardization-statistics computation workflow.

    Wraps ``Standardizer.calc_standardization`` and exposes all four
    configurable parameters via the Hydra config object so that they can
    be overridden on the command line without touching source code.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        standardizer (Standardizer): The singleton Standardizer instance
            for the current process, pre-loaded with any existing stats.
    """

    def __init__(self, cfg: DictConfig, runtime_config: RuntimeConfig) -> None:
        """Initialises the DataStatsRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain a ``stats`` group with keys: ``start_time``,
                ``end_time``, ``sample_size``, ``num_criteria``.
            runtime_config (RuntimeConfig): The validated runtime
                configuration singleton for the current process.
        """
        self.cfg = cfg
        self.standardizer: Standardizer = get_standardizer(runtime_config)
        self._start_time: datetime = datetime.strptime(cfg.stats.start_time, "%Y-%m-%d %H:%M").replace(
            tzinfo=UTC
        )
        self._end_time: datetime = datetime.strptime(cfg.stats.end_time, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
        self._sample_size: int = cfg.stats.sample_size
        self._num_criteria: int = cfg.stats.num_criteria

    def run(self) -> dict[str, Any]:
        """Executes the statistics computation workflow.

        Iterates over all variables in the data config and computes z-score
        statistics for those not already present in the JSON file.

        Returns:
            dict[str, Any]: A summary containing:
                - ``standardization_path`` (str): Path to the JSON written.
                - ``start_time`` (str): Start of the sampling window.
                - ``end_time`` (str): End of the sampling window.
                - ``sample_size`` (int): Number of random pixels per frame.
                - ``num_criteria`` (int): Minimum samples required to keep
                    a variable's statistics.
        """
        logger.info(
            "DataStatsRunner: computing stats for %s → %s (sample_size=%d, num_criteria=%d)",
            self._start_time.date(),
            self._end_time.date(),
            self._sample_size,
            self._num_criteria,
        )
        self.standardizer.calc_standardization(
            start_time=self._start_time,
            end_time=self._end_time,
            sample_size=self._sample_size,
            num_criteria=self._num_criteria,
        )
        json_path = str(self.standardizer._config.standardization_path)
        logger.info("DataStatsRunner: stats written to %s", json_path)
        return {
            "standardization_path": json_path,
            "start_time": str(self._start_time),
            "end_time": str(self._end_time),
            "sample_size": self._sample_size,
            "num_criteria": self._num_criteria,
        }
