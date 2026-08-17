"""Boundary condition extraction and sponge zone operations for RegPGW.

Provides utilities for cropping regional domains from driving global fields,
generating spatial sponge masks, and blending lateral boundary conditions.
"""


import numpy as np
import torch

from fcn_regpgw.const import (
    DEFAULT_BOUNDARY_WIDTH,
    DEFAULT_REGIONAL_BOUNDS,
)


class BoundaryExtractor:
    """Extracts regional domains and boundary condition buffers.

    Attributes:
        bounds (Tuple[int, int, int, int]): Slice bounds
            (lat_min, lat_max, lon_min, lon_max) on the global grid.
        boundary_width (int): Number of lateral grid cells for sponge boundary.
    """

    def __init__(
        self,
        bounds: tuple[int, int, int, int] = DEFAULT_REGIONAL_BOUNDS,
        boundary_width: int = DEFAULT_BOUNDARY_WIDTH,
    ) -> None:
        """Initialize BoundaryExtractor.

        Args:
            bounds (Tuple[int, int, int, int]): Global grid indices
                (lat_min, lat_max, lon_min, lon_max).
            boundary_width (int): Width of the sponge zone in grid points.
        """
        self.bounds = bounds
        self.boundary_width = boundary_width

    def crop_regional_domain(
        self, global_field: np.ndarray
    ) -> np.ndarray:
        """Crop regional subgrid from a global field.

        Args:
            global_field (np.ndarray): Global array of shape (..., H, W).

        Returns:
            np.ndarray: Regional subgrid of shape (..., H_reg, W_reg).
        """
        lat_min, lat_max, lon_min, lon_max = self.bounds
        return global_field[..., lat_min:lat_max, lon_min:lon_max].copy()

    def paste_regional_to_global(
        self,
        global_field: np.ndarray,
        regional_field: np.ndarray,
        blend_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """Paste regional field back into global domain with optional blending.

        Args:
            global_field (np.ndarray): Global array of shape (..., H, W).
            regional_field (np.ndarray): Regional array of shape
                (..., H_reg, W_reg).
            blend_mask (Optional[np.ndarray]): Spatial blending mask of shape
                (H_reg, W_reg). If None, directly replaces the subgrid.

        Returns:
            np.ndarray: Updated global array.
        """
        lat_min, lat_max, lon_min, lon_max = self.bounds
        out = global_field.copy()
        if blend_mask is None:
            out[..., lat_min:lat_max, lon_min:lon_max] = regional_field
        else:
            current_reg = out[..., lat_min:lat_max, lon_min:lon_max]
            blended = (1.0 - blend_mask) * current_reg + blend_mask * regional_field
            out[..., lat_min:lat_max, lon_min:lon_max] = blended
        return out


class SpongeLayer:
    """Computes spatial sponge boundary weights for lateral boundary blending.

    Attributes:
        height (int): Regional domain height in grid cells.
        width (int): Regional domain width in grid cells.
        boundary_width (int): Sponge zone width in grid cells.
        decay (float): Exponential decay or polynomial steepness factor.
    """

    def __init__(
        self,
        height: int,
        width: int,
        boundary_width: int = DEFAULT_BOUNDARY_WIDTH,
        decay: float = 0.5,
    ) -> None:
        """Initialize SpongeLayer.

        Args:
            height (int): Domain height.
            width (int): Domain width.
            boundary_width (int): Width of lateral boundary zone.
            decay (float): Decay factor.
        """
        self.height = height
        self.width = width
        self.boundary_width = boundary_width
        self.decay = decay
        self._mask = self._generate_sponge_mask()

    @property
    def mask(self) -> np.ndarray:
        """Get 2D sponge mask of shape (height, width).

        Returns:
            np.ndarray: Mask array where boundary is 1.0 and interior is 0.0.
        """
        return self._mask

    def _generate_sponge_mask(self) -> np.ndarray:
        """Construct 2D smooth sponge mask transitioning from 1 at edge to 0.

        Returns:
            np.ndarray: 2D float32 array with sponge weights.
        """
        mask = np.zeros((self.height, self.width), dtype=np.float32)
        bw = self.boundary_width

        if bw <= 0:
            return mask

        # Distance to boundary for each coordinate
        y_idx = np.arange(self.height)
        x_idx = np.arange(self.width)

        dist_y = np.minimum(y_idx, self.height - 1 - y_idx)
        dist_x = np.minimum(x_idx, self.width - 1 - x_idx)

        grid_dist_y, grid_dist_x = np.meshgrid(dist_y, dist_x, indexing="ij")
        min_dist = np.minimum(grid_dist_y, grid_dist_x)

        # Apply cosine relaxation profile within boundary width
        in_sponge = min_dist < bw
        sponge_weights = 0.5 * (1.0 + np.cos(np.pi * min_dist[in_sponge] / bw))
        mask[in_sponge] = sponge_weights

        return mask

    def blend_boundary(
        self,
        regional_state: np.ndarray,
        boundary_forcing: np.ndarray,
    ) -> np.ndarray:
        """Blend lateral driving boundary condition into regional state.

        Args:
            regional_state (np.ndarray): Regional state array (..., H, W).
            boundary_forcing (np.ndarray): Driving boundary array (..., H, W).

        Returns:
            np.ndarray: Blended regional state.
        """
        w = self._mask
        return (1.0 - w) * regional_state + w * boundary_forcing

    def blend_boundary_tensor(
        self,
        regional_state: torch.Tensor,
        boundary_forcing: torch.Tensor,
    ) -> torch.Tensor:
        """Blend lateral boundary in PyTorch Tensor format.

        Args:
            regional_state (torch.Tensor): Tensor of shape (B, C, H, W).
            boundary_forcing (torch.Tensor): Tensor of shape (B, C, H, W).

        Returns:
            torch.Tensor: Blended Tensor.
        """
        mask_t = torch.from_numpy(self._mask).to(
            device=regional_state.device, dtype=regional_state.dtype
        )
        return (1.0 - mask_t) * regional_state + mask_t * boundary_forcing
