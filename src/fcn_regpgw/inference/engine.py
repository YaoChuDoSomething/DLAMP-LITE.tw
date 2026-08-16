"""Inference engine abstractions for PyTorch and ONNX Runtime backends.

Provides safe checkpoint loading, execution management, device placement,
and unified prediction interfaces.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from fcn_regpgw.utils.file_util import safe_load_weights
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class BaseInferenceEngine(ABC):
    """Abstract interface for model inference backends."""

    @abstractmethod
    def predict(
        self,
        x: np.ndarray | torch.Tensor,
        **kwargs: Any,
    ) -> np.ndarray:
        """Run model prediction on input data.

        Args:
            x (Union[np.ndarray, torch.Tensor]): Input data tensor.
            **kwargs: Extra parameters (e.g. modulation timestep).

        Returns:
            np.ndarray: Model prediction array on CPU.
        """
        raise NotImplementedError


class PyTorchInferenceEngine(BaseInferenceEngine):
    """PyTorch execution backend with safe deserialization and device management."""

    def __init__(
        self,
        model: nn.Module,
        weights_path: str | Path | None = None,
        device: str = "cpu",
    ) -> None:
        """Initialize PyTorch inference engine.

        Args:
            model (nn.Module): Instantiated PyTorch model architecture.
            weights_path (Optional[Union[str, Path]]): Path to checkpoint file.
            device (str): Compute device ('cuda' or 'cpu').
        """
        self.device = torch.device(device)
        self.model = model

        if weights_path:
            state_dict = safe_load_weights(weights_path, device=device)
            # Remove any unwanted buffer keys from checkpoint
            state_dict.pop("device_buffer", None)
            state_dict.pop("backbone.device_buffer", None)
            # Strip potential 'model.' prefix if saved from LightningModule
            clean_state_dict: dict[str, Any] = {}
            for k, v in state_dict.items():
                new_key = k.removeprefix("model.")
                clean_state_dict[new_key] = v
            try:
                self.model.load_state_dict(clean_state_dict, strict=True)
            except RuntimeError as exc:
                logger.warning(
                    "Strict weight loading failed (%s). Retrying non-strict.",
                    exc,
                )
                self.model.load_state_dict(clean_state_dict, strict=False)

        self.model.to(self.device)
        self.model.eval()
        logger.info(
            "Initialized PyTorchInferenceEngine on device: %s", self.device
        )

    def predict(
        self,
        x: np.ndarray | torch.Tensor,
        **kwargs: Any,
    ) -> np.ndarray:
        """Execute forward pass under torch.no_grad().

        Args:
            x (Union[np.ndarray, torch.Tensor]): Input state.
            **kwargs: Additional tensors like modulation timestep 't'.

        Returns:
            np.ndarray: Predicted atmospheric state array.
        """
        if isinstance(x, np.ndarray):
            x_tensor = torch.from_numpy(x).float()
        else:
            x_tensor = x.float()

        if x_tensor.ndim == 3:
            # (C, H, W) -> (1, C, H, W)
            x_tensor = x_tensor.unsqueeze(0)

        x_tensor = x_tensor.to(self.device)

        t_val = kwargs.get("t", None)
        with torch.no_grad():
            if t_val is not None:
                if isinstance(t_val, (float, int)):
                    t_tensor = torch.tensor([float(t_val)], dtype=torch.float32)
                elif isinstance(t_val, np.ndarray):
                    t_tensor = torch.from_numpy(t_val).float()
                else:
                    t_tensor = t_val.float()
                t_tensor = t_tensor.to(self.device)
                out = self.model(x_tensor, t_tensor)
            else:
                out = self.model(x_tensor)

        return out.detach().cpu().numpy()


class ONNXInferenceEngine(BaseInferenceEngine):
    """ONNX Runtime execution backend."""

    def __init__(
        self,
        onnx_path: str | Path,
        device: str = "cpu",
    ) -> None:
        """Initialize ONNX Runtime inference session.

        Args:
            onnx_path (Union[str, Path]): Path to exported .onnx model file.
            device (str): Target device ('cuda' or 'cpu').

        Raises:
            ImportError: If onnxruntime is not installed.
            FileNotFoundError: If onnx_path does not exist.
        """
        try:
            import onnxruntime as ort  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "onnxruntime is required for ONNXInferenceEngine."
            ) from exc

        path = Path(onnx_path)
        if not path.is_file():
            raise FileNotFoundError(f"ONNX model file not found: {path}")

        providers: list[str] = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device.startswith("cuda")
            else ["CPUExecutionProvider"]
        )

        logger.info(
            "Initializing ONNX session from %s with providers: %s",
            path,
            providers,
        )
        self.session = ort.InferenceSession(str(path), providers=providers)
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

    def predict(
        self,
        x: np.ndarray | torch.Tensor,
        **kwargs: Any,
    ) -> np.ndarray:
        """Execute ONNX graph inference.

        Args:
            x (Union[np.ndarray, torch.Tensor]): Input tensor.
            **kwargs: Extra feed inputs.

        Returns:
            np.ndarray: Predicted output array.
        """
        if isinstance(x, torch.Tensor):
            x_arr = x.detach().cpu().numpy().astype(np.float32)
        else:
            x_arr = np.asarray(x, dtype=np.float32)

        if x_arr.ndim == 3:
            x_arr = x_arr[np.newaxis, ...]

        feeds: dict[str, np.ndarray] = {self.input_names[0]: x_arr}

        if len(self.input_names) > 1 and "t" in kwargs:
            t_val = kwargs["t"]
            t_arr = np.asarray([t_val], dtype=np.float32).reshape(-1, 1)
            feeds[self.input_names[1]] = t_arr

        outputs = self.session.run(self.output_names, feeds)
        return outputs[0]
