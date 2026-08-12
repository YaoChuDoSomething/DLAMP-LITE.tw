"""Tests for Diagnostic modules."""

import torch
from unittest.mock import Mock, patch

from dlamp.diagnostics import DataQualityChecker, AnomalyDetection


def test_data_quality_checker() -> None:
    """Test DataQualityChecker detects anomalies."""
    checker = DataQualityChecker()
    # Mock input data with some anomalies
    x = torch.randn(10, 3, 64, 64)
    # Should detect anomalies in the data
    anomalies = checker.check(x)
    assert isinstance(anomalies, list)
    assert len(anomalies) > 0


def test_anomaly_detection() -> None:
    """Test AnomalyDetection identifies outliers."""
    detector = AnomalyDetection()
    # Input with known outlier
    x = torch.randn(5, 3, 64, 64)
    # Add an outlier
    x[0, :, :, :] = torch.tensor([999.0] * 64 * 64)
    predictions = detector.predict(x)
    # Should flag the outlier
    assert len(predictions) == 5
    # At least one prediction should indicate anomaly
    assert any(prediction > 0.5 for prediction in predictions)
