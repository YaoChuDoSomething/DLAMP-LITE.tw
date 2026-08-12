from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import yaml
from tqdm import tqdm

from .const import BLACKLIST_PATH
from .runtime_config import RuntimeConfig
from .utils import DataCompose, DataGenerator, DataType, gen_path

if TYPE_CHECKING:
    from .utils import DataCompose

logger = logging.getLogger(__name__)

MEAN_THRESHOLD = 1e-4


class Standardizer:
    """Standardizes and destandardizes weather data.

    Loads statistics once at construction time from the
    ``standardization_path`` and ``data_config_path`` provided by
    ``RuntimeConfig``. Eliminates the per-call YAML re-reads and the
    import-time module-level state of the old ``standardization`` module.

    Both ``standardize`` and ``destandardize`` share the same stats
    dictionary and data ordering, so they can never disagree.
    """

    def __init__(self, config: RuntimeConfig):
        self._config = config
        self._stat_dict = self._load_stats(config.standardization_path)
        self._data_list = DataCompose.from_config(config.data_config_path)

    def _load_stats(self, path: Path) -> dict:
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def standardize(self, dc_name: str, array: np.ndarray) -> np.ndarray:
        """Standardize a single variable array.

        Matches the behavior of the old ``standardization()`` function.
        """
        if dc_name in self._stat_dict:
            stat = self._stat_dict[dc_name]
            if abs(stat["mean"]) < MEAN_THRESHOLD:
                return array
            elif "Qt@Hpa" in dc_name:
                return np.log(array * 1e5 + 1)
            else:
                return (array - stat["mean"]) / stat["std"]
        else:
            return np.zeros_like(array)

    def destandardize(self, array: np.ndarray) -> np.ndarray:
        """Destandardize a full stacked array.

        The array shape is either (lv, H, W, C) or (B, lv, H, W, C).
        Variable ordering is determined by the data_list loaded from the
        data config at construction time, so no per-call YAML re-reads
        are needed.
        """
        num_array_dim = len(array.shape)
        if num_array_dim not in [4, 5]:
            raise ValueError(f"Expected 4D or 5D array, got {num_array_dim}D")

        is_surface = array.shape[1 if num_array_dim == 5 else 0] == 1
        return self._destandardize(array, is_surface)

    def _destandardize(
        self, array: np.ndarray, is_sfc: bool
    ) -> np.ndarray:
        """Handle destandardization for surface or upper-level variables."""
        new_array = np.zeros_like(array)

        if is_sfc:
            filtered_dc = [dc for dc in self._data_list if dc.level.is_surface()]
            variables = DataCompose.get_all_vars(self._data_list, only_surface=True)
        else:
            filtered_dc = [dc for dc in self._data_list if not dc.level.is_surface()]
            levels = DataCompose.get_all_levels(self._data_list, only_upper=True)
            variables = DataCompose.get_all_vars(self._data_list, only_upper=True)

        for dc in filtered_dc:
            if str(dc) not in self._stat_dict:
                continue

            stat = self._stat_dict[str(dc)]
            lv_idx = 0 if is_sfc else levels.index(dc.level)
            var_idx = variables.index(dc.var_name)

            if len(array.shape) == 5:
                new_array[:, lv_idx, :, :, var_idx] = self._destandardize_array(
                    array[:, lv_idx, :, :, var_idx], stat, dc
                )
            else:
                new_array[lv_idx, :, :, var_idx] = self._destandardize_array(
                    array[lv_idx, :, :, var_idx], stat, dc
                )

        return new_array

    def _destandardize_array(
        self, array: np.ndarray, stat: dict[str, float], dc: DataCompose
    ) -> np.ndarray:
        """Apply destandardization to a single array using statistics from stat_dict."""
        if abs(stat["mean"]) < MEAN_THRESHOLD:
            return array
        elif "Qt@Hpa" in str(dc):
            return (np.exp(array) - 1) / 1e5
        else:
            return array * stat["std"] + stat["mean"]

    def calc_standardization(
        self,
        start_time: datetime = datetime(2021, 1, 1),
        end_time: datetime = datetime(2022, 12, 31),
        sample_size: int = 100,
        num_criteria: int = 1000,
    ) -> None:
        """Calculate the mean and standard deviation from a dataset within a specified time range."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        with open(self._config.data_config_path, "r") as stream:
            data_config = yaml.safe_load(stream)

        with open(BLACKLIST_PATH, "r") as f:
            blacklist = [
                datetime.strptime(line.strip(), "%Y-%m-%d %H:%M")
                for line in f
                if line.strip()
            ]

        data_list = DataCompose.from_config(data_config["train_data"])
        data_gnrt = DataGenerator(data_config["data_shape"], data_config["image_shape"])
        use_Kth_hour_pred = (
            data_config["use_Kth_hour_pred"] if "use_Kth_hour_pred" in data_config else None
        )

        def _progress_one_step(dt, month_cnt):
            dt += timedelta(hours=8)
            if (dt - start_time) / timedelta(days=30) > month_cnt:
                month_cnt += 1
                logging.info(f"now is processing {dt}")
            return dt, month_cnt

        for data_compose in tqdm(data_list):
            dt = start_time
            month_cnt = 0
            container = []
            logging.info(f"start executing {data_compose}")

            if str(data_compose) in self._stat_dict:
                logging.info(
                    f"skip {data_compose} because it already exists in {self._config.standardization_path}"
                )
                continue

            while dt < end_time:
                if (
                    gen_path(dt, data_compose, use_Kth_hour_pred).exists()
                    and dt not in blacklist
                ):
                    data: np.ndarray = data_gnrt.yield_data(
                        dt, data_compose, use_Kth_hour_pred=use_Kth_hour_pred
                    )

                    indices = np.arange(data.size)
                    chosen_indices = np.random.choice(indices, sample_size, replace=False)
                    rows, cols = np.unravel_index(chosen_indices, data.shape)
                    random_values = data[rows, cols]

                    if (
                        data_compose.var_name == DataType.SWDOWN
                        and np.mean(random_values) == 0
                    ):
                        dt, month_cnt = _progress_one_step(dt, month_cnt)
                        continue

                    container.append(random_values)

                dt, month_cnt = _progress_one_step(dt, month_cnt)

            all_data = np.stack(container).flatten()
            lower_bound = np.percentile(all_data, 10)
            upper_bound = np.percentile(all_data, 90)
            filtered_data = all_data[(all_data > lower_bound) & (all_data < upper_bound)]

            if len(filtered_data) < num_criteria:
                logging.info(
                    f"skip {data_compose} because data sample {len(filtered_data)} is not enough"
                )
                continue

            self._stat_dict[str(data_compose)] = {
                "mean": float(np.mean(filtered_data)),
                "std": float(np.std(filtered_data)),
            }

            with open(self._config.standardization_path, "w") as f:
                json.dump(self._stat_dict, f, indent=4)


def get_standardizer(config: RuntimeConfig | None = None) -> Standardizer:
    """Return (or construct) the singleton Standardizer for the current
    process. If ``config`` is provided, a new Standardizer is built and
    cached. If ``config`` is None, the cached instance is returned, or
    one is built from ``get_runtime_config()``.

    .. note:: If multiple entrypoints are run in the same process
              (e.g. tests), the last call with a config wins.
    """
    if not hasattr(get_standardizer, "_singleton"):
        if config is None:
            from .runtime_config import get_runtime_config
            config = get_runtime_config()
        get_standardizer._singleton = Standardizer(config)
    return get_standardizer._singleton