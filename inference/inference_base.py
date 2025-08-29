import abc
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_cdt
from omegaconf import DictConfig
from tqdm import trange

from src.datasets import CustomDataset
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
        if self.init_time_list is not None:
            return self.init_time_list

        # TODO: This is a temporary solution. The DataManager should provide a public
        # interface to get the prediction init time list.
        return self.data_manager._predict_dataset._init_time_list

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
        self, data: np.ndarray, dt: datetime, method: str, bdy_grid: int = 8
    ) -> np.ndarray:
        """
        Swaps the boundary values of the predicted data with actual values
        from the dataset.

        Args:
            data (np.ndarray): Input data array with shape (batch, level,
                width, height, channel). Batch must be 1.
            dt (datetime): The datetime for which to get the actual values.
            method (str): "exp_decay", "linear", "override".
                "override" means replace all values on the boundary with the actual values.
                "linear" means linearly replacing the boundary values.
                "exp_decay" means
                for the
            bdy_grid (int, optional): Number of pixels to swap. Defaults to 8.

        Returns:
            np.ndarray: Data array with boundary values swapped, same shape as input
                (batch, level, width, height, channel).

        Raises:
            AssertionError: If batch size is not 1.
        """
        # --- Read debug settings from the config object ---
        # We use OmegaConf.get to safely access nested keys, providing a default value.
        # This makes the code robust even if the keys don't exist in the yaml.
        plot_cfg = self.cfg.plot.get('test_bdy', {}) # Get the test_bdy dict, or an empty one
        plot_verification = plot_cfg.get('plot_verification', False)
        debug_level_idx = plot_cfg.get('debug_level_idx', 0)
        debug_channel_idx = plot_cfg.get('debug_channel_idx', 0)

        batch, level, width, height, channel = data.shape
        if batch != 1:
            raise ValueError(f"Only 1 eval case at a time, but got {batch}")

        pd_data = np.copy(data)

        dataset: CustomDataset = self.data_manager._predict_dataset
        data_dict = dataset._get_variables_from_dt(dt, is_input=True)
        gt_data = data_dict["surface"] if level == 1 else data_dict["upper_air"]

        if gt_data.shape != pd_data[0].shape:
            warnings.warn(
                f"Shape mismatch between ground truth {gt_data.shape} and "
                f"prediction {pd_data[0].shape}. Boundary swapping may fail."
            )

        gt_mask = np.zeros((width, height), dtype=np.float32)

        if method == "override":
            gt_mask[:bdy_grid, :] = gt_mask[-bdy_grid:, :] = 1.0
            gt_mask[:, :bdy_grid] = gt_mask[:, -bdy_grid:] = 1.0

        elif method == "linear":
            # --- Logic for Linear Decay ---
            # We need a distance ramp that is 0 in the center and increases outwards.
            # 1. Define the interior "safe zone" as False (0).
            interior_mask = np.ones((width, height), dtype=bool)
            interior_mask[bdy_grid:-bdy_grid, bdy_grid:-bdy_grid] = False

            # 2. Calculate distance TO the nearest False point.
            # This creates a ramp from 0 (in the safe zone) to bdy_grid (at the outer edge).
            dist_from_interior = distance_transform_cdt(interior_mask, metric="chessboard")

            # 3. Normalize the ramp to create weights from 0 to 1.
            gt_mask = dist_from_interior / bdy_grid

        elif method == "exp_decay":
            # Define the boundary on mass points
            interior_mask = np.zeros((width, height), dtype=bool)
            interior_mask[1:-1, 1:-1] = True

            # Calculate the distance from boundary to arbitory mass points
            dist_from_true_boundary = distance_transform_cdt(
                interior_mask, metric="chessboard"
            )

            # Generate the math defined mask
            gt_mask = np.exp(-dist_from_true_boundary / bdy_grid)
        
        elif method == "None":
            gt_mask = np.zeros((width, height), dtype=np.float32)

        else:
            raise ValueError(f"Unknown Method: {method}")

        gt_mask = np.clip(gt_mask, 0.0, 1.0)
        gt_mask[gt_mask < 0.01] = 0.0

        pd_mask = 1.0 - gt_mask

        # Reshape masks for broadcasting over level and channel dimensions.
        pd_mask_b = pd_mask.reshape(1, width, height, 1)
        gt_mask_b = gt_mask.reshape(1, width, height, 1)

        # Blend data using broadcasting
        data[0] = (pd_data[0] * pd_mask_b) + (gt_data * gt_mask_b)

        if plot_verification:
            self._plot_boundary_swapping_verification(
                original_pred=pd_data[0],
                ground_truth=gt_data,
                blended_result=data[0],
                gt_mask=gt_mask,
                method=method,
                level_idx=debug_level_idx,    # Use value from cfg
                channel_idx=debug_channel_idx, # Use value from cfg
                dt=dt
            )
        return data

        """
        # Plotting for verification for the first channel
        c = 0 if level == 1 else 1
        l = 0 if level == 1 else 1
        fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
        axes = axes.flatten()

        plot_data = [
            (
                gt_data[l, :, :, c],
                f"L{l} C{c} Ground Truth",
                "seismic",
            ),
            (
                gt_mask,
                "Ground Truth Mask",
                "magma",
            ),
            (
                gt_data[l, :, :, c] * gt_mask,
                "GT Component",
                "twilight_shifted",
            ),
            (
                pd_data[0, l, :, :, c],
                f"L{l} C{c} Predicted",
                "seismic",
            ),
            (
                pd_mask,
                "Predicted Mask",
                "magma",
            ),
            (
                pd_data[0, l, :, :, c] * pd_mask,
                "Predicted Component",
                "twilight_shifted",
            ),
            (
                pd_data[0, l, :, :, c] - gt_data[l, :, :, c],
                "GT - Predicted Difference",
                "seismic",
            ),
            (
                gt_mask + pd_mask,
                "Mask Sum (should be 1)",
                "magma",
            ),
            (
                data[0, l, :, :, c],
                f"L{l} C{c} Blended Result",
                "twilight_shifted",
            ),
        ]

        for i, (img_data, title, cmap) in enumerate(plot_data):
            ax = axes[i]
            im = ax.imshow(img_data, cmap=cmap, origin="lower")
            ax.set_title(title)
            fig.colorbar(im, ax=ax)

        fig.suptitle(
            f"Boundary Swapping Verification: Level {l}, Channel {c}, Method '{method}'",
            fontsize=16,
        )
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        fig.savefig(f"DEBUG_bdy_swapping_var{c:02d}_lev{l:02d}_{method}.png")
        plt.close(fig)
        """

    def _plot_boundary_swapping_verification(
        self,
        original_pred: np.ndarray,
        ground_truth: np.ndarray,
        blended_result: np.ndarray,
        gt_mask: np.ndarray,
        method: str,
        level_idx: int,
        channel_idx: int,
        dt: datetime
    ):
        """
        Generates and saves a 3x3 grid of plots to verify the boundary swapping process.
        """
        pd_mask = 1.0 - gt_mask
        
        # Safely get the data slices for plotting
        try:
            gt_slice = ground_truth[level_idx, :, :, channel_idx]
            pred_slice = original_pred[level_idx, :, :, channel_idx]
            blended_slice = blended_result[level_idx, :, :, channel_idx]
        except IndexError:
            warnings.warn(
                f"Cannot plot verification for level_idx={level_idx}, channel_idx={channel_idx}. "
                f"Index out of bounds for shape {original_pred.shape}."
            )
            return

        fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
        axes = axes.flatten()

        plot_data = [
            (gt_mask, "GT Mask (Weight for GT)", "magma"),
            (gt_slice, f"L{level_idx} C{channel_idx} GT", "twilight_shifted"),
            (gt_slice * gt_mask, "GT Component (GT * GT_Mask)", "twilight_shifted"),

            (pd_mask, "PD Mask (Weight for PD)", "magma"),
            (pred_slice, f"L{level_idx} C{channel_idx} PD", "twilight_shifted"),
            (pred_slice * pd_mask, "PD Component (PD * PD_Mask)", "twilight_shifted"),

            (gt_mask + pd_mask, "Mask Sum (Should be 1.0)", "magma"),
            (pred_slice - gt_slice, "Difference (PD - GT)", "seismic"),
            (blended_slice, f"L{level_idx} C{channel_idx} Blended Result", "twilight_shifted"),
        ]

        for i, (img_data, title, cmap) in enumerate(plot_data):
            ax = axes[i]
            # Use a common color range for comparable plots for better visualization
            if cmap is "magma":
                vmin, vmax = (0, 1)
            elif cmap is "twilight_shifted":
                vmin = np.minimum(
                    np.min(gt_slice.ravel()), 
                    np.min(pred_slice.ravel())
                )
                vmax = np.maximum(
                    np.max(gt_slice.ravel()),
                    np.max(pred_slice.ravel())
                )
            else:
                vmin, vmax = (None, None)
            #vmin, vmax = (np.min(gt_slice), np.max(gt_slice)) if "Component" in title or "Truth" in title or "Predicted" in title or "Result" in title else (None, None)
            im = ax.imshow(img_data, cmap=cmap, origin="lower", vmin=vmin, vmax=vmax)
            ax.set_title(title)
            fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.15)
        
        fig.suptitle(
            f"Boundary Swapping Verification @ {dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"Method: '{method}', Level: {level_idx}, Channel: {channel_idx}",
            fontsize=16,
        )
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Ensure the debug directory exists
        output_dir = Path("debug_plots")
        output_dir.mkdir(exist_ok=True)
        dsname = "sfc" if np.size(original_pred, 0) == 1 else "upp"
        save_path = output_dir / f"bdy_swap_{dsname}_L{level_idx}_C{channel_idx}_{method}_{dt.strftime('%Y%m%d%H%M')}.png"        
        fig.savefig(save_path)
        plt.close(fig)

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
            ValueError: If the requested variable or level is not found, or if the
                datetime `dt` is not in the list of initial times.
        """
        assert phase in ["input", "output"], f"invalid phase: {phase}"
        try:
            time_idx = self.init_time.index(dt)
        except ValueError:
            raise ValueError(f"Datetime {dt} not found in initial time list.")

        if data_compose.level.is_surface():
            data = getattr(self, f"{phase}_surface")
            var_idx = self.surface_vars.index(data_compose.var_name)
            # Input shape: (time, level, height, width, channel)
            # Output shape: (time, seq_len, level, height, width, channel)
            return (
                data[time_idx, :, :, :, var_idx]
                if phase == "input"
                else data[time_idx, :, 0, :, :, var_idx]
            )
        else:
            data = getattr(self, f"{phase}_upper")
            level_idx = self.pressure_lv.index(data_compose.level)
            var_idx = self.upper_vars.index(data_compose.var_name)
            # Input shape: (time, level, height, width, channel)
            # Output shape: (time, seq_len, level, height, width, channel)
            return (
                data[time_idx, level_idx : level_idx + 1, :, :, var_idx]
                if phase == "input"
                else data[time_idx, :, level_idx, :, :, var_idx]
            )
