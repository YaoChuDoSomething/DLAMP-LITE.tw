"""Prediction and multi-model coupling workflow runner for FCN-RegPGW.

Orchestrates inference execution across FCNv2 autoregressive forecasting,
RegPGW one-way downscaling, two-way coupled feedback, precipitation diagnostics,
and ModAFNO temporal interpolation.
"""

from pathlib import Path
from typing import Any

import numpy as np
from torch import nn

from fcn_regpgw.config import AppConfig
from fcn_regpgw.data.ingestion import DataIngestionFactory
from fcn_regpgw.data.standardizer import GlobalStandardizer
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
from fcn_regpgw.inference.temporal_interp import ModAFNOInterpolator
from fcn_regpgw.models.afno import AFNO
from fcn_regpgw.models.modafno import ModAFNO
from fcn_regpgw.models.precip_net import PrecipNet
from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class PredictRunner:
    """Unified orchestration runner for meteorological forecast inference workflows."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize PredictRunner.

        Args:
            config (Optional[AppConfig]): Full application configuration.
        """
        self.config = config or AppConfig()
        self.standardizer: GlobalStandardizer | None = None
        self._init_standardizer()

    def _init_standardizer(self) -> None:
        """Initialize standardizer if statistics files are configured and exist."""
        m_path = self.config.data.global_means_path
        s_path = self.config.data.global_stds_path
        if m_path and s_path and Path(m_path).is_file() and Path(s_path).is_file():
            self.standardizer = GlobalStandardizer.from_files(m_path, s_path)

    def build_engine(
        self,
        weights_path: Path,
        model_type: str = "modafno",
    ) -> BaseInferenceEngine:
        """Instantiate PyTorch or ONNX inference engine matching configuration.

        Args:
            weights_path (Path): Path to model weights or ONNX file.
            model_type (str): Architecture identifier.

        Returns:
            BaseInferenceEngine: Configured inference backend engine.
        """
        if self.config.inference.engine_type == "onnx":
            return ONNXInferenceEngine(
                onnx_path=weights_path,
                device=self.config.inference.device,
            )

        # PyTorch Engine
        name = model_type.lower()
        if "precip" in name:
            model: nn.Module = PrecipNet(
                in_channels=self.config.model.in_channels,
                embed_dim=self.config.model.embed_dim,
                depth=self.config.model.depth,
                num_blocks=self.config.model.num_blocks,
            )
        elif "modafno" in name:
            model = ModAFNO(
                in_channels=self.config.model.in_channels,
                out_channels=self.config.model.out_channels,
                patch_size=self.config.model.patch_size,
                embed_dim=self.config.model.embed_dim,
                mod_dim=self.config.model.mod_dim,
                depth=self.config.model.depth,
                num_blocks=self.config.model.num_blocks,
            )
        else:
            model = AFNO(
                in_channels=self.config.model.in_channels,
                out_channels=self.config.model.out_channels,
                patch_size=self.config.model.patch_size,
                embed_dim=self.config.model.embed_dim,
                depth=self.config.model.depth,
                num_blocks=self.config.model.num_blocks,
            )

        return PyTorchInferenceEngine(
            model=model,
            weights_path=weights_path if weights_path.is_file() else None,
            device=self.config.inference.device,
        )

    def run(
        self,
        initial_condition: np.ndarray | None = None,
        custom_engine: BaseInferenceEngine | None = None,
    ) -> Any:
        """Dispatch and execute inference workflow based on configured mode.

        Args:
            initial_condition (Optional[np.ndarray]): Initial atmospheric state array.
            custom_engine (Optional[BaseInferenceEngine]): Custom inference engine override.

        Returns:
            Any: Saved file paths or forecast artifacts.

        Raises:
            ValueError: If initial condition is missing or mode is unsupported.
        """
        mode = self.config.inference.mode.lower()
        out_dir = ensure_dir(self.config.inference.output_dir)
        logger.info("Executing PredictRunner for mode: %s", mode)

        # Load IC if not provided explicitly
        ic = initial_condition
        if ic is None and self.config.data.initial_condition_path:
            loader = DataIngestionFactory.create(
                self.config.data.initial_condition_path
            )
            ic = loader.load(
                self.config.data.initial_condition_path,
                lat_size=self.config.data.lat_size,
                lon_size=self.config.data.lon_size,
            )

        if mode == "fcnv2":
            if ic is None:
                raise ValueError("Initial condition required for FCNv2 forecast.")
            engine = custom_engine or self.build_engine(
                self.config.inference.weights_path, model_type="afno"
            )
            predictor = FCNv2Predictor(
                engine=engine, standardizer=self.standardizer
            )
            return predictor.run_forecast(
                initial_condition=ic,
                forecast_hours=self.config.inference.forecast_hours,
                step_hours=self.config.data.lead_time_step_hours,
                output_dir=out_dir,
            )

        elif mode == "pgw_oneway":
            pgw_weights = (
                self.config.inference.pgw_weights_path
                or self.config.inference.weights_path
            )
            engine = custom_engine or self.build_engine(
                pgw_weights, model_type="afno"
            )
            pgw_predictor = PGWOneWayPredictor(
                pgw_engine=engine, standardizer=self.standardizer
            )
            return pgw_predictor.run_downscaling(
                fcnv2_output_dir=self.config.data.data_dir,
                output_dir=out_dir,
                forecast_hours=self.config.inference.forecast_hours,
                step_hours=self.config.data.lead_time_step_hours,
            )

        elif mode == "pgw_twoway":
            if ic is None:
                raise ValueError("Initial condition required for two-way forecast.")
            fcn_engine = custom_engine or self.build_engine(
                self.config.inference.weights_path, model_type="afno"
            )
            pgw_weights = (
                self.config.inference.pgw_weights_path
                or self.config.inference.weights_path
            )
            pgw_engine = self.build_engine(pgw_weights, model_type="afno")
            two_way = PGWTwoWayPredictor(
                fcnv2_engine=fcn_engine,
                pgw_engine=pgw_engine,
                standardizer=self.standardizer,
            )
            return two_way.run_coupled_forecast(
                initial_condition=ic,
                forecast_hours=self.config.inference.forecast_hours,
                step_hours=self.config.data.lead_time_step_hours,
                output_dir=out_dir,
            )

        elif "precip" in mode:
            engine = custom_engine or self.build_engine(
                self.config.inference.weights_path, model_type="precip"
            )
            precip_pred = PrecipPredictor(
                engine=engine, standardizer=self.standardizer
            )
            return precip_pred.run_prediction(
                weather_data_dir=self.config.data.data_dir,
                output_dir=out_dir,
                forecast_hours=self.config.inference.forecast_hours,
                step_hours=self.config.data.lead_time_step_hours,
            )

        elif "temporal_interp" in mode:
            engine = custom_engine or self.build_engine(
                self.config.inference.weights_path, model_type="modafno"
            )
            interp = ModAFNOInterpolator(
                engine=engine,
                standardizer=self.standardizer,
                lat_size=self.config.data.lat_size,
                lon_size=self.config.data.lon_size,
            )
            intervals = (
                self.config.inference.forecast_hours
                // self.config.data.lead_time_step_hours
            )
            return interp.run_interpolation(
                input_folder=self.config.data.data_dir,
                output_folder=out_dir,
                initial_time_str=self.config.inference.initial_time_str,
                num_6h_intervals=intervals,
            )
        else:
            raise ValueError(f"Unsupported prediction mode: {mode}")
