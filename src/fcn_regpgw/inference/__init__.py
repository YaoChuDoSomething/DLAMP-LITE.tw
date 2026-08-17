"""Inference engines, predictors, downscalers, and coupling for FCN-RegPGW."""

from fcn_regpgw.inference.engine import (
    BaseInferenceEngine,
    ONNXInferenceEngine,
    PyTorchInferenceEngine,
)
from fcn_regpgw.inference.fcnv2_predictor import FCNv2Predictor
from fcn_regpgw.inference.pgw_coupling import (
    PGWOneWayPredictor,
    PGWTwoWayPredictor,
)
from fcn_regpgw.inference.precip_predictor import PrecipPredictor
from fcn_regpgw.inference.regpgw_predictor import (
    RegPGWOneWayDownscaler,
    RegPGWPredictor,
    RegPGWTwoWayCoupler,
)
from fcn_regpgw.inference.temporal_interp import ModAFNOInterpolator

__all__ = [
    "BaseInferenceEngine",
    "FCNv2Predictor",
    "ModAFNOInterpolator",
    "ONNXInferenceEngine",
    "PGWOneWayPredictor",
    "PGWTwoWayPredictor",
    "PrecipPredictor",
    "PyTorchInferenceEngine",
    "RegPGWOneWayDownscaler",
    "RegPGWPredictor",
    "RegPGWTwoWayCoupler",
]
