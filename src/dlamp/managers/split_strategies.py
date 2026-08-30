"""Train/valid/test split strategies for the DatetimeManager.

Each strategy owns one way of partitioning an ordered list of initial
times into three disjoint sets. ``DatetimeManager`` composes the chosen
strategy rather than inlining the split logic, so adding a new split
method means writing one strategy module, not editing ``DatetimeManager``.
"""

from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime
from typing import Protocol

import numpy as np


class TimeSplitStrategy(Protocol):
    """Split an ordered list of initial times into train/valid/test.

    Strategies are stateless and return three disjoint set instances.
    """

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        """Return ``(train_time, valid_time, test_time)``."""

    def __call__(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        return self.split(time_list, ratios)


class RandomSplit(TimeSplitStrategy):
    """Shuffle the whole range and split by normalized ratios."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()
        ratios = ratios * len(time_list)

        shuffled = time_list.copy()
        random.seed(1000)
        random.shuffle(shuffled)

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        for category, category_idx in {"train": 0, "valid": 1, "test": 2}.items():
            start_idx = int(np.sum(ratios[:category_idx]))
            end_idx = int(np.sum(ratios[: category_idx + 1]))
            target = {"train": train_time, "valid": valid_time, "test": test_time}[category]
            target.update(shuffled[start_idx:end_idx])
        return train_time, valid_time, test_time


class SequentialSplit(TimeSplitStrategy):
    """Assign times round-robin in fixed chunks of ``max(ratios) * 10``."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()
        ratios = np.round(ratios * 10).astype(int)
        chunk_size = int(ratios.sum())

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        time_array = np.array(time_list)
        for i in range(chunk_size):
            chunk = time_array[i::chunk_size]
            if i < ratios[0]:
                train_time.update(chunk)
            elif i >= chunk_size - ratios[-1]:
                test_time.update(chunk)
            else:
                valid_time.update(chunk)
        return train_time, valid_time, test_time


class HalfMonthSplit(TimeSplitStrategy):
    """Group times by calendar half-month, shuffle groups, then assign."""

    def split(
        self, time_list: list[datetime], ratios: list[float | int]
    ) -> tuple[set[datetime], set[datetime], set[datetime]]:
        ratios = np.array(ratios, dtype=float)
        ratios = ratios / ratios.sum()

        groups: dict[str, list[datetime]] = defaultdict(list)
        for dt in time_list:
            half = "1st_half" if dt.day <= 15 else "2nd_half"
            groups[f"{dt.strftime('%b')}_{half}"].append(dt)

        group_list = list(groups.values())
        random.seed(1000)
        random.shuffle(group_list)

        num_groups = len(group_list)
        train_end = int(num_groups * ratios[0])
        valid_end = int(num_groups * (ratios[0] + ratios[1]))

        train_time: set[datetime] = set()
        valid_time: set[datetime] = set()
        test_time: set[datetime] = set()
        for i, group in enumerate(group_list):
            if i < train_end:
                train_time.update(group)
            elif i < valid_end:
                valid_time.update(group)
            else:
                test_time.update(group)
        return train_time, valid_time, test_time


def get_split_strategy(split_method: str) -> TimeSplitStrategy:
    """Return the split strategy registered for ``split_method``.

    Args:
        split_method: One of ``"random"``, ``"sequential"``, ``"half_month"``.

    Returns:
        The matching ``TimeSplitStrategy`` instance.

    Raises:
        ValueError: If ``split_method`` is not registered.
    """
    strategies: dict[str, TimeSplitStrategy] = {
        "random": RandomSplit(),
        "sequential": SequentialSplit(),
        "half_month": HalfMonthSplit(),
    }
    try:
        return strategies[split_method]
    except KeyError as exc:
        raise ValueError(
            f"Invalid split_method '{split_method}'. "
            f"Available: {', '.join(sorted(strategies))}"
        ) from exc