"""Global FourCastNet (FCN / AFNO / SFNO) driving model interface.

FourCastNet acts as the global background model, generating global forecast
trajectories and providing lateral driving boundary conditions for regional
RegPGW models.
"""

import numpy as np

from fcn_regpgw.config import GlobalFCNInferenceConfig
from fcn_regpgw.const import (
    DEFAULT_REGIONAL_BOUNDS,
)
from fcn_regpgw.data.boundary_extractor import BoundaryExtractor
from fcn_regpgw.inference.engine import (
    BaseInferenceEngine,
    ONNXInferenceEngine,
    PyTorchInferenceEngine,
)
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


class GlobalFCNDrivingModel:
    """Pre-trained Global FourCastNet engine for driving boundary generation.

    Attributes:
        config (GlobalFCNInferenceConfig): Global FCN inference configuration.
        engine (BaseInferenceEngine): Execution engine (ONNX or PyTorch).
        extractor (BoundaryExtractor): Regional slice extractor.
    """

    def __init__(
        self,
        config: GlobalFCNInferenceConfig | None = None,
        regional_bounds: tuple[int, int, int, int] = DEFAULT_REGIONAL_BOUNDS,
        engine: BaseInferenceEngine | None = None,
    ) -> None:
        """Initialize GlobalFCNDrivingModel.

        Args:
            config (Optional[GlobalFCNInferenceConfig]): Inference config.
            regional_bounds (Tuple[int, int, int, int]): Regional subgrid bounds.
            engine (Optional[BaseInferenceEngine]): Custom inference engine.
        """
        self.config = config or GlobalFCNInferenceConfig()
        self.regional_bounds = regional_bounds
        self.extractor = BoundaryExtractor(bounds=regional_bounds)

        if engine is not None:
            self.engine = engine
        else:
            self.engine = self._init_engine()

    def _init_engine(self) -> BaseInferenceEngine:
        """Instantiate ONNX or PyTorch backend for Global FCN.

        Returns:
            BaseInferenceEngine: Configured engine.
        """
        if self.config.engine_type.lower() == "onnx":
            return ONNXInferenceEngine(
                model_path=self.config.model_path,
                device=self.config.device,
            )
        return PyTorchInferenceEngine(
            model_path=self.config.model_path,
            device=self.config.device,
        )

    def step(self, global_state: np.ndarray) -> np.ndarray:
        """Execute single 6-hour global forecast step.

        Args:
            global_state (np.ndarray): Global state array of shape
                (1, 73, 720, 1440) or (73, 720, 1440).

        Returns:
            np.ndarray: Predicted next global state of shape (1, 73, 720, 1440).
        """
        if global_state.ndim == 3:
            global_state = np.expand_dims(global_state, axis=0)

        # In case the model requires static channel concatenation (e.g. 73 -> 73 or 79 -> 73)
        return self.engine.predict(global_state)

    def extract_regional_boundary(
        self, global_state: np.ndarray
    ) -> np.ndarray:
        """Extract regional slice from a global state array.

        Args:
            global_state (np.ndarray): Global state array (..., 720, 1440).

        Returns:
            np.ndarray: Regional subgrid array (..., H_reg, W_reg).
        """
        return self.extractor.crop_regional_domain(global_state)

    def run_global_rollout(
        self,
        initial_state: np.ndarray,
        total_hours: int = 240,
        step_hours: int = 6,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Run multi-step global forecast and extract regional boundary trajectory.

        Args:
            initial_state (np.ndarray): Global initial conditions (73, 720, 1440).
            total_hours (int): Total forecast horizon in hours.
            step_hours (int): Global step delta (6h).

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - global_trajectory: (num_steps + 1, 73, 720, 1440)
                - regional_boundaries: (num_steps + 1, 73, H_reg, W_reg)
        """
        num_steps = total_hours // step_hours
        logger.info(
            "Running Global FourCastNet rollout for %d hours (%d steps)",
            total_hours,
            num_steps,
        )

        curr_state = initial_state.copy()
        if curr_state.ndim == 3:
            curr_state = np.expand_dims(curr_state, axis=0)

        global_frames = [curr_state[0]]
        regional_frames = [self.extract_regional_boundary(curr_state[0])]

        for step in range(1, num_steps + 1):
            next_state = self.step(curr_state)
            global_frames.append(next_state[0])
            regional_frames.append(self.extract_regional_boundary(next_state[0]))
            curr_state = next_state

        global_traj = np.stack(global_frames, axis=0)
        regional_bounds = np.stack(regional_frames, axis=0)
        return global_traj, regional_bounds
