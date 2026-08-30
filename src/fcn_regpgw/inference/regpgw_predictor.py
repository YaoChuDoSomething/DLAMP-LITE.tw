"""RegPGW regional inference, one-way downscaling, and two-way coupled execution.

Provides inference runners for standalone regional prognostic forecasts driven
by Global FourCastNet boundary conditions and two-way coupled domain feedback.
"""

from pathlib import Path
from typing import Any

import numpy as np

from fcn_regpgw.const import (
    DEFAULT_BOUNDARY_WIDTH,
    NUM_STATIC_CHANNELS,
)
from fcn_regpgw.data.boundary_extractor import BoundaryExtractor, SpongeLayer
from fcn_regpgw.inference.engine import (
    BaseInferenceEngine,
)
from fcn_regpgw.utils.file_util import save_numpy_atomic
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class RegPGWPredictor:
    """Core RegPGW regional neural inference predictor.

    Attributes:
        engine (BaseInferenceEngine): ONNX or PyTorch inference backend.
        sponge_layer (SpongeLayer): Lateral sponge boundary handler.
        static_features (np.ndarray): 6-channel static mask (6, H_reg, W_reg).
    """

    def __init__(
        self,
        engine: BaseInferenceEngine,
        height: int,
        width: int,
        boundary_width: int = DEFAULT_BOUNDARY_WIDTH,
        static_features: np.ndarray | None = None,
    ) -> None:
        """Initialize RegPGWPredictor.

        Args:
            engine (BaseInferenceEngine): Inference engine.
            height (int): Regional domain height.
            width (int): Regional domain width.
            boundary_width (int): Width of sponge layer.
            static_features (Optional[np.ndarray]): Static array of shape
                (6, H, W). If None, initializes zero channels.
        """
        self.engine = engine
        self.height = height
        self.width = width
        self.sponge_layer = SpongeLayer(
            height=height, width=width, boundary_width=boundary_width
        )
        if static_features is not None:
            self.static_features = static_features.astype(np.float32)
        else:
            self.static_features = np.zeros(
                (NUM_STATIC_CHANNELS, height, width), dtype=np.float32
            )

    def predict_step(
        self,
        regional_state_t: np.ndarray,
        boundary_forcing_t1: np.ndarray,
    ) -> np.ndarray:
        """Execute single regional time step.

        Args:
            regional_state_t (np.ndarray): Regional state at t, shape (73, H, W).
            boundary_forcing_t1 (np.ndarray): Boundary driving field at t+dt,
                shape (73, H, W).

        Returns:
            np.ndarray: Predicted next regional state at t+dt, shape (73, H, W).
        """
        # Assemble 152 input channels: (1, 152, H, W)
        inp = np.concatenate(
            [regional_state_t, boundary_forcing_t1, self.static_features],
            axis=0,
        )
        inp_batch = np.expand_dims(inp, axis=0).astype(np.float32)

        pred_raw = self.engine.predict(inp_batch)[0]  # (73, H, W)

        # Apply lateral sponge zone relaxation with boundary forcing
        return self.sponge_layer.blend_boundary(
            pred_raw, boundary_forcing_t1
        )


class RegPGWOneWayDownscaler:
    """One-way regional downscaling driven by Global FourCastNet.

    Attributes:
        global_model (Any): Driving global model.
        regpgw_predictor (RegPGWPredictor): Regional model.
        save_dir (Path): Output directory for saved forecasts.
    """

    def __init__(
        self,
        global_model: Any,
        regpgw_predictor: RegPGWPredictor,
        save_dir: Path = Path("outputs/regpgw_oneway"),
    ) -> None:
        """Initialize RegPGWOneWayDownscaler.

        Args:
            global_model (Any): Global model.
            regpgw_predictor (RegPGWPredictor): Regional predictor.
            save_dir (Path): Output directory.
        """
        self.global_model = global_model
        self.regpgw_predictor = regpgw_predictor
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        initial_global_state: np.ndarray,
        total_hours: int = 240,
        step_hours: int = 6,
    ) -> np.ndarray:
        """Execute full one-way downscaled regional forecast.

        Args:
            initial_global_state (np.ndarray): Global IC of shape (73, 720, 1440).
            total_hours (int): Total forecast horizon in hours.
            step_hours (int): Step interval (6h).

        Returns:
            np.ndarray: Regional forecast trajectory of shape (num_steps + 1, 73, H_reg, W_reg).
        """
        # Step 1: Run Global FourCastNet to generate boundary trajectory
        _, bdry_traj = self.global_model.run_global_rollout(
            initial_state=initial_global_state,
            total_hours=total_hours,
            step_hours=step_hours,
        )

        num_steps = total_hours // step_hours
        logger.info("Executing RegPGW One-Way Downscaling for %d steps", num_steps)

        # Initial regional condition from initial boundary slice
        curr_regional = bdry_traj[0].copy()
        regional_frames = [curr_regional]

        # Save initial lead 0h
        save_numpy_atomic(
            self.save_dir / "regpgw_forecast_000h.npy", curr_regional
        )

        # Sequential regional stepping
        for step in range(1, num_steps + 1):
            lead_hour = step * step_hours
            bdry_t1 = bdry_traj[step]
            next_reg = self.regpgw_predictor.predict_step(
                curr_regional, bdry_t1
            )
            regional_frames.append(next_reg)
            curr_regional = next_reg

            save_numpy_atomic(
                self.save_dir / f"regpgw_forecast_{lead_hour:03d}h.npy",
                curr_regional,
            )

        return np.stack(regional_frames, axis=0)


