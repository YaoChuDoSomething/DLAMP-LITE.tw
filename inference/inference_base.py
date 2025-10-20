import abc
import logging
import warnings
from datetime import datetime, timedelta

import numpy as np
from omegaconf import DictConfig
from scipy.fft import fft2, ifft2, fftshift, ifftshift
from scipy.ndimage import distance_transform_cdt
from tqdm import trange

from src.datasets import CustomDataset
from src.debug.boundary_plots import (
    BoundaryPlotData,
    FFTPlotData,
    plot_bdy_blending_debug,
    plot_fft_blending_debug,
)
from src.managers import DataManager, DatetimeManager
from src.utils import DataCompose, DataGenerator, DataType, Level

logger = logging.getLogger(__name__)


class InferenceBase(metaclass=abc.ABCMeta):
    def __init__(self, cfg: DictConfig, eval_cases: list[datetime] | None = None):
        # args
        self.cfg = cfg
        self.eval_cases = eval_cases

        # useful properties
        self.data_list = DataCompose.from_config(self.cfg.data.train_data)
        self.data_itv = timedelta(**self.cfg.data.time_interval)
        self.output_itv = timedelta(**self.cfg.inference.output_itv)
        self.showcase_length = self.cfg.plot.figure_columns
        self.pressure_lv: list[Level] = DataCompose.get_all_levels(
            self.data_list, only_upper=True
        )
        self.upper_vars: list[DataType] = DataCompose.get_all_vars(
            self.data_list, only_upper=True
        )
        self.surface_vars: list[DataType] = DataCompose.get_all_vars(
            self.data_list, only_surface=True
        )

        # data manager
        self.init_time_list = self.build_init_time_list()
        self.data_manager = DataManager(
            self.data_list,
            **self.cfg.data,
            **self.cfg.lightning,
            init_time_list=self.init_time_list,
        )
        self.data_manager.setup("predict")

        # custom setup
        self._setup()

    def build_init_time_list(self) -> list[datetime] | None:
        """
        Builds a list of initial time for evaluation.

        This function make sure all the initial time are valid during entire showcase length.
        And also make sure their forecast time exists.

        Returns:
            list[datetime | None]: A sorted list of initial times for evaluation.

        Raises:
            ValueError: If the sanity check fails for the initial time or forecast time.

        """
        if self.eval_cases is None:
            warnings.warn(
                "No custom eval cases are provided, using default EVAL_CASES defined in `src.const`.",
                UserWarning,
            )
            return None

        init_time_list = set()
        for eval_case in self.eval_cases:
            for num in range(self.showcase_length):
                fcst_time = eval_case + self.output_itv * num

                if not DatetimeManager.sanity_check(fcst_time, self.data_list):
                    raise ValueError(
                        f"Sanity check failed for fcst time: {fcst_time}, "
                        f"please choose another day instead {eval_case}."
                    )

            init_time_list.add(eval_case)
        return sorted(init_time_list)

    @property
    def init_time(self) -> list[datetime]:
        """
        Since `self.init_time_list` is not always available, this function returns default init times
        used by CustomDataset from `self.data_manager` or `self.init_time_list`
        """
        return (
            self.init_time_list
            if self.init_time_list is not None
            else self.data_manager._predict_dataset._init_time_list
        )

    @abc.abstractmethod
    def _setup(self):
        """
        Prepare all necessary objects for inference when calling `__init__`.
        """
        return NotImplemented

    @abc.abstractmethod
    def infer(self):
        """
        Inference process.
        """
        return NotImplemented

    def _boundary_swapping(
        self,
        data: np.ndarray,
        dt: datetime,
        method: str,
        bdy_grid: int = 10,
        fft_k_critical: int = 17,
        fft_transition_ratio: float = 0.2,
    ) -> np.ndarray:
        """
        Swaps the boundary values of the predicted data with actual values
        from the dataset.

        Args:
            data (np.ndarray): Input data array with shape (batch, level,
                width, height, channel). Batch must be 1.
            dt (datetime): The datetime for which to get the actual values.
            method (str): 
                - "override": Replace boundary with actual values.
                - "linear": Linearly blend boundary values.
                - "exp_decay": Exponentially blend boundary values.
                - "fft_tukey": First applies a frequency-domain blending, then 
                               performs a "linear" spatial blending on the 
                               boundaries of the FFT-blended result.
                - "None": No boundary swapping.
            bdy_grid (int, optional): Number of pixels to swap for spatial 
                                      methods. Defaults to 10. Used for 
                                      "linear", "exp_decay", "override", and 
                                      the "fft_tukey".
            fft_k_critical (int, optional): The critical wavenumber (radius in pixels from the
                                            frequency spectrum center) for the FFT-based Tukey filter.
                                            This defines where the filter starts to transition.
                                            Defaults to 16.
            fft_transition_ratio (float, optional): The ratio of the transition width to `fft_k_critical`
                                                    for the FFT-based Tukey filter. E.g., 0.5 means
                                                    the transition width is 0.5 * `fft_k_critical`.
                                                    Defaults to 0.5.

        Returns:
            np.ndarray: Data array with boundary values swapped, same shape as input
                (batch, level, width, height, channel).

        Raises:
            ValueError: If batch size is not 1 or an unknown method is specified.
        """
        # --- Read debug settings from the config object ---
        plot_cfg = self.cfg.plot.get("test_infer", {})
        plot_bdy_debug = plot_cfg.get("plot_bdy_debug", True)
        plot_fft_debug = plot_cfg.get("plot_fft_debug", True)
        debug_lv_idx = plot_cfg.get("debug_lv_idx", 0)
        debug_ch_idx = plot_cfg.get("debug_ch_idx", 1)

        batch, level, width, height, channel = data.shape
        if batch != 1:
            raise ValueError(f"Only 1 eval case at a time, but got {batch}")

        tensor_type = "surface" if level == 1 else "upper"

        pd_data = np.copy(data)  # Make a copy of the input predicted data

        dataset: CustomDataset = self.data_manager._predict_dataset
        data_dict = dataset._get_variables_from_dt(dt, is_input=True)
        gt_data = data_dict["surface"] if level == 1 else data_dict["upper_air"]

        if gt_data.shape != pd_data[0].shape:
            warnings.warn(
                f"Shape mismatch between ground truth {gt_data.shape} and "
                f"prediction {pd_data[0].shape}. Boundary swapping may fail "
                f"and data will not be modified for this call."
            )
            return data  # Return original data if shapes don't match

        # Initialize variables for plotting and blending
        blended_data = np.copy(pd_data[0])  # Start with predicted data
        gt_mask = np.zeros((width, height), dtype=np.float32)
        fft_blended_initial = np.zeros_like(pd_data[0], dtype=np.float32)

        # --- Helper functions for flow-dependent mask generation ---
        def _create_inflow_dependent_mask(
            width: int,
            height: int,
            bdy_grid: int,
            U: np.ndarray,
            V: np.ndarray,
            grid_resolution_km_inv: float,
            outflow_grid_width: int = 5,
        ) -> np.ndarray:
            """
            Creates a physically-aware anisotropic boundary blending mask that
            distinguishes between inflow and outflow based on boundary winds.

            Design Principles:
            - Inflow: Mask weight is determined by an ellipse aligned with the
                      wind, where the weight is 0.5 at a one-hour wind
                      advection distance downwind.
            - Outflow: The mask defaults to a simple linear ramp with a width
                       of `outflow_grid_width`.

            Args:
                width: Grid width.
                height: Grid height.
                bdy_grid: Base width (in grid points) for the crosswind
                          component of the inflow ellipse.
                U: 2D array of the U-component of the wind.
                V: 2D array of the V-component of the wind.
                grid_resolution_km_inv: Inverse of grid resolution (grids/km).
                outflow_grid_width: Width of the linear mask for outflow.

            Returns:
                The calculated final weight mask, where 1.0 means full ground
                truth and 0.0 means full prediction.
            """
            # 1. Create a baseline linear mask for outflow regions.
            interior_mask = np.ones((height, width), dtype=bool)
            interior_mask[
                outflow_grid_width:-outflow_grid_width,
                outflow_grid_width:-outflow_grid_width,
            ] = False
            dist = distance_transform_cdt(interior_mask, metric="chessboard")
            safe_divisor = float(outflow_grid_width) if outflow_grid_width > 0 else 1.0
            baseline_mask = np.clip(dist / safe_divisor, 0.0, 1.0)

            # 2. Calculate the anisotropic mask generated by inflow regions.
            inflow_effect_mask = np.zeros((height, width), dtype=np.float32)
            rows, cols = np.mgrid[0:height, 0:width]

            boundary_indices = []
            for j in range(width):
                boundary_indices.extend([(0, j), (height - 1, j)])
            for i in range(1, height - 1):
                boundary_indices.extend([(i, 0), (i, width - 1)])

            for br, bc in boundary_indices:
                # Determine outward normal vector at the boundary point
                normal_r, normal_c = 0.0, 0.0
                if br == 0:
                    normal_r = -1.0
                elif br == height - 1:
                    normal_r = 1.0
                if bc == 0:
                    normal_c = -1.0
                elif bc == width - 1:
                    normal_c = 1.0

                # Check for inflow by comparing wind and normal vectors
                wind_r, wind_c = V[br, bc], U[br, bc]
                dot_product = (wind_r * normal_r) + (wind_c * normal_c)

                if dot_product < 0:  # Inflow condition
                    speed_ms = np.sqrt(wind_c**2 + wind_r**2)

                    # Define ellipse axes based on wind advection distance
                    dist_km_one_hour = speed_ms * 3.6  # 3600s/h / 1000m/km
                    dist_grid_one_hour = dist_km_one_hour * grid_resolution_km_inv
                    R_major = 2.0 * dist_grid_one_hour  # Downwind axis
                    R_minor = 2.0 * bdy_grid  # Crosswind axis

                    # Make ellipse circular for very low wind speeds
                    if speed_ms < 0.1:
                        R_major = R_minor

                    R_major = max(1.0, R_major)
                    R_minor = max(1.0, R_minor)

                    # Rotate grid to align with wind direction
                    angle = np.arctan2(wind_r, wind_c)
                    cos_a, sin_a = np.cos(-angle), np.sin(-angle)
                    dr, dc = rows - br, cols - bc
                    d_rot_c = dc * cos_a - dr * sin_a  # Downwind distance
                    d_rot_r = dc * sin_a + dr * cos_a  # Crosswind distance

                    # Calculate weight based on normalized distance in rotated frame
                    with np.errstate(divide="ignore", invalid="ignore"):
                        norm_dist_sq = (d_rot_c / R_major) ** 2 + (
                            d_rot_r / R_minor
                        ) ** 2
                    weight = np.maximum(0, 1 - np.sqrt(norm_dist_sq))
                    inflow_effect_mask = np.maximum(inflow_effect_mask, weight)

            # 3. Combine masks: Use inflow mask where active, otherwise use baseline.
            final_mask = np.maximum(baseline_mask, inflow_effect_mask)
            return np.clip(final_mask, 0.0, 1.0)

        # --- Helper function ---
        def _create_flow_advection_mask(
            width: int,
            height: int,
            bdy_grid: int,
            U: np.ndarray,
            V: np.ndarray,
            grid_resolution_km_inv: float,
        ) -> np.ndarray:
            """
            Creates a physically-aware anisotropic boundary blending mask based
            on the wind field at all boundary points.

            Unlike `_create_inflow_dependent_mask`, this method does not
            distinguish between inflow and outflow, applying the advection
            effect universally from all boundary points.

            Design Principles:
            - The mask weight is determined by an ellipse aligned with the
              wind, where the weight is 0.5 at a one-hour wind advection
              distance downwind.
            - The final mask at any grid point is the maximum influence from
              all boundary points.

            Args:
                width: Grid width.
                height: Grid height.
                bdy_grid: Base width (in grid points) for the crosswind
                          component of the influence ellipse.
                U: 2D array of the U-component of the wind.
                V: 2D array of the V-component of the wind.
                grid_resolution_km_inv: Inverse of grid resolution (grids/km).

            Returns:
                The calculated weight mask, where 1.0 means full ground truth
                and 0.0 means full prediction.
            """
            gt_mask = np.zeros((height, width), dtype=np.float32)
            rows, cols = np.mgrid[0:height, 0:width]

            boundary_indices = []
            for j in range(width):
                boundary_indices.extend([(0, j), (height - 1, j)])
            for i in range(1, height - 1):
                boundary_indices.extend([(i, 0), (i, width - 1)])

            # Calculate the influence of each boundary point on the grid
            for br, bc in boundary_indices:
                u, v = U[br, bc], V[br, bc]
                speed_ms = np.sqrt(u**2 + v**2)

                # Define ellipse axes based on wind advection distance
                dist_km_one_hour = speed_ms * 3.6  # 3600s/h / 1000m/km
                dist_grid_one_hour = dist_km_one_hour * grid_resolution_km_inv
                R_major = 2.0 * dist_grid_one_hour  # Downwind axis
                R_minor = 2.0 * bdy_grid  # Crosswind axis

                # Make ellipse circular for very low wind speeds
                if speed_ms < 0.1:
                    R_major = R_minor

                R_major = max(1.0, R_major)
                R_minor = max(1.0, R_minor)

                # Rotate grid to align with wind direction
                angle = np.arctan2(v, u)
                cos_a, sin_a = np.cos(-angle), np.sin(-angle)
                dr, dc = rows - br, cols - bc
                d_rot_c = dc * cos_a - dr * sin_a  # Downwind distance
                d_rot_r = dc * sin_a + dr * cos_a  # Crosswind distance

                # Calculate weight based on normalized distance in rotated frame
                with np.errstate(divide="ignore", invalid="ignore"):
                    norm_dist_sq = (d_rot_c / R_major) ** 2 + (d_rot_r / R_minor) ** 2
                weight = np.maximum(0, 1 - np.sqrt(norm_dist_sq))
                gt_mask = np.maximum(gt_mask, weight)

            return np.clip(gt_mask, 0.0, 1.0)


        # --- Helper function for FFT filter mask generation (nested for self-containment) ---
        def _create_scale_filter_masks(shape, k_critical, transition_width_ratio):
            """
            Creates radially symmetric smooth low-pass and high-pass filter masks
            using a Tukey Window concept for smooth transition in the frequency domain.
            """
            h, w = shape

            # Create a meshgrid representing pixel distances from the center of the frequency spectrum.
            k_x = np.arange(w) - (w // 2)
            k_y = np.arange(h) - (h // 2)
            K_X, K_Y = np.meshgrid(k_x, k_y)

            radius_map = np.sqrt(K_X**2 + K_Y**2)

            # Calculate the inner and outer radii for the Tukey window's transition band
            transition_width = k_critical * transition_width_ratio
            r_inner = k_critical - transition_width / 2
            r_outer = k_critical + transition_width / 2

            r_inner = max(0.0, float(r_inner))  # Ensure non-negative
            max_possible_radius = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
            r_outer = min(
                float(max_possible_radius), float(r_outer)
            )  # Cap at max possible frequency

            low_pass_mask = np.zeros(shape, dtype=np.float32)

            low_pass_mask[radius_map <= r_inner] = 1.0  # Fully pass region

            # Transition region (Tukey window application)
            transition_indices = (radius_map > r_inner) & (radius_map < r_outer)
            if (
                np.any(transition_indices) and (r_outer - r_inner) > 1e-9
            ):  # Avoid division by zero
                normalized_distance = (radius_map[transition_indices] - r_inner) / (
                    r_outer - r_inner
                )
                low_pass_mask[transition_indices] = 0.5 * (
                    1 + np.cos(np.pi * normalized_distance)
                )

            high_pass_mask = 1.0 - low_pass_mask

            return low_pass_mask, high_pass_mask

        # --- End of FFT filter helper function ---


        # --- Blending Methods ---
        if method == "override":
            gt_mask[:bdy_grid, :] = 1.0
            gt_mask[-bdy_grid:, :] = 1.0
            gt_mask[:, :bdy_grid] = 1.0
            gt_mask[:, -bdy_grid:] = 1.0

        elif method == "linear":
            interior_mask = np.ones((width, height), dtype=bool)
            interior_mask[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior = distance_transform_cdt(
                interior_mask, metric="chessboard"
            )
            gt_mask = dist_from_interior / bdy_grid
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

        elif method == "exp_decay":
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True  # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(
                interior_mask, metric="chessboard"
            )
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

        elif method == "flow_depend":
            # For multi-level data, use the mean wind across pressure levels.
            # For surface data, use the wind from the single surface level.
            if level == 1:
                u_wind = gt_data[0, ..., 1]
                v_wind = gt_data[0, ..., 2]
            else:
                u_wind = np.mean(gt_data[..., 2], axis=0)
                v_wind = np.mean(gt_data[..., 3], axis=0)

            gt_mask = _create_flow_advection_mask(
                width=width,
                height=height,
                bdy_grid=bdy_grid,
                U=u_wind,
                V=v_wind,
                grid_resolution_km_inv=0.25,  # Assuming 4km resolution
            )

        elif method == "inflow_advect":
            # For multi-level data, use the mean wind across pressure levels.
            # For surface data, use the wind from the single surface level.
            if level == 1:
                u_wind = gt_data[0, ..., 1]
                v_wind = gt_data[0, ..., 2]
            else:
                u_wind = np.mean(gt_data[..., 2], axis=0)
                v_wind = np.mean(gt_data[..., 3], axis=0)

            gt_mask = _create_inflow_dependent_mask(
                width=width,
                height=height,
                bdy_grid=bdy_grid,
                U=u_wind,
                V=v_wind,
                grid_resolution_km_inv=0.25,  # Assuming 4km resolution
                outflow_grid_width=5,
            )

        elif method == "fft_tukey":
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True  # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(
                interior_mask, metric="chessboard"
            )
            lwn_gt_mask = np.ones((width, height), dtype=np.float32)
            lwn_gt_mask = 0.9 ** (dist_from_true_boundary / 2)
            # Build FFT mask in wavenumber space
            lpf_mask, hpf_mask = _create_scale_filter_masks(
                (width, height), fft_k_critical, fft_transition_ratio
            )

            # Apply the mask in wavenumber spaces
            for lv in range(level):
                for ch in range(channel):
                    pd_slice = pd_data[0, lv, :, :, ch]
                    gt_slice = gt_data[lv, :, :, ch]

                    fft_pd_slice = fftshift(fft2(pd_slice))
                    fft_gt_slice = fftshift(fft2(gt_slice))

                    lwn_gt_slice = np.real(ifft2(ifftshift(fft_gt_slice * lpf_mask)))
                    lwn_pd_slice = np.real(ifft2(ifftshift(fft_pd_slice * lpf_mask)))
                    hwn_pd_slice = np.real(ifft2(ifftshift(fft_pd_slice * hpf_mask)))

                    # Blend low-wavenumber components from GT and high-wavenumber from PD
                    fft_blended_initial[lv, :, :, ch] = (
                        (lwn_gt_slice * lwn_gt_mask)
                        + (lwn_pd_slice * (1 - lwn_gt_mask))
                        + hwn_pd_slice
                    )
                    # z t u v w q qt
                    # t u v q st sp swdown olr
                    debug_ch_idx = 3 if level == 1 else 5
                    debug_lv_idx = 0 if level == 1 else 10
                    if plot_fft_debug and lv == debug_lv_idx and ch == debug_ch_idx:
                        logger.debug(
                            "Plotting FFT blending debug figure for dt=%s, level=%s, channel=%s.",
                            dt,
                            debug_lv_idx,
                            debug_ch_idx,
                        )
                        plot_fft_blending_debug(
                            FFTPlotData(
                                pd_slice=pd_slice,
                                gt_slice=gt_slice,
                                fft_pd_slice=fft_pd_slice,
                                fft_gt_slice=fft_gt_slice,
                                lpf_mask=lpf_mask,
                                hpf_mask=hpf_mask,
                                blended_spatial_slice=fft_blended_initial[
                                    lv, :, :, ch
                                ],
                                level_idx=debug_lv_idx,
                                channel_idx=debug_ch_idx,
                                dt=dt,
                                method=method,
                                tensor_type=tensor_type,
                            )
                        )

            # For the final result, use the FFT blended data as the new "predicted" data
            blended_data = fft_blended_initial

            # Build linear mask to stick the boundaries
            interior_mask = np.ones((width, height), dtype=bool)
            interior_mask[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior = distance_transform_cdt(
                interior_mask, metric="chessboard"
            )
            gt_mask = dist_from_interior / bdy_grid
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

        elif method == "None":
            pass  # gt_mask remains all zeros, so no change to data

        else:
            raise ValueError(
                f"Unknown Method: {method}. Supported methods are: 'override', 'linear', 'exp_decay', 'fft_tukey', 'None'."
            )

        # Apply the spatial blending using the calculated gt_mask
        if method != "None":
            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, 1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, 1, width, height, 1)
            data[0] = (blended_data * pd_mask_b) + (gt_data * gt_mask_b)
        else:
            pd_mask = np.ones_like(gt_mask)  # for plotting
            data[0] = blended_data

        if plot_bdy_debug:
            logger.info(
                "Plotting boundary blending debug figure for dt=%s, method=%s.",
                dt,
                method,
            )
            plot_bdy_blending_debug(
                BoundaryPlotData(
                    pd_data=pd_data,
                    gt_data=gt_data,
                    fft_blended_initial=fft_blended_initial
                    if "fft" in method
                    else None,
                    final_data=data,
                    pd_mask=pd_mask,
                    gt_mask=gt_mask,
                    level_idx=debug_lv_idx,
                    channel_idx=debug_ch_idx,
                    dt=dt,
                    method=method,
                    tensor_type=tensor_type,
                )
            )

        return data

    def get_figure_materials(self, case_dt: datetime, data_compose: DataCompose):
        """Get ground truth and prediction data for plotting figures.

        Args:
            case_dt (datetime): The initial datetime to get data for
            data_compose (DataCompose): Configuration specifying the variable and level to retrieve

        Returns:
            tuple[np.ndarray, np.ndarray]: data with shape (showcase_length, H, W)
        """
        input_data = self.get_infer_results_from_dt(case_dt, "input", data_compose)
        output_data = self.get_infer_results_from_dt(case_dt, "output", data_compose)

        # (showcase_length, H, W)
        output_plot_data = np.concatenate((input_data, output_data), axis=0)

        # prepare ground truth data
        data_gnrt: DataGenerator = self.data_manager.data_gnrt
        gt_data = []
        for i in trange(self.showcase_length, desc=f"Get {data_compose} ground truth"):
            curr_time = case_dt + i * self.output_itv
            gt_data.append(data_gnrt.yield_data(curr_time, data_compose))  # (H, W)
        gt_data = np.stack(gt_data, axis=0)  # (showcase_length, H, W)

        return gt_data, output_plot_data

    def get_infer_results_from_dt(
        self, dt: datetime, phase: str, data_compose: DataCompose
    ) -> np.ndarray:
        """Get inference input/output data for a specific datetime and variable.

        Args:
            dt (datetime): The datetime to get data for.
            phase (str): Either "input" or "output" to specify which data to retrieve.
                The shape of input data is (time, level, height, width, channel).
                The shape of output data is (time, seq_len, level, height, width, channel).
            data_compose (DataCompose): Configuration specifying the variable and level.

        Returns:
            np.ndarray: The requested data array. The output shape are all the same:
                (seq_len, height, width), for input phase, seq_len is 1.

        Raises:
            AssertionError: If phase is not "input" or "output"
            ValueError: If the requested variable or level is not found
        """
        assert phase in ["input", "output"], f"invalid phase: {phase}"
        time_idx = self.init_time.index(dt)
        if data_compose.level.is_surface():
            data = getattr(self, f"{phase}_surface")
            var_idx = self.surface_vars.index(data_compose.var_name)
            return (
                data[time_idx, :, :, :, var_idx]
                if phase == "input"
                else data[time_idx, :, 0, :, :, var_idx]
            )
        else:
            data = getattr(self, f"{phase}_upper")
            level_idx = self.pressure_lv.index(data_compose.level)
            var_idx = self.upper_vars.index(data_compose.var_name)
            return (
                data[time_idx, level_idx : level_idx + 1, :, :, var_idx]
                if phase == "input"
                else data[time_idx, :, level_idx, :, :, var_idx]
            )
