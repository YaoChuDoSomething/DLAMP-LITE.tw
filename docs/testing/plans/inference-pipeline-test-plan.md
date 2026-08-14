# Inference Pipeline Test Plan

## 1. Scope & Target Submodules

- `dlamp.analysis.prediction` (`PredictionRunner`, `predict.py`)
- `dlamp.inference.batch_inference_onnx` (`ONNXBatchInference`)
- `dlamp.inference.batch_inference_ckpt` (`PyTorchBatchInference`)
- `dlamp.workflows` (`PredictDscaleRunner`, `PredictFeedbackRunner`)

## 2. Unit Test Specifications

- `tests/dlamp/inference/test_batch_inference_onnx.py`: Test ONNX runtime session initialization and input tensor binding.
- `tests/dlamp/inference/test_batch_inference_ckpt.py`: Test PyTorch checkpoint loading and step inference execution.
- `tests/dlamp/analysis/test_prediction.py`: Test forecast loop orchestration, multi-step autoregression, and output NetCDF writing.
- `tests/dlamp/workflows/test_predict_runners.py`: Test downscaling and boundary feedback inference runner setup.

## 3. Integration Test Scenarios (`@pytest.mark.integration`)

- Run a 3-hour inference pass with sample input data and ONNX model runtime.

## 4. Regression Test Specifications (`@pytest.mark.regression`)

- Compare forecast NetCDF variable fields (temperature, wind, precipitation) against pre-move golden outputs in `DLAMP_DATA_PATH/regression_golden/`.
- Tolerance: `rtol=1e-5`, `atol=1e-6`.

## 5. Fixtures & Environment Requirements

- ONNX model file fixture in `export/` or mock session.
- Sample Standardization JSON file for experiment code.

## 6. Target Coverage & Acceptance Criteria

- Target Line Coverage: >85%
- Multi-step forecast generation produces valid NetCDF files with correct dimensions (`time`, `latitude`, `longitude`, `level`).
