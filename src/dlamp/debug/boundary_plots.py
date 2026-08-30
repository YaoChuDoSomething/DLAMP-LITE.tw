import os
from datetime import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def plot_bdy_blending_verification(
    pd_data: np.ndarray,
    gt_data: np.ndarray,
    fft_blended_initial: np.ndarray,
    final_data: np.ndarray,
    pd_mask: np.ndarray,
    gt_mask: np.ndarray,
    level_idx: int,
    channel_idx: int,
    dt: datetime,
    method: str,
    save_dir: str = "output/debug_plot",
):
    """Plots the results of boundary blending for verification."""
    l, c = level_idx, channel_idx
    plt.ioff()
    plt.close("all")
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    plt.tight_layout(pad=3.0)
    vmin = min(
        pd_data[0, l, :, :, c].min(),
        gt_data[l, :, :, c].min(),
        fft_blended_initial[l, :, :, c].min(),
        final_data[0, l, :, :, c].min(),
    )
    vmax = max(
        pd_data[0, l, :, :, c].max(),
        gt_data[l, :, :, c].max(),
        fft_blended_initial[l, :, :, c].max(),
        final_data[0, l, :, :, c].max(),
    )

    im = axes[0, 0].imshow(pd_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 0].set_title(f"Original PD Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 0])

    im = axes[0, 1].imshow(gt_data[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 1].set_title(f"Original GT Data (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 1])

    im = axes[0, 2].imshow(fft_blended_initial[l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[0, 2].set_title(f"FFT Blended Initial (L{l} C{c})")
    fig.colorbar(im, ax=axes[0, 2])

    pd_mask_stats = f"Max: {pd_mask.max():.2f}, Mean: {pd_mask.mean():.2f}, Min: {pd_mask.min():.2f}"
    im = axes[1, 0].imshow(pd_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 0].set_title(f"Linear Blend PD Mask\n{pd_mask_stats}")
    fig.colorbar(im, ax=axes[1, 0])

    gt_mask_stats = f"Max: {gt_mask.max():.2f}, Mean: {gt_mask.mean():.2f}, Min: {gt_mask.min():.2f}"
    im = axes[1, 1].imshow(gt_mask, cmap="twilight_shifted", vmin=0, vmax=1)
    axes[1, 1].set_title(f"Linear Blend GT Mask\n{gt_mask_stats}")
    fig.colorbar(im, ax=axes[1, 1])

    im = axes[1, 2].imshow(final_data[0, l, :, :, c], cmap="viridis", vmin=vmin, vmax=vmax)
    axes[1, 2].set_title(f"Final Blended (FFT + Linear) (L{l} C{c})")
    fig.colorbar(im, ax=axes[1, 2])

    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"debug_{dt.strftime('%Y%m%d%H')}_{method}_L{l}_C{c}.png")
    plt.savefig(save_path)
    plt.close(fig)


def plot_fft_blending_debug(
    pd_slice: np.ndarray,
    gt_slice: np.ndarray,
    fft_pd_slice: np.ndarray,
    fft_gt_slice: np.ndarray,
    lpf_mask: np.ndarray,
    hpf_mask: np.ndarray,
    blended_spatial_slice: np.ndarray,
    level_idx: int,
    channel_idx: int,
    dt: datetime,
    method: str,
    save_dir: str = "output/debug_plot",
):
    """Plots FFT blending debug information."""
    from scipy.fft import ifft2, ifftshift

    l, c = level_idx, channel_idx
    plt.ioff()
    plt.close("all")
    fig_fft, axes_fft = plt.subplots(4, 4, figsize=(24, 24))
    fig_fft.suptitle(f"FFT Blending Debug (L{l}, C{c}, Method: {method}) @ {dt}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- Pre-calculate all components for the grid ---
    # Spatial components
    pd_low_freq_spatial = np.real(ifft2(ifftshift(fft_pd_slice * lpf_mask)))
    pd_high_freq_spatial = np.real(ifft2(ifftshift(fft_pd_slice * hpf_mask)))
    gt_low_freq_spatial = np.real(ifft2(ifftshift(fft_gt_slice * lpf_mask)))
    gt_high_freq_spatial = np.real(ifft2(ifftshift(fft_gt_slice * hpf_mask)))

    # Difference components
    diff_spatial = pd_slice - gt_slice
    diff_freq = np.abs(fft_pd_slice) - np.abs(fft_gt_slice)
    diff_low_freq = pd_low_freq_spatial - gt_low_freq_spatial
    diff_high_freq = pd_high_freq_spatial - gt_high_freq_spatial

    # --- Setup shared color normalization & wavenumber coordinates ---
    # For spatial plots
    spatial_data_list = [
        pd_slice,
        gt_slice,
        pd_low_freq_spatial,
        pd_high_freq_spatial,
        gt_low_freq_spatial,
        gt_high_freq_spatial,
        blended_spatial_slice,
    ]
    vmin_spatial = min(d.min() for d in spatial_data_list)
    vmax_spatial = max(d.max() for d in spatial_data_list)

    # For frequency plots
    vmax_spec = max(np.max(np.abs(fft_pd_slice)), np.max(np.abs(fft_gt_slice)))
    norm_spec = mcolors.LogNorm(vmin=1e-3, vmax=vmax_spec)
    freq_cmap = "plasma"  # Consistent colormap for frequency domain

    # Wavenumber coordinates
    h, w = pd_slice.shape
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
    im = axes_fft[0, 0].imshow(blended_spatial_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[0, 0].set_title("[0,0] Final Blended Spatial")
    fig_fft.colorbar(im, ax=axes_fft[0, 0])

    mid_y = lpf_mask.shape[0] // 2
    axes_fft[0, 1].plot(k_x_coords, lpf_mask[mid_y, :], label="LPF")
    axes_fft[0, 1].plot(k_x_coords, hpf_mask[mid_y, :], label="HPF")
    axes_fft[0, 1].set_title("[0,1] LPF/HPF Cross Section")
    axes_fft[0, 1].set_xlabel("Wavenumber k_x")
    axes_fft[0, 1].legend()
    axes_fft[0, 1].grid(True)

    im = axes_fft[0, 2].imshow(
        lpf_mask,
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
        hpf_mask,
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
    im = axes_fft[1, 0].imshow(pd_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 0].set_title("[1,0] PD Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 0])

    im = axes_fft[1, 1].imshow(
        np.abs(fft_pd_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[1, 1].set_title("[1,1] PD Spectrum (Wavenumber)")
    axes_fft[1, 1].set_xlabel("Wavenumber k_x")
    axes_fft[1, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[1, 1])

    im = axes_fft[1, 2].imshow(pd_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 2].set_title("[1,2] PD Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 2])

    im = axes_fft[1, 3].imshow(pd_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[1, 3].set_title("[1,3] PD High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[1, 3])

    # Row 2: Ground Truth Analysis
    im = axes_fft[2, 0].imshow(gt_slice, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 0].set_title("[2,0] GT Slice (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 0])

    im = axes_fft[2, 1].imshow(
        np.abs(fft_gt_slice),
        cmap=freq_cmap,
        norm=norm_spec,
        extent=wavenumber_extent,
        origin="lower",
    )
    axes_fft[2, 1].set_title("[2,1] GT Spectrum (Wavenumber)")
    axes_fft[2, 1].set_xlabel("Wavenumber k_x")
    axes_fft[2, 1].set_ylabel("Wavenumber k_y")
    fig_fft.colorbar(im, ax=axes_fft[2, 1])

    im = axes_fft[2, 2].imshow(gt_low_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 2].set_title("[2,2] GT Low-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 2])

    im = axes_fft[2, 3].imshow(gt_high_freq_spatial, cmap="viridis", vmin=vmin_spatial, vmax=vmax_spatial)
    axes_fft[2, 3].set_title("[2,3] GT High-Freq (Spatial)")
    fig_fft.colorbar(im, ax=axes_fft[2, 3])

    # Row 3: Difference Analysis
    im = axes_fft[3, 0].imshow(diff_spatial, cmap="coolwarm", norm=get_centered_norm(diff_spatial))
    axes_fft[3, 0].set_title("[3,0] Diff Spatial (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 0])

    im = axes_fft[3, 1].imshow(diff_freq, cmap="coolwarm", norm=get_centered_norm(diff_freq))
    axes_fft[3, 1].set_title("[3,1] Diff Spectrum (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 1])

    im = axes_fft[3, 2].imshow(diff_low_freq, cmap="coolwarm", norm=get_centered_norm(diff_low_freq))
    axes_fft[3, 2].set_title("[3,2] Diff Low-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 2])

    im = axes_fft[3, 3].imshow(diff_high_freq, cmap="coolwarm", norm=get_centered_norm(diff_high_freq))
    axes_fft[3, 3].set_title("[3,3] Diff High-Freq (PD-GT)")
    fig_fft.colorbar(im, ax=axes_fft[3, 3])

    # Save the figure
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"debug_fft_{dt.strftime('%Y%m%d%H')}_{method}_L{l}_C{c}.png")
    plt.savefig(save_path)
    plt.close(fig_fft)
