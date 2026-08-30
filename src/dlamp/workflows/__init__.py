"""Workflow runner classes for the DLAMP pipeline.

This subpackage provides thin, testable runner objects that implement
the business logic for each Hydra entrypoint.  The entrypoints at the
repository root are intentionally kept small — they perform only Hydra
bootstrapping, singleton initialisation, and delegation to these runners.

Exported runners:
    DataPrepRunner       — constant-mask generation (``data_prep.py``)
    DataStatsRunner      — z-score statistics computation (``data_stats.py``)
    PredictDscaleRunner  — one-way downscaling inference (``predict_dscale.py``)
    PredictFeedbackRunner — two-way boundary-feedback inference
                           (``predict_feedback.py``)
"""

from .data_prep_runner import DataPrepRunner
from .data_stats_runner import DataStatsRunner
from .predict_dscale_runner import PredictDscaleRunner
from .predict_feedback_runner import PredictFeedbackRunner

__all__ = [
    "DataPrepRunner",
    "DataStatsRunner",
    "PredictDscaleRunner",
    "PredictFeedbackRunner",
]
