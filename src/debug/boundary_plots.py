import logging
import os
from dataclasses import dataclass
from datetime import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class BoundaryPlotData:
    """Data for plotting boundary blending debug information."""

    pd_data: np.ndarray
    gt_data: np.ndarray
    final_data: np.ndarray
    pd_mask: np.ndarray
    gt_mask: np.ndarray
    level_idx: int
    channel_idx: int
    dt: datetime
    method: str
    tensor_type: str
    fft_blended_initial: np.ndarray | None = None
    save_dir: str = "outputs/debug_plot"


@dataclass
class FFTPlotData:
    """Data for plotting FFT blending debug information."""

    pd_slice: np.ndarray
    gt_slice: np.ndarray
    fft_pd_slice: np.ndarray
    fft_gt_slice: np.ndarray
    lpf_mask: np.ndarray
    hpf_mask: np.ndarray
    blended_spatial_slice: np.ndarray
    level_idx: int
    channel_idx: int
    dt: datetime
    method: str
    tensor_type: str
    save_dir: str = "outputs/debug_plot"


def plot_bdy_blending_debug(p: BoundaryPlotData):
    """Plots the results of boundary blending for verification."""
    l, c = p.level_idx, p.channel_idx
    plt.ioff()
    plt.close("all")
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    plt.tight_layout(pad=3.0)

    data_list = [
        p.pd_data[0, l, :, :, c],
        p.gt_data[l, :, :, c],
        p.final_data[0, l, :, :, c],
    ]
    if p.fft_blended_initial is not None:
        data_list.append(p.fft_blended_initial[l, :, :, c])

    vmin = min(d.min() for d in data_list)
    vmax = max(d.max() for d in data_list)

    im = axes[0, 0].imshow(p.pd_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 0].set_title(f"Original PD Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 0])

    im = axes[0, 1].imshow(p.gt_data[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 1].set_title(f"Original GT Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 1])

    if p.fft_blended_initial is not None:
        im = axes[0, 2].imshow(
            p.fft_blended_initial[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax
        )
        axes[0, 2].set_title(f"FFT Blended Initial (L{l} C{c})")
        fig.colorbar(im, ax=axes[0, 2])
    else:
        axes[0, 2].text(
            0.5, 0.5, "N/A", ha="center", va="center", transform=axes[0, 2].transAxes
        )
        axes[0, 2].set_title("FFT Blended Initial")
        axes[0, 2].set_xticks([])
        axes[0, 2].set_yticks([])

    pd_mask_stats = (
        f"Max: {p.pd_mask.max():.2f}, Mean: {p.pd_mask.mean():.2f}, Min: {p.pd_mask.min():.2f}"
    )
    im = axes[1, 0].imshow(p.pd_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 0].set_title(f"PD Blend Mask\n{pd_mask_stats}")
    fig.colorbar(im, ax=axes[1, 0])

    gt_mask_stats = (
        f"Max: {p.gt_mask.max():.2f}, Mean: {p.gt_mask.mean():.2f}, Min: {p.gt_mask.min():.2f}"
    )
    im = axes[1, 1].imshow(p.gt_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 1].set_title(f"GT Blend Mask\n{gt_mask_stats}")
    fig.colorbar(im, ax=axes[1, 1])

    im = axes[1, 2].imshow(
        p.final_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax
    )
    axes[1, 2].set_title(f"Final Blended ({p.method}) (L{l} C{c})")
    fig.colorbar(im, ax=axes[1, 2])

    plotted_axes_count = 0
    for ax in axes.flatten():
        if ax.images or ax.lines or ax.patches or ax.texts:
            plotted_axes_count += 1
    if plotted_axes_count == axes.size:
        logger.info(
            f"All {axes.size}/{axes.size} subplots for boundary blending debug "
            "figure seem to be correctly plotted."
        )
    else:
        logger.warning(
            f"Only {plotted_axes_count}/{axes.size} subplots for boundary blending "
            "debug figure were plotted. The figure might be incomplete."
        )
    os.makedirs(p.save_dir, exist_ok=True)
    save_path = os.path.join(
        p.save_dir,
        f"debug_bdy_{p.dt.strftime('%Y%m%d%H')}_{p.method}_L{l}_C{c}_{p.tensor_type}.png",
    )
    plt.savefig(save_path)
    logger.info(f"Saved boundary blending debug figure to {save_path}")
    plt.close(fig)


def plot_fft_blending_debug(p: FFTPlotData):
    """Plots FFT blending debug information."""
    from scipy.fft import ifft2, ifftshift

    l, c = p.level_idx, p.channel_idx
    plt.ioff()
    plt.close("all")
    fig_fft, axes_fft = plt.subplots(4, 4, figsize=(24, 24))
    fig_fft.suptitle(
        f"FFT Blending Debug (L{l}, C{c}, Method: {p.method}) @ {p.dt}", fontsize=16
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- Pre-calculate all components for the grid ---
    # Spatial components
    pd_low_freq_spatial = np.real(ifft2(ifftshift(p.fft_pd_slice * p.lpf_mask)))
    pd_high_freq_spatial = np.real(ifft2(ifftshift(p.fft_pd_slice * p.hpf_mask)))
    gt_low_freq_spatial = np.real(ifft2(ifftshift(p.fft_gt_slice * p.lpf_mask)))
    gt_high_freq_spatial = np.real(ifft2(ifftshift(p.fft_gt_slice * p.hpf_mask)))

    # Difference components
    diff_spatial = p.pd_slice - p.gt_slice
    diff_freq = np.abs(p.fft_pd_slice) - np.abs(p.fft_gt_slice)
    diff_low_freq = pd_low_freq_spatial - gt_low_freq_spatial
    diff_high_freq = pd_high_freq_spatial - gt_high_freq_spatial

    # --- Setup shared color normalization & wavenumber coordinates ---
    # For spatial plots
    spatial_data_list = [
        p.pd_slice,
        p.gt_slice,
        pd_low_freq_spatial,
        pd_high_freq_spatial,
        gt_low_freq_spatial,
        gt_high_freq_spatial,
        p.blended_spatial_slice,
    ]
    vmin_spatial = min(d.min() for d in spatial_data_list)
    vmax_spatial = max(d.max() for d in spatial_data_list)

    # For frequency plots
    vmax_spec = max(np.max(np.abs(p.fft_pd_slice)), np.max(np.abs(p.fft_gt_slice)))
    norm_spec = mcolors.LogNorm(vmin=1e-3, vmax=vmax_spec)
    freq_cmap = "plasma"  # Consistent colormap for frequency domain

    # Wavenumber coordinates
    h, w = p.pd_slice.shape
    k_x_coords = np.arange(w) - (w // 2)
    k_y_coords = np.arange(h) - (h // 2)
    wavenumber_extent = [
        k_x_coords.min(),
        k_x_coords.max(),
        k_y_coords.min(),
        k_y_coords.max(),
    ]

    # For difference plots
    def get_centered_norm(data_array):
        vmax_abs = np.max(np.abs(data_array))
        return mcolors.CenteredNorm(vcenter=0, halfrange=vmax_abs)

    # --- Plotting Grid ---
    # Row 0: Masks and Final Result
    im = axes_fft[0, 0].imshow(
        p.blended_spatial_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[0, 0].set_title("[0,0] Final Blended Spatial")
    fig_fft.colorbar(im, ax=axes_fft[0, 0])

    mid_y = p.lpf_mask.shape[0] // 2
    axes_fft[0, 1].plot(k_x_coords, p.lpf_mask[mid_y, :], label="LPF")
    axes_fft[0, 1].plot(k_x_coords, p.hpf_mask[mid_y, :], label="HPF")
    axes_fft[0, 1].set_title("[0,1] LPF/HPF Cross Section")
    axes_fft[0, 1].set_xlabel("Wavenumber k_x")
    axes_fft[0, 1].legend()
    axes_fft[0, 1].grid(True)

    im = axes_fft[0, 2].imshow(
        p.lpf_mask,
        cmap=freq_cmap,
        vmin=0,
        vmax=1,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[0, 2].set_title("[0,2] LPF Mask (Wavenumber)")
    axes_fft[0, 2].set_xlabel("Wavenumber k_x")
    axes_fft[0, 2].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[0, 2])

    im = axes_fft[0, 3].imshow(
        p.hpf_mask,
        cmap=freq_cmap,
        vmin=0,
        vmax=1,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[0, 3].set_title("[0,3] HPF Mask (Wavenumber)")
    axes_fft[0, 3].set_xlabel("Wavenumber k_x")
    axes_fft[0, 3].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[0, 3])

    # Row 1: Predicted Data Analysis
    im = axes_fft[1, 0].imshow(
        p.pd_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[1, 0].set_title("[1,0] PD Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 0])

    im = axes_fft[1, 1].imshow(
        np.abs(p.fft_pd_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[1, 1].set_title("[1,1] PD Spectrum (Wavenumber)")
    axes_fft[1, 1].set_xlabel("Wavenumber k_x")
    axes_fft[1, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[1, 1])

    im = axes_fft[1, 2].imshow(
        pd_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[1, 2].set_title("[1,2] PD Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 2])

    im = axes_fft[1, 3].imshow(
        pd_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[1, 3].set_title("[1,3] PD High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 3])

    # Row 2: Ground Truth Analysis
    im = axes_fft[2, 0].imshow(
        p.gt_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[2, 0].set_title("[2,0] GT Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 0])

    im = axes_fft[2, 1].imshow(
        np.abs(p.fft_gt_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[2, 1].set_title("[2,1] GT Spectrum (Wavenumber)")
    axes_fft[2, 1].set_xlabel("Wavenumber k_x")
    axes_fft[2, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[2, 1])

    im = axes_fft[2, 2].imshow(
        gt_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[2, 2].set_title("[2,2] GT Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 2])

    im = axes_fft[2, 3].imshow(
        gt_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial
    )
    axes_fft[2, 3].set_title("[2,3] GT High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 3])

    # Row 3: Difference Analysis
    im = axes_fft[3, 0].imshow(
        diff_spatial, cmap="coolwarm", norm=get_centered_norm(diff_spatial)
    )
    axes_fft[3, 0].set_title("[3,0] Diff Spatial (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 0])

    im = axes_fft[3, 1].imshow(
        diff_freq, cmap="coolwarm", norm=get_centered_norm(diff_freq)
    )
    axes_fft[3, 1].set_title("[3,1] Diff Spectrum (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 1])

    im = axes_fft[3, 2].imshow(
        diff_low_freq, cmap="coolwarm", norm=get_centered_norm(diff_low_freq)
    )
    axes_fft[3, 2].set_title("[3,2] Diff Low-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 2])

    im = axes_fft[3, 3].imshow(
        diff_high_freq, cmap="coolwarm", norm=get_centered_norm(diff_high_freq)
    )
    axes_fft[3, 3].set_title("[3,3] Diff High-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 3])

    plotted_axes_count = 0
    for ax in axes_fft.flatten():
        if ax.images or ax.lines or ax.patches or ax.texts:
            plotted_axes_count += 1
    if plotted_axes_count == axes_fft.size:
        logger.info(
            f"All {axes_fft.size}/{axes_fft.size} subplots for FFT blending debug "
            "figure seem to be correctly plotted."
        )
    else:
        logger.warning(
            f"Only {plotted_axes_count}/{axes_fft.size} subplots for FFT blending "
            "debug figure were plotted. The figure might be incomplete."
        )
    # Save the figure
    os.makedirs(p.save_dir, exist_ok=True)
    save_path = os.path.join(
        p.save_dir,
        f"debug_fft_{p.dt.strftime('%Y%m%d_%H%M')}_{p.method}_L{l}_C{c}_{p.tensor_type}.png",
    )
    plt.savefig(save_path)
    logger.info(f"Saved FFT blending debug figure to {save_path}")
    plt.close(fig_fft)