class RegPGWTwoWayCoupler:
    """Two-way coupled global-regional prognostic forecast runner.

    At each step:
        1. FCNv2 executes a global forecast step.
        2. Boundary forcing is extracted from the global step.
        3. RegPGW executes a regional step conditioned on the boundary forcing.
        4. RegPGW regional forecast is re-injected and blended into the global domain.

    Attributes:
        global_model (Any): Driving global model.
        regpgw_predictor (RegPGWPredictor): Regional model.
        extractor (BoundaryExtractor): Regional domain cropper & paster.
        feedback_weight (float): Relaxation factor for domain re-injection.
        save_dir (Path): Output directory.
    """

    def __init__(
        self,
        global_model: Any,
        regpgw_predictor: RegPGWPredictor,
        extractor: BoundaryExtractor,
        feedback_weight: float = 0.8,
        save_dir: Path = Path("outputs/regpgw_twoway"),
    ) -> None:
        """Initialize RegPGWTwoWayCoupler.

        Args:
            global_model (Any): Global model.
            regpgw_predictor (RegPGWPredictor): Regional model.
            extractor (BoundaryExtractor): Domain boundary extractor.
            feedback_weight (float): Relaxation weight for domain feedback.
            save_dir (Path): Output directory.
        """
        self.global_model = global_model
        self.regpgw_predictor = regpgw_predictor
        self.extractor = extractor
        self.feedback_weight = feedback_weight
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        initial_global_state: np.ndarray,
        total_hours: int = 240,
        step_hours: int = 6,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Execute full two-way coupled global and regional forecast.

        Args:
            initial_global_state (np.ndarray): Global IC (73, 720, 1440).
            total_hours (int): Total forecast horizon in hours.
            step_hours (int): Step delta (6h).

        Returns:
            Tuple[np.ndarray, np.ndarray]: (global_trajectory, regional_trajectory).
        """
        num_steps = total_hours // step_hours
        logger.info("Executing RegPGW Two-Way Coupling for %d steps", num_steps)

        curr_global = initial_global_state.copy()
        if curr_global.ndim == 3:
            curr_global = np.expand_dims(curr_global, axis=0)

        curr_reg = self.extractor.crop_regional_domain(curr_global[0])

        global_frames = [curr_global[0]]
        regional_frames = [curr_reg]

        save_numpy_atomic(
            self.save_dir / "fcn_global_000h.npy", curr_global[0]
        )
        save_numpy_atomic(
            self.save_dir / "regpgw_regional_000h.npy", curr_reg
        )

        for step in range(1, num_steps + 1):
            lead_hour = step * step_hours

            # Step 1: Global FCN step
            next_global_raw = self.global_model.step(curr_global)[0]

            # Step 2: Extract boundary forcing
            bdry_forcing_t1 = self.extractor.crop_regional_domain(next_global_raw)

            # Step 3: Regional RegPGW step
            next_reg = self.regpgw_predictor.predict_step(
                curr_reg, bdry_forcing_t1
            )

            # Step 4: Re-inject regional solution into global domain
            next_global = self.extractor.paste_regional_to_global(
                global_field=next_global_raw,
                regional_field=next_reg,
                blend_mask=None,
            )

            # Record and save
            global_frames.append(next_global)
            regional_frames.append(next_reg)

            save_numpy_atomic(
                self.save_dir / f"fcn_global_{lead_hour:03d}h.npy",
                next_global,
            )
            save_numpy_atomic(
                self.save_dir / f"regpgw_regional_{lead_hour:03d}h.npy",
                next_reg,
            )

            curr_global = np.expand_dims(next_global, axis=0)
            curr_reg = next_reg

        return np.stack(global_frames, axis=0), np.stack(regional_frames, axis=0)
