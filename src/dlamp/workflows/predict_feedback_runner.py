"""Two-way boundary-feedback inference workflow runner for DLAMP.

Executes the auto-regression loop with boundary re-injection at **every
model time-step**.  At each 1-hour step the boundary ring of the
predicted field is overwritten with observations loaded from disk before
the prediction is fed back as the next input — this is the "two-way
feedback" or "nudging" mode that prevents error accumulation near the
domain edges.

The feedback is implemented by setting a non-null ``bdy_swap_method``
in the Hydra config, which the underlying
``BatchInferenceOnnx.infer()`` / ``BatchInferenceCkpt.infer()`` loop
already accepts.  This runner validates that the required config keys
are present and provides a descriptive error if the caller forgets to
set them.

Decision record (Q1 from implementation plan):
    Boundary re-injection fires at every model time-step (the 1-hour
    inner loop in ``BatchInferenceOnnx.infer``), not only at
    ``output_itv`` intervals.  This is the strongest form of nudging
    and matches the "two-way" naming convention from the WRF literature.
    If you want nudging only at output intervals, set
    ``inference.bdy_swap_method`` to ``null`` in ``predict_dscale.yaml``
    and apply the swap yourself in post-processing.

Raises:
    ValueError: If ``cfg.inference.bdy_swap_method`` is null — the
        feedback runner requires a concrete swap method.
"""

import logging
from typing import Any

from omegaconf import DictConfig, OmegaConf

from dlamp.analysis.prediction import PredictionRunner

logger = logging.getLogger(__name__)


class PredictFeedbackRunner:
    """Runs the two-way boundary-feedback inference workflow.

    Extends the one-way downscaling approach by enforcing a non-null
    ``bdy_swap_method`` so that boundary conditions from ground-truth
    observations are blended into the model state at every auto-
    regression step.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        _predictor (PredictionRunner): The underlying prediction engine.
    """

    def __init__(self, cfg: DictConfig) -> None:
        """Initialises the PredictFeedbackRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object.  Must
                contain:
                - ``inference.bdy_swap_method`` (dict): A non-null dict
                  with at least ``name`` (str) and ``n_of_grid`` (int)
                  keys identifying the blending kernel and the number of
                  boundary grid cells to replace.
                - ``inference.feedback_iters`` (int): Documented key for
                  future use — currently informational only, as the
                  feedback loop length is determined by
                  ``showcase_length`` and ``output_itv`` in the base
                  class.

        Raises:
            ValueError: If ``cfg.inference.bdy_swap_method`` is null or
                missing.
        """
        self.cfg = cfg
        self._validate_feedback_config()
        self._predictor: PredictionRunner = PredictionRunner(cfg)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Executes the two-way boundary-feedback inference.

        The ``bdy_swap_method`` configured in Hydra is forwarded to
        ``InferenceBase.infer()``, which calls
        ``_boundary_swapping()`` at every model time-step inside the
        auto-regression loop.

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
        method_name: str = self.cfg.inference.bdy_swap_method["name"]
        n_grid: int = self.cfg.inference.bdy_swap_method["n_of_grid"]
        logger.info(
            "PredictFeedbackRunner: two-way feedback enabled "
            "(method=%s, n_of_grid=%d)",
            method_name,
            n_grid,
        )
        results = self._predictor.run()
        logger.info("PredictFeedbackRunner: inference with feedback complete")
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_feedback_config(self) -> None:
        """Validates that the feedback-specific config keys are present.

        Raises:
            ValueError: If ``cfg.inference.bdy_swap_method`` is null or
                missing the required ``name`` / ``n_of_grid`` sub-keys.
        """
        bdy_method = OmegaConf.select(self.cfg, "inference.bdy_swap_method")
        if not bdy_method:
            raise ValueError(
                "PredictFeedbackRunner requires cfg.inference.bdy_swap_method "
                "to be a non-null dict with 'name' and 'n_of_grid' keys. "
                "Got: null. "
                "Set bdy_swap_method in config/predict_feedback.yaml or pass "
                "'inference.bdy_swap_method.name=<method>' on the CLI."
            )
        for key in ("name", "n_of_grid"):
            if key not in bdy_method:
                raise ValueError(
                    f"cfg.inference.bdy_swap_method is missing key '{key}'. "
                    f"Current value: {dict(bdy_method)}"
                )
