# FILE: analysis/prediction.py
"""Module for running the weather model inference.

This module provides the PredictionRunner class, which encapsulates the
logic for setting up and executing a model inference session based on a
Hydra configuration.
"""

import importlib
import logging
from datetime import datetime
from typing import Any, Dict, Type

import numpy as np
from omegaconf import DictConfig

from inference import InferenceBase
from src.utils import DataCompose, DataGenerator

logger = logging.getLogger(__name__)


class PredictionRunner:
    """Handles the setup and execution of the model inference process.

    This class reads the configuration, initializes the appropriate
    inference engine (either from a checkpoint or ONNX), runs the
    prediction, and returns the results in memory.

    Attributes:
        cfg (DictConfig): The Hydra configuration object.
        eval_cases (List[datetime]): A list of timestamps for evaluation.
        infer_machine (InferenceBase): The instantiated inference engine.
    """


    def __init__(self, cfg: DictConfig):
        """Initializes the PredictionRunner.

        Args:
            cfg (DictConfig): The Hydra configuration object that defines
                the model, data, and inference settings.
        """
        self.cfg = cfg
        self.eval_cases = [
            datetime.strptime(cfg.data.start_time, cfg.data.format)
        ]
        self.infer_machine: InferenceBase = self._setup_inference_machine()

    def _setup_inference_machine(self) -> InferenceBase:
        """Sets up the inference engine based on the configuration.

        Dynamically imports and instantiates the correct inference class
        (e.g., 'BatchInferenceCkpt' or 'BatchInferenceOnnx').

        Raises:
            ValueError: If the 'infer_type' in the config is not supported.

        Returns:
            InferenceBase: An initialized instance of the inference engine.
        """
        infer_type: str = self.cfg.inference.infer_type
        INFERENCE_CLASSES = {
            "ckpt": ("inference.batch_inference_ckpt", "BatchInferenceCkpt"),
            "onnx": ("inference.batch_inference_onnx", "BatchInferenceOnnx"),
        }

        if infer_type not in INFERENCE_CLASSES:
            raise ValueError(f"Unsupported inference type: {infer_type}")

        module_name, class_name = INFERENCE_CLASSES[infer_type]

        try:
            module = importlib.import_module(module_name)
            infer_class: Type[InferenceBase] = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            logger.error("Failed to load inference class: %s", e)
            raise

        return infer_class(self.cfg, self.eval_cases)

    def run(self) -> Dict[str, Any]:
        """Executes the full inference workflow.

        This method runs the model prediction and then generates the
        corresponding latitude and longitude grids. It returns all results
        as a dictionary, avoiding file I/O for intermediate data.

        Returns:
            Dict[str, Any]: A dictionary containing the prediction results,
                including:
                - 'output_upper' (np.ndarray): Upper-air variables.
                - 'output_surface' (np.ndarray): Surface variables.
                - 'lat' (np.ndarray): Latitude grid.
                - 'lon' (np.ndarray): Longitude grid.
                - 'start_time' (datetime): The forecast start time.
        """
        logger.info("Starting model inference...")
        self.infer_machine.infer(
            bdy_swap_method=self.cfg.inference.bdy_swap_method
        )
        logger.info("Inference complete.")

        # Prepare latitude and longitude grids
        data_gnrt: DataGenerator = self.infer_machine.data_manager.data_gnrt
        dc_lat: DataCompose
        dc_lon: DataCompose
        dc_mask: DataCompose
        dc_lat, dc_lon, dc_mask = DataCompose.from_config(
                {"Lat": ["NoRule"], "Lon": ["NoRule"], "MASK": ["NoRule"]}
        )
        start_time: datetime = datetime.strptime(
            self.cfg.data.start_time, self.cfg.data.format
        )
        lat: np.ndarray = data_gnrt.yield_data(start_time, dc_lat)
        lon: np.ndarray = data_gnrt.yield_data(start_time, dc_lon)
        mask: np.ndarray = data_gnrt.yield_data(start_time, dc_mask)

        return {
            "output_upper": self.infer_machine.output_upper,
            "output_surface": self.infer_machine.output_surface,
            "lat": lat,
            "lon": lon,
            "mask": mask,
            "start_time": start_time,
        }
