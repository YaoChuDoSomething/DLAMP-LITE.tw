"""Model export runner for converting trained RegPGW models to ONNX.

Produces optimized ONNX artifacts (such as RegPGW+LS+Res.onnx) for fast inference
and deployment.
"""

from pathlib import Path

import torch

from fcn_regpgw.config import RegPGWModelConfig
from fcn_regpgw.const import (
    DEFAULT_REGIONAL_LAT_SIZE,
    DEFAULT_REGIONAL_LON_SIZE,
)
from fcn_regpgw.models.regpgw_lightning import RegPGWLightningModule
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class RegPGWExportRunner:
    """Exports trained RegPGW models to ONNX format.

    Attributes:
        output_path (Path): Destination path for exported ONNX file.
        model_cfg (RegPGWModelConfig): Model architecture configuration.
    """

    def __init__(
        self,
        output_path: Path = Path("weight/RegPGW+LS+Res.onnx"),
        model_cfg: RegPGWModelConfig | None = None,
    ) -> None:
        """Initialize RegPGWExportRunner.

        Args:
            output_path (Path): Target path for .onnx file.
            model_cfg (Optional[RegPGWModelConfig]): Model configuration.
        """
        self.output_path = output_path
        self.model_cfg = model_cfg or RegPGWModelConfig()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        model_or_ckpt: torch.nn.Module | str | Path,
        spatial_shape: tuple[int, int] = (
            DEFAULT_REGIONAL_LAT_SIZE,
            DEFAULT_REGIONAL_LON_SIZE,
        ),
        opset_version: int = 17,
    ) -> Path:
        """Export model to ONNX.

        Args:
            model_or_ckpt (torch.nn.Module | str | Path): PyTorch model instance
                or path to a Lightning checkpoint file.
            spatial_shape (Tuple[int, int]): Height and width for dummy tensor.
            opset_version (int): ONNX opset version.

        Returns:
            Path: Path to saved ONNX model.
        """
        if isinstance(model_or_ckpt, (str, Path)):
            logger.info("Loading weights from checkpoint %s", model_or_ckpt)
            lightning_module = RegPGWLightningModule.load_from_checkpoint(
                str(model_or_ckpt)
            )
            model = lightning_module.model
        else:
            model = model_or_ckpt

        model.eval()
        device = torch.device("cpu")
        model.to(device)

        h, w = spatial_shape
        dummy_input = torch.randn(
            1,
            self.model_cfg.in_channels,
            h,
            w,
            dtype=torch.float32,
            device=device,
        )

        logger.info(
            "Exporting RegPGW model to %s with input shape %s",
            self.output_path,
            dummy_input.shape,
        )

        torch.onnx.export(
            model,
            dummy_input,
            str(self.output_path),
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes={
                "input": {0: "batch_size"},
                "output": {0: "batch_size"},
            },
            dynamo=False,
        )

        logger.info("ONNX export successfully finished: %s", self.output_path)
        return self.output_path
