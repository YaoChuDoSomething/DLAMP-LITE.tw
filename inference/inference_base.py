import abc
import warnings
from datetime import datetime, timedelta

import numpy as np
from omegaconf import DictConfig
from tqdm import trange
from scipy.ndimage import distance_transform_cdt
from scipy.fft import fft2, ifft2, fftshift, ifftshift

from src.datasets import CustomDataset
from src.debug.boundary_plots import (
    plot_bdy_blending_verification,
    plot_fft_blending_debug,
)
from src.managers import DataManager, DatetimeManager
from src.utils import DataCompose, DataGenerator, DataType, Level


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
        fft_transition_ratio: float = 0.5,
    ) -> np.ndarray:
        """
        Swaps the boundary values of the predicted data with actual values
        from the dataset.

        Args:
            data (np.ndarray): Input data array with shape (batch, level,
                width, height, channel). Batch must be 1.
            dt (datetime): The datetime for which to get the actual values.
            method (str): "exp_decay", "linear", "override",
                "fft_tukey_linear_boundary", "None".
                - "override": Replace boundary with actual values.
                - "linear": Linearly blend boundary values.
                - "exp_decay": Exponentially blend boundary values.
                - "fft_tukey_linear_boundary": First applies a frequency-domain blending,
                                               then performs a "linear" spatial blending
                                               on the boundaries of the FFT-blended result.
                - "None": No boundary swapping.
            bdy_grid (int, optional): Number of pixels to swap for spatial methods. Defaults to 10.
                                      Used for "linear", "exp_decay", "override", and the linear
                                      part of "fft_tukey_linear_boundary".
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

            r_inner = max(0.0, float(r_inner)) # Ensure non-negative
            max_possible_radius = np.sqrt((w/2)**2 + (h/2)**2)
            r_outer = min(float(max_possible_radius), float(r_outer)) # Cap at max possible frequency

            low_pass_mask = np.zeros(shape, dtype=np.float32)

            low_pass_mask[radius_map <= r_inner] = 1.0 # Fully pass region

            # Transition region (Tukey window application)
            transition_indices = (radius_map > r_inner) & (radius_map < r_outer)
            if np.any(transition_indices) and (r_outer - r_inner) > 1e-9: # Avoid division by zero
                normalized_distance = (radius_map[transition_indices] - r_inner) / (r_outer - r_inner)
                low_pass_mask[transition_indices] = 0.5 * (1 + np.cos(np.pi * normalized_distance))

            high_pass_mask = 1.0 - low_pass_mask

            return low_pass_mask, high_pass_mask
        # --- End of FFT filter helper function ---


        # --- Read debug settings from the config object ---
        plot_cfg = self.cfg.plot.get('test_bdy', {})
        plot_verification = plot_cfg.get('plot_verification', True)
        plot_fft_debug = plot_cfg.get('plot_fft_debug', True)
        debug_level_idx = plot_cfg.get('debug_level_idx', 0)
        debug_channel_idx = plot_cfg.get('debug_channel_idx', 1)

        batch, level, width, height, channel = data.shape
        if batch != 1:
            raise ValueError(f"Only 1 eval case at a time, but got {batch}")

        pd_data = np.copy(data) # Make a copy of the input predicted data

        dataset: CustomDataset = self.data_manager._predict_dataset
        data_dict = dataset._get_variables_from_dt(dt, is_input=True)
        gt_data = data_dict["surface"] if level == 1 else data_dict["upper_air"]

        if gt_data.shape != pd_data[0].shape:
            warnings.warn(
                f"Shape mismatch between ground truth {gt_data.shape} and "
                f"prediction {pd_data[0].shape}. Boundary swapping may fail "
                f"and data will not be modified for this call."
            )
            return data # Return original data if shapes don't match

        # --- Spatial Blending Methods ---
        #if method in ["override", "linear", "exp_decay"]:
        gt_mask = np.zeros((width, height), dtype=np.float32)

        if method == "override":
            gt_mask[:bdy_grid, :] = 1.0
            gt_mask[-bdy_grid:, :] = 1.0
            gt_mask[:, :bdy_grid] = 1.0
            gt_mask[:, -bdy_grid:] = 1.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "linear":
            interior_mask = np.ones((width, height), dtype=bool)
            interior_mask[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = dist_from_interior / bdy_grid
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "exp_decay":
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        elif method == "fft_tukey":
            # Build mask exp_decay for scale blending
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            # Build FFT mask in wavenumber space
            fft_blended_initial = np.zeros_like(pd_data[0], dtype=np.float32)
            lpf_mask, hpf_mask = _create_scale_filter_masks(
                (width, height), fft_k_critical, fft_transition_ratio
            )

            # Apply the mask in wavenumber spaces
            pd_fft = np.zeros(pd_data.shape)
            for lv in range(level):
                for ch in range(channel):
                    pd_slice = pd_data[0, lv, :, :, ch]
                    gt_slice = gt_data[lv, :, :, ch]
                    lwn_pd_slice = np.real(ifft2(ifftshift(fftshift(fft2(pd_slice)) * lpf_mask)))
                    lwn_gt_slice = np.real(ifft2(ifftshift(fftshift(fft2(gt_slice)) * lpf_mask)))
                    hwn_pd_slice = np.real(ifft2(ifftshift(fftshift(fft2(pd_slice)) * hpf_mask)))

                    pd_fft[0, lv, :, :, ch] = (lwn_gt_slice * gt_mask) + (lwn_pd_slice * (1 - gt_mask)) + hwn_pd_slice

            # Build mask linear to stick the boundaries
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True # Consider outer boundary for distance
            dist_from_true_boundary = distance_transform_cdt(interior_mask, metric="chessboard")
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
            gt_mask = np.clip(gt_mask, 0.0, 1.0)
            gt_mask[gt_mask < 0.01] = 0.0

            pd_mask = 1.0 - gt_mask
            pd_mask_b = pd_mask.reshape(1, width, height, 1)
            gt_mask_b = gt_mask.reshape(1, width, height, 1)

            data[0] = (pd_fft[0] * pd_mask_b) + (gt_data * gt_mask_b)


        # --- FFT-based Blending Methods (Pure or Combined) ---
        elif method == "fft_tukey0":
            fft_blended_initial = np.zeros_like(pd_data[0], dtype=np.float32)

            lpf_mask, hpf_mask = _create_scale_filter_masks(
                (width, height), fft_k_critical, fft_transition_ratio
            )

            l = debug_level_idx
            c = debug_channel_idx

            for l_idx in range(level):
                for c_idx in range(channel):
                    pd_slice = pd_data[0, l_idx, :, :, c_idx]
                    gt_slice = gt_data[l_idx, :, :, c_idx]

                    fft_pd_slice = fftshift(fft2(pd_slice)) # pd_data in wavenumber domain
                    fft_gt_slice = fftshift(fft2(gt_slice)) # gt_data in wavenumber domain

                    combined_fft_slice = (fft_gt_slice * lpf_mask) + (fft_pd_slice * hpf_mask)

                    blended_spatial_slice = np.real(ifft2(ifftshift(combined_fft_slice)))
                    fft_blended_initial[l_idx, :, :, c_idx] = blended_spatial_slice

                    if plot_fft_debug and l_idx == l and c_idx == c:
                        plot_fft_blending_debug(
                            pd_slice=pd_slice, gt_slice=gt_slice,
                            fft_pd_slice=fft_pd_slice, fft_gt_slice=fft_gt_slice,
                            lpf_mask=lpf_mask, hpf_mask=hpf_mask,
                            blended_spatial_slice=blended_spatial_slice,
                            level_idx=l, channel_idx=c,
                            dt=dt, method=method,
                        )

            gt_mask_linear = np.zeros((width, height), dtype=np.float32)
            interior_mask_linear = np.ones((width, height), dtype=bool)
            interior_mask_linear[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False
            dist_from_interior_linear = distance_transform_cdt(interior_mask_linear, metric="chessboard")
            gt_mask_linear = dist_from_interior_linear / bdy_grid
            gt_mask_linear = np.clip(gt_mask_linear, 0.0, 1.0)
            gt_mask_linear[gt_mask_linear < 0.01] = 0.0

            pd_mask_linear = 1.0 - gt_mask_linear

            pd_mask_b_linear = pd_mask_linear.reshape(1, width, height, 1)
            gt_mask_b_linear = gt_mask_linear.reshape(1, width, height, 1)

            data[0] = (fft_blended_initial * pd_mask_b_linear) + (gt_data * gt_mask_b_linear)

            if plot_verification:
                plot_bdy_blending_verification(
                    pd_data=pd_data,
                    gt_data=gt_data,
                    fft_blended_initial=fft_blended_initial,
                    final_data=data,
                    pd_mask=pd_mask_linear,
                    gt_mask=gt_mask_linear,
                    level_idx=debug_level_idx,
                    channel_idx=debug_channel_idx,
                    dt=dt,
                    method=method,
                )

        elif method == "None":
            pass

        else:
            raise ValueError(f"Unknown Method: {method}. Supported methods are: 'override', 'linear', 'exp_decay', 'fft_tukey_linear_boundary', 'None'.")

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
