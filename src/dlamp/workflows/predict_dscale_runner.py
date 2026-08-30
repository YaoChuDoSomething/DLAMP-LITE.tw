"""One-way downscaling inference workflow runner for the DLAMP pipeline.

Executes model auto-regression in the forward direction only —
no boundary values from ground-truth are re-injected during the
prediction loop.  This is the simplest inference mode and is equivalent
to the existing ``predict.py`` workflow with
``inference.bdy_swap_method`` set to ``null``.

The runner delegates to ``analysis.PredictionRunner`` (the same class
used by ``predict.py``) and returns its result dict unchanged so that
callers can pipe it through the same saving and plotting helpers.

Raises:
    ValueError: If the configuration is invalid.
    ModuleNotFoundError: If the specified inference engine module cannot
        be imported.
"""

import logging
from typing import Any

from omegaconf import DictConfig

from dlamp.analysis.prediction import PredictionRunner

logger = logging.getLogger(__name__)


class PredictDscaleRunner:
    """Runs the one-way downscaling (no feedback) inference workflow.

    Thin wrapper around ``PredictionRunner`` that forces the boundary-
    swap method to ``None`` for the standard downscaling use-case.
    Boundary override can still be enabled by setting
    ``inference.bdy_swap_method`` in the Hydra config to a non-null
    dict — the runner passes the config through unchanged.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        _predictor (PredictionRunner): The underlying prediction engine.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the PredictDscaleRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  The
                ``inference.bdy_swap_method`` key is expected to be
                ``null`` for pure downscaling.  If it is set to a dict
                it will be forwarded to the auto-regression loop as-is.
        """
        self.cfg = cfg
        self._predictor: PredictionRunner = PredictionRunner(cfg)

    def run(self) -> dict[str, Any]:
        """Executes the one-way downscaling inference.

        Returns:
            dict[str, Any]: Prediction results as returned by
                ``PredictionRunner.run()``, containing:
                - ``output_upper`` (np.ndarray): Upper-air predictions.
                - ``output_surface`` (np.ndarray): Surface predictions.
                - ``lat`` (np.ndarray): Latitude grid.
                - ``lon`` (np.ndarray): Longitude grid.
                - ``mask`` (np.ndarray): Land-sea mask.
                - ``start_time`` (datetime): Forecast start time.
        """
        logger.info("PredictDscaleRunner: starting one-way downscaling inference")
        results = self._predictor.run()
        logger.info("PredictDscaleRunner: inference complete")
        return results
