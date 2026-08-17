This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: docs/architecture/codebase-review-externals-fcn-regpgw.md, externals/fcn-regpgw/
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  architecture/
    codebase-review-externals-fcn-regpgw.md
externals/
  fcn-regpgw/
    modAFNO_test/
      modAFNO_model/
        __init__.py
        afno.py
        fft.py
        inference_helper.py
        modafno.py
        modembed.py
      inference.py
    20251119_prceip.pptx
    Hands_on_4 -FCNv2-RegPGW.pptx
```

# Files

## File: docs/architecture/codebase-review-externals-fcn-regpgw.md
```markdown
# Codebase Review — `externals/fcn-regpgw/`

**Scope:** full review of `externals/fcn-regpgw/` — external, **untracked** content
(`git status` shows `?? externals/fcn-regpgw/`; the 4 `.ipynb` notebooks are gitignored via
`*.ipynb`). Contents: `modAFNO_test/` (user driver `inference.py`, vendored NVIDIA
`modAFNO_model/*`, modified `inference_helper.py`), 4 coupling notebooks, 2 pptx.
**Method:** two axes — **Standards** (repo rules where they apply + Fowler smell baseline)
and **Spec** (no formal PRD; de-facto spec = the 4 notebooks' stated FCNv2/RegPGW/FCNV1
coupling flows). Key claims re-verified against source.

---

## Standards

### Hard

- **`safe_members` filter is inverted (security)** — `inference.py:13-24`. It `yield`s a
  member when `".." in name OR os.path.isabs(name) OR realpath(join(local_path,name)).startswith(realpath(local_path))` —
  so path-traversal (`../evil`) and absolute-path members are **extracted**, not skipped;
  only members *outside* the target dir are skipped. Correct predicate:
  `not (".." in name or isabs(name)) and realpath(...).startswith(realpath(local_path))`.
  Additionally `startswith` is a substring match (`model_weight_evil` passes) — use
  `os.path.commonpath`.
- **`@staticmethod` at module level** — `inference.py:12`; not inside a class, does nothing.
- **`torch.load` without `weights_only`** — `inference.py:40`; pickle RCE vector on torch 2.4.
- **Hardcoded absolute path** — `inference.py:82` `/wk2/yungyun/code_space/FCNV2_test/...`
  (someone else's home dir; won't exist on this box).
- **Top-level script, no `__main__` guard** — importing `inference` runs the whole pipeline.
- **`# ignore_header_test` leftover** — `inference_helper.py:1`.

### Judgement — hygiene + smells

- **Not runnable as-shipped:** `modAFNO_weight/` missing (`inference.py:10,93-97` references
  `fcinterp-modafno-2x2.mdlus`, `model.pt`, `global_means/stds.npy`, `land_sea_mask.nc`,
  `orography.nc` — none present). 73 MB + 16 MB pptx untracked in the tree.
- **Duplicated Code:** 720/1440 lat-lon meshgrid rebuilt in `inference_helper.py:54-57` and
  `inference.py:74-77`; the ~41-line plotting cell is verbatim across all 4 notebooks
  (oneway/2way/v1/v2 differ only in weight download, predict command, IC time —
  oneway `2025110900` vs others `2025072400`); `modafno.py` `ModAFNO2DLayer`/`Block`
  near-verbatim copies of `afno.py` (and a real divergence: `total_modes = H//2+1` in
  `afno.py:171` vs `min(H,W)//2+1` in `modafno.py:218`).
- **Repeated Switches:** `scale_shift_mode` if/elif in both `afno.py`/`modafno.py`; `method`
  string switched twice in `ModEmbedNet` (`modembed.py`).
- **Primitive Obsession:** `embed_model={...}` dict config in `inference.py:49-51`.
- **Dead code:** `compute_sza` (`inference_helper.py:80`), `irradiance`/`toa_*` unused;
  `files`/`os.listdir` at `inference.py:83-84` never used; debug `print(t)` at
  `inference_helper.py:90`; `timezone` imported unused at `inference.py:4`.
- **Mysterious Name:** `dtype` module-global in `inference_helper.py`.
- **Stale artifacts:** `__pycache__/cpython-310.pyc` present (repo is Python 3.11).
- **Notebook reproducibility:** notebooks pull `/content/couple_model` (scripts + weights)
  from Colab/gdown — not reproducible from this repo; the 2-way notebook never executed
  (`execution_count` all `None`).

---

## Spec (de-facto = the 4 notebooks)

The notebooks implement FCNv2 autoregressive forecasting + RegPGW one-way / two-way coupling
+ FCNV1 precip coupling (cells call `inference_FCNV2.py`, `inference_PGW_one_way_test.py`,
`inference_PGW_two_way_test.py`, `inference_precip_v1/v2.py`, and flip lat with
`np.flip(IC_data, axis=1)`).

### (a) Missing / partial vs notebooks

- `modAFNO_test/inference.py` implements **ModAFNO "fcinterp" temporal interpolation** — a
  model referenced in **zero** of the four notebooks (keyword scan: no
  `modAFNO`/`fcinterp`). It is neither FCNV2 autoregressive, nor PGW one-way, nor two-way
  (which re-injects PGW→FCNV2 each step), nor precip v1/v2. No regional/PGW model, no
  boundary re-injection, no lat flip.
- Data assets absent: entire `modAFNO_weight/` dir missing; hardcoded input
  `/wk2/yungyun/.../output_IFS_2025072400` unreachable.

### (b) Not asked for (scope creep)

- Entire ModAFNO driver is extraneous to the notebook flows: tar-extraction + `safe_members`
  wrapper, 3-channel cos-zenith + static channel stack, hourly `intro_i`/`t_norm`
  interpolation grid (6 outputs per 6 h pair).

### (c) Implemented but wrong

1. **`inference.py:74-78`** — `sincos_latlon = np.sin/cos(grid)` on **degrees**, no
   `deg2rad`; static features are corrupted on every forward pass. The same file's helper
   `cos_zenith_angle` does it right (`inference_helper.py:130-131` uses `np.deg2rad`), and
   `cos_zenith` (`inference_helper.py:53`) correctly hands degrees to it — the inline
   `sincos_latlon` path does not.
2. **`inference.py:105/110` vs `:131`** — reads unpadded `output_weather_0h.npy`, writes
   3-digit-padded `output_weather_000h`; self-inconsistent. Loop at `:103` iterates
   `range(len(files))` over arbitrary folder contents and reads `(len)*6h` at the last `i`
   (off-by-one / name-drift risk).
3. **`inference.py:107-108,112-113`** — RH→q converted pre-standardization, but the
   de-standardized output is saved as **q in RH-named channels** (notebook cell 8 ordering
   `r50..r1000`); no inverse q→RH. T/RH index hardcodes (`47:60`/`60:73`) assume that
   ordering.
4. **`inference.py:116-132`** — `intro_i=0` rewrites anchor time t0 already present as input;
   `model.to(device)` + `model.eval()` inside the per-intro loop; `out.detach().numpy()`
   without `.cpu()` breaks on non-CPU devices.
5. Channel math itself reconciles (73+73+3+6=155; de-std `out*scale+center` matches the std
   direction); `rh_to_q` formula/units correct.

---

## Improvement plan (ranked)

1. **Fix `safe_members` inversion** (`inference.py:13-24`) and add `weights_only=True` to
   `torch.load` — security.
2. **`deg2rad` before the sincos static features** (`inference.py:78`) — corrupts every
   forward pass otherwise.
3. **Decide what this directory is for**: implement the notebook flow (FCNV2 + PGW one/two-way
   coupling, incl. lat flip + boundary re-injection) or keep the ModAFNO interpolation as a
   separate experiment — right now `inference.py` matches neither the notebooks nor any spec.
4. **Parametrize paths/device/IC** via CLI args or config; drop `/wk2/yungyun`; unify
   read/write filenames and drive the loop from an actual lead-time file list.
5. **Make it runnable/reproducible**: commit `modAFNO_weight/` (or a fetch script), add a
   README, add a `__main__` guard, move `.to(device)`/`.eval()` out of the loop, add `.cpu()`
   before `.numpy()`.
6. **Dedupe notebooks** (shared plotting cell; unify IC time) and either vendor or clearly
   fork the NVIDIA model files (the `total_modes` divergence in `afno.py` vs `modafno.py`
   needs a decision).
7. **Track it**: the directory is entirely untracked and notebooks gitignored — nothing is
   version-controlled.

**One-line summary:** Standards — 5 hard + ~10 judgement findings, worst = inverted
`safe_members` tar filter (security) + un-runnable/un-tracked dir; Spec — ModAFNO driver
matches none of the 4 notebook flows (missing + scope-creep), worst = degree-units `sincos`
corrupting static features + read/write filename mismatch.
```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/__init__.py
```python

```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/afno.py
```python
# SPDX-FileCopyrightText: Copyright (c) 2023 - 2025 NVIDIA CORPORATION & AFFILIATES.
# SPDX-FileCopyrightText: All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import partial
from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F

# import prceip_model.fft as fft
# from prceip_model.fft import rfft2, real, imag, view_as_complex, irfft2
from .fft import rfft2, real, imag, view_as_complex, irfft2

Tensor = torch.Tensor

class AFNOMlp(nn.Module):
    """Fully-connected Multi-layer perception used inside AFNO

    Parameters
    ----------
    in_features : int
        Input feature size
    latent_features : int
        Latent feature size
    out_features : int
        Output feature size
    activation_fn :  nn.Module, optional
        Activation function, by default nn.GELU
    drop : float, optional
        Drop out rate, by default 0.0
    """

    def __init__(
        self,
        in_features: int,
        latent_features: int,
        out_features: int,
        activation_fn: nn.Module = nn.GELU(),
        drop: float = 0.0,
    ):
        super().__init__()
        self.fc1 = nn.Linear(in_features, latent_features)
        self.act = activation_fn
        self.fc2 = nn.Linear(latent_features, out_features)
        self.drop = nn.Dropout(drop)

    def forward(self, x: Tensor) -> Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x


class AFNO2DLayer(nn.Module):
    """AFNO spectral convolution layer

    Parameters
    ----------
    hidden_size : int
        Feature dimensionality
    num_blocks : int, optional
        Number of blocks used in the block diagonal weight matrix, by default 8
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1
    hidden_size_factor : int, optional
        Factor to increase spectral features by after weight multiplication, by default 1
    """

    def __init__(
        self,
        hidden_size: int,
        num_blocks: int = 8,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1,
        hidden_size_factor: int = 1,
    ):
        super().__init__()
        if not (hidden_size % num_blocks == 0):
            raise ValueError(
                f"hidden_size {hidden_size} should be divisible by num_blocks {num_blocks}"
            )

        self.hidden_size = hidden_size
        self.sparsity_threshold = sparsity_threshold
        self.num_blocks = num_blocks
        self.block_size = self.hidden_size // self.num_blocks
        self.hard_thresholding_fraction = hard_thresholding_fraction
        self.hidden_size_factor = hidden_size_factor
        self.scale = 0.02

        self.w1 = nn.Parameter(
            self.scale
            * torch.randn(
                2,
                self.num_blocks,
                self.block_size,
                self.block_size * self.hidden_size_factor,
            )
        )
        self.b1 = nn.Parameter(
            self.scale
            * torch.randn(2, self.num_blocks, self.block_size * self.hidden_size_factor)
        )
        self.w2 = nn.Parameter(
            self.scale
            * torch.randn(
                2,
                self.num_blocks,
                self.block_size * self.hidden_size_factor,
                self.block_size,
            )
        )
        self.b2 = nn.Parameter(
            self.scale * torch.randn(2, self.num_blocks, self.block_size)
        )

    def forward(self, x: Tensor) -> Tensor:
        bias = x

        dtype = x.dtype
        x = x.float()
        B, H, W, C = x.shape
        # Using ONNX friendly FFT functions
        # x = fft.rfft2(x, dim=(1, 2), norm="ortho")
        x = rfft2(x, dim=(1, 2), norm="ortho")
        x_real, x_imag = real(x), imag(x)
        # x_real, x_imag = fft.real(x), fft.imag(x)
        x_real = x_real.reshape(B, H, W // 2 + 1, self.num_blocks, self.block_size)
        x_imag = x_imag.reshape(B, H, W // 2 + 1, self.num_blocks, self.block_size)

        o1_real = torch.zeros(
            [
                B,
                H,
                W // 2 + 1,
                self.num_blocks,
                self.block_size * self.hidden_size_factor,
            ],
            device=x.device,
        )
        o1_imag = torch.zeros(
            [
                B,
                H,
                W // 2 + 1,
                self.num_blocks,
                self.block_size * self.hidden_size_factor,
            ],
            device=x.device,
        )
        o2 = torch.zeros(x_real.shape + (2,), device=x.device)

        total_modes = H // 2 + 1
        kept_modes = int(total_modes * self.hard_thresholding_fraction)

        o1_real[:, total_modes - kept_modes : total_modes + kept_modes, :kept_modes] = (
            F.relu(
                torch.einsum(
                    "nyxbi,bio->nyxbo",
                    x_real[
                        :,
                        total_modes - kept_modes : total_modes + kept_modes,
                        :kept_modes,
                    ],
                    self.w1[0],
                )
                - torch.einsum(
                    "nyxbi,bio->nyxbo",
                    x_imag[
                        :,
                        total_modes - kept_modes : total_modes + kept_modes,
                        :kept_modes,
                    ],
                    self.w1[1],
                )
                + self.b1[0]
            )
        )

        o1_imag[:, total_modes - kept_modes : total_modes + kept_modes, :kept_modes] = (
            F.relu(
                torch.einsum(
                    "nyxbi,bio->nyxbo",
                    x_imag[
                        :,
                        total_modes - kept_modes : total_modes + kept_modes,
                        :kept_modes,
                    ],
                    self.w1[0],
                )
                + torch.einsum(
                    "nyxbi,bio->nyxbo",
                    x_real[
                        :,
                        total_modes - kept_modes : total_modes + kept_modes,
                        :kept_modes,
                    ],
                    self.w1[1],
                )
                + self.b1[1]
            )
        )

        o2[
            :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes, ..., 0
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[0],
            )
            - torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[1],
            )
            + self.b2[0]
        )

        o2[
            :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes, ..., 1
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[0],
            )
            + torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[1],
            )
            + self.b2[1]
        )

        x = F.softshrink(o2, lambd=self.sparsity_threshold)
        # x = fft.view_as_complex(x)
        x = view_as_complex(x)
        # TODO(akamenev): replace the following branching with
        # a one-liner, something like x.reshape(..., -1).squeeze(-1),
        # but this currently fails during ONNX export.
        if torch.onnx.is_in_onnx_export():
            x = x.reshape(B, H, W // 2 + 1, C, 2)
        else:
            x = x.reshape(B, H, W // 2 + 1, C)
        # Using ONNX friendly FFT functions
        # x = fft.irfft2(x, s=(H, W), dim=(1, 2), norm="ortho")
        x = irfft2(x, s=(H, W), dim=(1, 2), norm="ortho")
        x = x.type(dtype)

        return x + bias


class Block(nn.Module):
    """AFNO block, spectral convolution and MLP

    Parameters
    ----------
    embed_dim : int
        Embedded feature dimensionality
    num_blocks : int, optional
        Number of blocks used in the block diagonal weight matrix, by default 8
    mlp_ratio : float, optional
        Ratio of MLP latent variable size to input feature size, by default 4.0
    drop : float, optional
        Drop out rate in MLP, by default 0.0
    activation_fn: nn.Module, optional
        Activation function used in MLP, by default nn.GELU
    norm_layer : nn.Module, optional
        Normalization function, by default nn.LayerNorm
    double_skip : bool, optional
        Residual, by default True
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1
    """

    def __init__(
        self,
        embed_dim: int,
        num_blocks: int = 8,
        mlp_ratio: float = 4.0,
        drop: float = 0.0,
        activation_fn: nn.Module = nn.GELU(),
        norm_layer: nn.Module = nn.LayerNorm,
        double_skip: bool = True,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ):
        super().__init__()
        self.norm1 = norm_layer(embed_dim)
        self.filter = AFNO2DLayer(
            embed_dim, num_blocks, sparsity_threshold, hard_thresholding_fraction
        )
        # self.drop_path = nn.Identity()
        self.norm2 = norm_layer(embed_dim)
        mlp_latent_dim = int(embed_dim * mlp_ratio)
        self.mlp = AFNOMlp(
            in_features=embed_dim,
            latent_features=mlp_latent_dim,
            out_features=embed_dim,
            activation_fn=activation_fn,
            drop=drop,
        )
        self.double_skip = double_skip

    def forward(self, x: Tensor) -> Tensor:
        residual = x
        x = self.norm1(x)
        x = self.filter(x)

        if self.double_skip:
            x = x + residual
            residual = x

        x = self.norm2(x)
        x = self.mlp(x)
        x = x + residual
        return x


class PatchEmbed(nn.Module):
    """Patch embedding layer

    Converts 2D patch into a 1D vector for input to AFNO

    Parameters
    ----------
    inp_shape : List[int]
        Input image dimensions [height, width]
    in_channels : int
        Number of input channels
    patch_size : List[int], optional
        Size of image patches, by default [16, 16]
    embed_dim : int, optional
        Embedded channel size, by default 256
    """

    def __init__(
        self,
        inp_shape: List[int],
        in_channels: int,
        patch_size: List[int] = [16, 16],
        embed_dim: int = 256,
    ):
        super().__init__()
        if len(inp_shape) != 2:
            raise ValueError("inp_shape should be a list of length 2")
        if len(patch_size) != 2:
            raise ValueError("patch_size should be a list of length 2")

        num_patches = (inp_shape[1] // patch_size[1]) * (inp_shape[0] // patch_size[0])
        self.inp_shape = inp_shape
        self.patch_size = patch_size
        self.num_patches = num_patches
        self.proj = nn.Conv2d(
            in_channels, embed_dim, kernel_size=patch_size, stride=patch_size
        )

    def forward(self, x: Tensor) -> Tensor:
        B, C, H, W = x.shape
        if not (H == self.inp_shape[0] and W == self.inp_shape[1]):
            raise ValueError(
                f"Input image size ({H}*{W}) doesn't match model ({self.inp_shape[0]}*{self.inp_shape[1]})."
            )
        x = self.proj(x).flatten(2).transpose(1, 2)
        return x


class AFNO(nn.Module):
    """Adaptive Fourier neural operator (AFNO) model.

    Note
    ----
    AFNO is a model that is designed for 2D images only.

    Parameters
    ----------
    inp_shape : List[int]
        Input image dimensions [height, width]
    in_channels : int
        Number of input channels
    out_channels: int
        Number of output channels
    patch_size : List[int], optional
        Size of image patches, by default [16, 16]
    embed_dim : int, optional
        Embedded channel size, by default 256
    depth : int, optional
        Number of AFNO layers, by default 4
    mlp_ratio : float, optional
        Ratio of layer MLP latent variable size to input feature size, by default 4.0
    drop_rate : float, optional
        Drop out rate in layer MLPs, by default 0.0
    num_blocks : int, optional
        Number of blocks in the block-diag frequency weight matrices, by default 16
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1

    Example
    -------
    >>> model = physicsnemo.models.afno.AFNO(
    ...     inp_shape=[32, 32],
    ...     in_channels=2,
    ...     out_channels=1,
    ...     patch_size=(8, 8),
    ...     embed_dim=16,
    ...     depth=2,
    ...     num_blocks=2,
    ... )
    >>> input = torch.randn(32, 2, 32, 32) #(N, C, H, W)
    >>> output = model(input)
    >>> output.size()
    torch.Size([32, 1, 32, 32])

    Note
    ----
    Reference: Guibas, John, et al. "Adaptive fourier neural operators:
    Efficient token mixers for transformers." arXiv preprint arXiv:2111.13587 (2021).
    """

    def __init__(
        self,
        inp_shape: List[int],
        in_channels: int,
        out_channels: int,
        patch_size: List[int] = [16, 16],
        embed_dim: int = 256,
        depth: int = 4,
        mlp_ratio: float = 4.0,
        drop_rate: float = 0.0,
        num_blocks: int = 16,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ) -> None:
        # super().__init__(meta=MetaData())
        super().__init__()
        if len(inp_shape) != 2:
            raise ValueError("inp_shape should be a list of length 2")
        if len(patch_size) != 2:
            raise ValueError("patch_size should be a list of length 2")

        if not (
            inp_shape[0] % patch_size[0] == 0 and inp_shape[1] % patch_size[1] == 0
        ):
            raise ValueError(
                f"input shape {inp_shape} should be divisible by patch_size {patch_size}"
            )

        self.in_chans = in_channels
        self.out_chans = out_channels
        self.inp_shape = inp_shape
        self.patch_size = patch_size
        self.num_features = self.embed_dim = embed_dim
        self.num_blocks = num_blocks
        norm_layer = partial(nn.LayerNorm, eps=1e-6)

        self.patch_embed = PatchEmbed(
            inp_shape=inp_shape,
            in_channels=self.in_chans,
            patch_size=self.patch_size,
            embed_dim=embed_dim,
        )
        num_patches = self.patch_embed.num_patches

        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))
        self.pos_drop = nn.Dropout(p=drop_rate)

        self.h = inp_shape[0] // self.patch_size[0]
        self.w = inp_shape[1] // self.patch_size[1]

        self.blocks = nn.ModuleList(
            [
                Block(
                    embed_dim=embed_dim,
                    num_blocks=self.num_blocks,
                    mlp_ratio=mlp_ratio,
                    drop=drop_rate,
                    norm_layer=norm_layer,
                    sparsity_threshold=sparsity_threshold,
                    hard_thresholding_fraction=hard_thresholding_fraction,
                )
                for i in range(depth)
            ]
        )

        self.head = nn.Linear(
            embed_dim,
            self.out_chans * self.patch_size[0] * self.patch_size[1],
            bias=False,
        )

        torch.nn.init.trunc_normal_(self.pos_embed, std=0.02)
        self.apply(self._init_weights)

    def _init_weights(self, m):
        """Init model weights"""
        if isinstance(m, nn.Linear):
            torch.nn.init.trunc_normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    # What is this for
    # @torch.jit.ignore
    # def no_weight_decay(self):
    #     return {"pos_embed", "cls_token"}

    def forward_features(self, x: Tensor) -> Tensor:
        """Forward pass of core AFNO"""
        B = x.shape[0]
        x = self.patch_embed(x)
        x = x + self.pos_embed
        x = self.pos_drop(x)

        x = x.reshape(B, self.h, self.w, self.embed_dim)
        for blk in self.blocks:
            x = blk(x)

        return x

    def forward(self, x: Tensor) -> Tensor:
        x = self.forward_features(x)
        x = self.head(x)

        # Correct tensor shape back into [B, C, H, W]
        # [b h w (p1 p2 c_out)]
        out = x.view(list(x.shape[:-1]) + [self.patch_size[0], self.patch_size[1], -1])
        # [b h w p1 p2 c_out]
        out = torch.permute(out, (0, 5, 1, 3, 2, 4))
        # [b c_out, h, p1, w, p2]
        out = out.reshape(list(out.shape[:2]) + [self.inp_shape[0], self.inp_shape[1]])
        # [b c_out, (h*p1), (w*p2)]
        return out
```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/fft.py
```python
# SPDX-FileCopyrightText: Copyright (c) 2023 - 2025 NVIDIA CORPORATION & AFFILIATES.
# SPDX-FileCopyrightText: All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
from typing import List, Optional, Tuple

import torch
import torch.fft
import torch.onnx
from torch import Tensor
from torch.autograd import Function

# Note 1: for DFT operators, the less verbose way of registering an operator is via
# `register_custom_op_symbolic`. However, it does not currently work due to
# torch.fft.rfft* functions returning Complex type which is not yet supported in ONNX.

# Note 2:
# - current ONNX Contrib implementation does not support configurable normalization, so
#   "normalized" must be 0, the normalization is done outside of Contrib ops.
#   See also comments in `_scale_output_backward` function for more details.
# - "onesided" is not configurable either - must be set to 1.
# - Contrib implementation requires DFT dimensions to be the last ones,
#   otherwise axes permutation is required.
# See:
# https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/contrib_ops/cuda/math/fft_ops.h#L19


def rfft(
    input: Tensor,
    n: Optional[int] = None,
    dim: int = -1,
    norm: Optional[str] = None,
) -> Tensor:
    """ONNX compatable method to compute the 1d Fourier transform of real-valued input.

    Parameters
    ----------
    input : Tensor
        Real input tensor
    n : Optional[int], optional
        Signal strength, by default None
    dim : int, optional
        Dimension along which to take the real FFT, by default -1
    norm : Optional[str], optional
        Normalization mode with options "forward", "backward and "ortho". When set to None,
        normalization will default to backward (no normalization), by default None

    Note
    ----
    The function is equivalent to `torch.fft.rfft` when not running in ONNX export mode
    """
    if not torch.onnx.is_in_onnx_export():
        return torch.fft.rfft(input, n=n, dim=dim, norm=norm)

    if not isinstance(dim, int):
        raise TypeError()
    return _rfft_onnx(input, (n,), (dim,), norm)


def rfft2(
    input: Tensor,
    s: Optional[Tuple[int]] = None,
    dim: Tuple[int] = (-2, -1),
    norm: Optional[str] = None,
) -> Tensor:
    """ONNX compatable method to compute the 2d Fourier transform of real-valued input.

    Parameters
    ----------
    input : Tensor
        Real input tensor
    s : Optional[Tuple[int]], optional
        Signal size in the transformed dimensions, by default None
    dim : Tuple[int], optional
        Dimensions along which to take the real 2D FFT, by default (-2, -1)
    norm : Optional[str], optional
        Normalization mode with options "forward", "backward" and "ortho". When set to None,
        normalization will default to backward (normalize by 1/n), by default None

    Note
    ----
    The function is equivalent to `torch.fft.rfft2` when not running in ONNX export mode
    """
    if not torch.onnx.is_in_onnx_export():
        return torch.fft.rfft2(input, s=s, dim=dim, norm=norm)

    if not (isinstance(dim, tuple) and len(dim) == 2):
        raise ValueError()
    return _rfft_onnx(input, s, dim, norm)


def irfft(
    input: Tensor,
    n: Optional[int] = None,
    dim: int = -1,
    norm: Optional[str] = None,
) -> Tensor:
    """ONNX compatable method to compute the inverse of `rfft`.

    Parameters
    ----------
    input : Tensor
        Real input tensor
    n : Optional[int], optional
        Signal strength, by default None
    dim : int, optional
        Dimension along which to take the real IFFT, by default -1
    norm : Optional[str], optional
        Normalization mode with options "forward", "backward" and "ortho". When set to None,
        normalization will default to backward (no normalization), by default None

    Note
    ----
    The function is equivalent to `torch.fft.irfft` when not running in ONNX export mode
    """
    if not torch.onnx.is_in_onnx_export():
        return torch.fft.irfft(input, n=n, dim=dim, norm=norm)

    if not isinstance(dim, int):
        raise TypeError()
    return _irfft_onnx(input, (n,), (dim,), norm)


def irfft2(
    input: Tensor,
    s: Optional[Tuple[int]] = None,
    dim: Tuple[int] = (-2, -1),
    norm: Optional[str] = None,
) -> Tensor:
    """ONNX compatable method to compute the inverse of `rfft2`.

    Parameters
    ----------
    input : Tensor
        Real input tensor
    s : Optional[Tuple[int]], optional
        Signal size in the transformed dimensions, by default None
    dim : Tuple[int], optional
        Dimensions along which to take the real 2D IFFT, by default (-2, -1)
    norm : Optional[str], optional
        Normalization mode with options "forward", "backward" and "ortho". When set to None,
        normalization will default to backward (normalize by 1/n), by default None

    Note
    ----
    The function is equivalent to `torch.fft.irfft2` when not running in ONNX export mode
    """
    if not torch.onnx.is_in_onnx_export():
        return torch.fft.irfft2(input, s=s, dim=dim, norm=norm)

    if not (isinstance(dim, tuple) and len(dim) == 2):
        raise ValueError()
    return _irfft_onnx(input, s, dim, norm)


def view_as_complex(input: Tensor) -> Tensor:
    """ONNX compatable method to view input as complex tensor

    Parameters
    ----------
    input : Tensor
        The input Tensor

    Note
    ----
    The function is equivalent to `torch.view_as_complex` when not running in ONNX export mode

    Raises
    ------
    AssertionError
        If input tensor shape is not [...,2] during ONNX runtime where the last dimension
        denotes the real / imaginary tensors
    """
    if not torch.onnx.is_in_onnx_export():
        return torch.view_as_complex(input)

    # Just return the input unchanged - during ONNX export
    # there will be no complex type.
    if input.size(-1) != 2:
        raise ValueError
    return input


def real(input: Tensor) -> Tensor:
    """ONNX compatable method to view input as real tensor

    Parameters
    ----------
    input : Tensor
        The input Tensor

    Note
    ----
    The function is equivalent to `input.real` when not running in ONNX export mode

    Raises
    ------
    AssertionError
        If input tensor shape is not [...,2] during ONNX runtime where the last dimension
        denotes the real / imaginary tensors
    """
    if not torch.onnx.is_in_onnx_export():
        return input.real

    # There is no complex type during ONNX export, so assuming
    # complex numbers are represented as if after `view_as_real`.
    if input.size(-1) != 2:
        raise ValueError()
    return input[..., 0]


def imag(input: Tensor) -> Tensor:
    """ONNX compatable method to view input as imaginary tensor

    Parameters
    ----------
    input : Tensor
        The input Tensor

    Note
    ----
    The function is equivalent to `input.imag` when not running in ONNX export mode

    Raises
    ------
    AssertionError
        If input tensor shape is not [...,2] during ONNX runtime  where the last dimension
        denotes the real / imaginary tensors
    """
    if not torch.onnx.is_in_onnx_export():
        return input.imag

    # There is no complex type during ONNX export, so assuming
    # complex numbers are represented as if after `view_as_real`.
    if input.size(-1) != 2:
        raise ValueError(input.size(-1))
    return input[..., 1]


def _rfft_onnx(
    input: Tensor, s: Optional[Tuple[Optional[int]]], dim: Tuple[int], norm: str
) -> Tensor:
    if s is not None:
        _check_padding_rfft(s, dim, input.size())

    ndim = len(dim)
    if ndim not in [1, 2]:
        raise ValueError(ndim)

    perm = not _is_last_dims(dim, input.ndim)

    if perm:
        perm_in, perm_out = _create_axes_perm(input.ndim, dim)
        # Add a dimension to account for complex output.
        perm_out.append(len(perm_out))
        # Transpose -> RFFT -> Transpose (inverse).
        input = input.permute(perm_in)

    rfft_func = OnnxRfft if ndim == 1 else OnnxRfft2
    output = rfft_func.apply(input)

    output = _scale_output_forward(output, norm, input.size(), ndim)

    if perm:
        output = output.permute(perm_out)

    return output


def _irfft_onnx(
    input: Tensor, s: Optional[Tuple[Optional[int]]], dim: Tuple[int], norm: str
) -> Tensor:
    if s is not None:
        _check_padding_irfft(s, dim, input.size())

    ndim = len(dim)
    if ndim not in [1, 2]:
        raise ValueError(ndim)

    # Whether to permute axes when DFT axis is not the last.
    perm = not _is_last_dims(dim, input.ndim)

    if perm:
        # Do not include last dimension (input is complex).
        perm_in, perm_out = _create_axes_perm(input.ndim - 1, dim)
        # Add a dimension to account for complex input.
        perm_in.append(len(perm_in))
        # Transpose -> IRFFT -> Transpose (inverse).
        input = input.permute(perm_in)

    irfft_func = OnnxIrfft if ndim == 1 else OnnxIrfft2
    output = irfft_func.apply(input)

    output = _scale_output_backward(output, norm, input.size(), ndim)

    if perm:
        output = output.permute(perm_out)

    return output


def _contrib_rfft(g: torch.Graph, input: torch.Value, ndim: int) -> torch.Value:
    if ndim not in [1, 2]:
        raise ValueError(ndim)

    # See https://github.com/microsoft/onnxruntime/blob/main/docs/ContribOperators.md#com.microsoft.Rfft
    output = g.op(
        "com.microsoft::Rfft",
        input,
        normalized_i=0,
        onesided_i=1,
        signal_ndim_i=ndim,
    )

    return output


def _contrib_irfft(g: torch.Graph, input: torch.Value, ndim: int) -> torch.Value:
    if ndim not in [1, 2]:
        raise ValueError(ndim)

    # See https://github.com/microsoft/onnxruntime/blob/main/docs/ContribOperators.md#com.microsoft.Irfft
    output = g.op(
        "com.microsoft::Irfft",
        input,
        normalized_i=0,
        onesided_i=1,
        signal_ndim_i=ndim,
    )

    return output


def _is_last_dims(dim: Tuple[int], inp_ndim: int) -> bool:
    ndim = len(dim)
    for i, idim in enumerate(dim):
        # This takes care of both positive and negative axis indices.
        if idim % inp_ndim != inp_ndim - ndim + i:
            return False
    return True


def _check_padding_rfft(
    sizes: Tuple[Optional[int]], dim: Tuple[int], inp_sizes: Tuple[int]
) -> None:
    if len(sizes) != len(dim):
        raise ValueError(f"{sizes}, {dim}")
    for i, s in enumerate(sizes):
        if s is None or s < 0:
            continue
        # Current Contrib RFFT does not support pad/trim yet.
        if s != inp_sizes[dim[i]]:
            raise RuntimeError(
                f"Padding/trimming is not yet supported, "
                f"got sizes {sizes}, DFT dims {dim}, "
                f"input dims {inp_sizes}."
            )


def _check_padding_irfft(
    sizes: Tuple[Optional[int]], dim: Tuple[int], inp_sizes: Tuple[int]
) -> None:
    if len(sizes) != len(dim):
        raise ValueError(f"{sizes}, {dim}")
    # All but last dims must be equal to input dims.
    for i, s in enumerate(sizes[:-1]):
        if s is None or s < 0:
            continue
        # Current Contrib RFFT does not support pad/trim yet.
        if s != inp_sizes[dim[i]]:
            raise RuntimeError(
                f"Padding/trimming is not yet supported, "
                f"got sizes {sizes}, DFT dims {dim}, "
                f"input dims {inp_sizes}."
            )
    # Check last dim.
    s = sizes[-1]
    if s is not None and s > 0:
        expected_size = 2 * (inp_sizes[dim[-1]] - 1)
        if s != expected_size:
            raise RuntimeError(
                f"Padding/trimming is not yet supported, got sizes {sizes}"
                f", DFT dims {dim}, input dims {inp_sizes}"
                f", expected last size {expected_size}."
            )


def _create_axes_perm(ndim: int, dims: Tuple[int]) -> Tuple[List[int], List[int]]:
    """Creates permuted axes indices for RFFT/IRFFT operators."""
    perm_in = list(range(ndim))
    perm_out = list(perm_in)
    # Move indices to the right to make 'dims' as innermost dimensions.
    for i in range(-1, -(len(dims) + 1), -1):
        perm_in[dims[i]], perm_in[i] = perm_in[i], perm_in[dims[i]]
    # Move indices to the left to restore original shape.
    for i in range(-len(dims), 0):
        perm_out[dims[i]], perm_out[i] = perm_out[i], perm_out[dims[i]]

    return perm_in, perm_out


def _scale_output_forward(
    output: Tensor, norm: str, sizes: torch.Size, ndim: int
) -> Tensor:
    """Scales the RFFT output according to norm parameter."""

    norm = "backward" if norm is None else norm
    if norm not in ["forward", "backward", "ortho"]:
        raise ValueError(norm)

    # No normalization for "backward" in RFFT ops.
    if norm in ["forward", "ortho"]:
        # Assuming DFT dimensions are the last. This is required by the current Contrib ops,
        # so the axes permutation of the input is done accordingly.
        dft_size = math.prod(sizes[-ndim:]).float()
        denom = torch.sqrt(dft_size) if norm == "ortho" else dft_size
        output = output / denom

    return output


def _scale_output_backward(
    output: Tensor, norm: str, sizes: torch.Size, ndim: int
) -> Tensor:
    """Scales the IRFFT output according to norm parameter."""

    norm = "backward" if norm is None else norm
    if norm not in ["forward", "backward", "ortho"]:
        raise ValueError(norm)

    # Things get interesting here: Contrib IRFFT op uses cuFFT cufftXtExec
    # followed by a custom CUDA kernel (`_Normalize`) which always performs
    # normalization (division by N) which means "norm" is essentially
    # always "backward" here. So we need to cancel this normalization
    # when norm is "forward" or "ortho".
    if norm in ["forward", "ortho"]:
        # Last dimension is complex numbers representation.
        # Second-to-last dim corresponds to last dim in RFFT transform.
        # This is required by the current Contrib ops,
        # so the axes permutation of the input is done previously.
        if not len(sizes) >= ndim + 1:
            raise ValueError
        dft_size = math.prod(sizes[-(ndim + 1) : -2])
        dft_size *= 2 * (sizes[-2] - 1)
        dft_size = dft_size.float()
        # Since cuFFT scales by 1/dft_size, replace this scale with appropriate one.
        scale = dft_size if norm == "forward" else torch.sqrt(dft_size)
        output = scale * output

    return output


class OnnxRfft(Function):
    """Auto-grad function to mimic rfft for ONNX exporting

    Note
    ----
    Should only be called during an ONNX export
    """

    @staticmethod
    def forward(ctx, input: Tensor) -> Tensor:
        if not torch.onnx.is_in_onnx_export():
            raise ValueError("Must be called only during ONNX export.")

        # We need to mimic the behavior of Contrib RFFT which assumes
        # DFT of last dim and no normalization.
        y = torch.fft.rfft(input, dim=-1, norm="backward")
        return torch.view_as_real(y)

    @staticmethod
    def symbolic(g: torch.Graph, input: torch.Value) -> torch.Value:
        """Symbolic representation for onnx graph"""
        return _contrib_rfft(g, input, ndim=1)


class OnnxRfft2(Function):
    """Auto-grad function to mimic rfft2 for ONNX exporting

    Note
    ----
    Should only be called during an ONNX export
    """

    @staticmethod
    def forward(ctx, input: Tensor) -> Tensor:
        if not torch.onnx.is_in_onnx_export():
            raise AssertionError("Must be called only during ONNX export.")

        # We need to mimic the behavior of Contrib RFFT which assumes
        # DFT of last dims and no normalization.
        y = torch.fft.rfft2(input, dim=(-2, -1), norm="backward")
        return torch.view_as_real(y)

    @staticmethod
    def symbolic(g: torch.Graph, input: torch.Value) -> torch.Value:
        """Symbolic representation for onnx graph"""
        return _contrib_rfft(g, input, ndim=2)


class OnnxIrfft(Function):
    """Auto-grad function to mimic irfft for ONNX exporting

    Note
    ----
    Should only be called during an ONNX export
    """

    @staticmethod
    def forward(ctx, input: Tensor) -> Tensor:
        if not torch.onnx.is_in_onnx_export():
            raise ValueError("Must be called only during ONNX export.")

        # We need to mimic the behavior of Contrib IRFFT which assumes
        # DFT of last dim and 1/n normalization.
        return torch.fft.irfft(torch.view_as_complex(input), dim=-1, norm="backward")

    @staticmethod
    def symbolic(g: torch.Graph, input: torch.Value) -> torch.Value:
        """Symbolic representation for onnx graph"""
        return _contrib_irfft(g, input, ndim=1)


class OnnxIrfft2(Function):
    """Auto-grad function to mimic irfft2 for ONNX exporting.

    Note
    ----
    Should only be called during an ONNX export
    """

    @staticmethod
    def forward(ctx, input: Tensor) -> Tensor:
        if not torch.onnx.is_in_onnx_export():
            raise AssertionError("Must be called only during ONNX export.")

        # We need to mimic the behavior of Contrib IRFFT which assumes
        # DFT of last dims and 1/n normalization.
        return torch.fft.irfft2(
            torch.view_as_complex(input), dim=(-2, -1), norm="backward"
        )

    @staticmethod
    def symbolic(g: torch.Graph, input: torch.Value) -> torch.Value:
        """Symbolic representation for onnx graph"""
        return _contrib_irfft(g, input, ndim=2)
```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/inference_helper.py
```python
# ignore_header_test

# climt/LICENSE
# @mcgibbon
# BSD License
# Copyright (c) 2016, Rodrigo Caballero
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


import datetime
from typing import TypeVar, Union

import numpy as np

# can replace this import with zoneinfo from the standard library in python3.9+.
import pytz

def rh_to_q(rh, T_K, p):
    """
    rh: 相對濕度 [%]
    T_K: 溫度 [K]
    p: 氣壓 [hPa]
    回傳 q [kg/kg]
    """
    p = (np.array(p)[:,np.newaxis]*np.ones([1,rh.shape[1]]))[:,:,np.newaxis]*np.ones([1,rh.shape[2]])
    T_C = T_K - 273.15
    es = 6.112 * np.exp((17.67 * T_C) / (T_C + 243.5))
    e = (rh / 100) * es
    w = 0.622 * e / (p - e)
    q = w / (1 + w)
    return q

def cos_zenith(times: list):
    lat = np.linspace(90, -90, 720, endpoint=False)
    lon = np.linspace(0, 360, 1440, endpoint=False)
    grid_y, grid_x = np.meshgrid(
        lat, lon, indexing="ij"
    )
    """Calculate cosine of zenith angle for given times.

    Parameters
    ----------
    times : list
        List of times to calculate cosine of zenith angle for

    Returns
    -------
    torch.Tensor
        Cosine of zenith angle for each time
    """
    # Convert generator to list to fix type incompatibility
    times_list = list(datetime.datetime.fromisoformat(str(t)[:19]) for t in times)
    cos_zen = [
        cos_zenith_angle(t, grid_x, grid_y)
        for t in times_list
    ]
    return np.stack(cos_zen, axis=0)


def compute_sza(
    lon: np.ndarray,
    lat: np.ndarray,
    time: np.datetime64,
    lead_time: np.timedelta64,
):
    _unix = np.datetime64(0, "s")
    _ds = np.timedelta64(1, "s")
    t = time + lead_time
    t = datetime.datetime.fromtimestamp((t - _unix) / _ds, tz=datetime.timezone.utc)
    print(t)
    return cos_zenith_angle(t, lon, lat)
# helper type
dtype = np.float32


T = TypeVar("T", np.ndarray, float)

TIMESTAMP_2000 = datetime.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.utc).timestamp()


def cos_zenith_angle(
    time: Union[T, datetime.datetime],
    lon: T,
    lat: T,
) -> T:  # pragma: no cover
    """
    Cosine of sun-zenith angle for lon, lat at time (UTC).
    If DataArrays are provided for the lat and lon arguments, their units will
    be assumed to be in degrees, unless they have a units attribute that
    contains "rad"; in that case they will automatically be converted to having
    units of degrees.

    Parameters
    ----------
    time: time in UTC
    lon: float or np.ndarray in degrees (E/W)
    lat: float or np.ndarray in degrees (N/S)

    Returns
    --------
    float, np.ndarray

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> angle = cos_zenith_angle(model_time, lat=360, lon=120)
    >>> abs(angle - -0.447817277) < 1e-6
    True
    """
    lon_rad = np.deg2rad(lon, dtype=dtype)
    lat_rad = np.deg2rad(lat, dtype=dtype)
    julian_centuries = _datetime_to_julian_century(time)
    return _star_cos_zenith(julian_centuries, lon_rad, lat_rad)


def cos_zenith_angle_from_timestamp(
    timestamp: T,
    lon: T,
    lat: T,
) -> T:
    """
    Compute cosine of zenith angle using UNIX timestamp

    Since the UNIX timestamp is a floating point or integer this routine can be
    compiled with jax.

    Parameters
    ----------
    timestamp: timestamp in seconds from UNIX epoch
    lon: longitude in degrees E
    lat: latitude in degrees N

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> angle = cos_zenith_angle_from_timestamp(model_time.timestamp(), lat=360, lon=120)
    >>> abs(angle - -0.447817277) < 1e-6
    True
    """
    lon_rad = np.deg2rad(lon, dtype=dtype)
    lat_rad = np.deg2rad(lat, dtype=dtype)
    julian_centuries = _timestamp_to_julian_century(timestamp)
    return _star_cos_zenith(julian_centuries, lon_rad, lat_rad)


def irradiance(
    t,
    S0=1361,
    e=0.0167,
    perihelion_longitude=282.895,
    mean_tropical_year=365.2422,
    newton_iterations: int = 3,
):
    """The flux of solar energy in W/m2 towards Earth

    The default orbital parameters are set to 2000 values.
    Over the period of 1900-2100 this will result in an error of at most 0.02%,
    so can be neglected for many applications.

    Parameters
    ----------
    t: linux timestamp
    S0: the solar constant in W/m2. This is the mean irradiance received by
        earth over a year.
    e: the eccentricity of earths elliptical orbit
    perihelion_longitude: spatial angle from moving vernal equinox to perihelion with Sun as angle vertex.
        Perihelion is moment when earth is closest to sun. vernal equinox is
        the longitude when the Earth crosses the equator from South to North.
    newton_iterations: number of iterations for newton solver for elliptic anomaly


    Notes
    -----

    TISR can be computed from Berger's formulas:

        Berger, A. (1978). Long-Term Variations of Daily Insolation and
        Quaternary Climatic Changes. Journal of the Atmospheric Sciences,
        35(12), 2362–2367.
        https://doi.org/10.1175/1520-0469(1978)035<2362:LTVODI>2.0.CO;2

    NASA Example computing the orbital parameters: https://data.giss.nasa.gov/modelE/ar5plots/srorbpar.html. From 1900-2100 these are the ranges::
        Orbital Parmameters

                                            Long. of
        Year     Eccentri    Obliquity    Perihel.
        (A.D.)      city      (degrees)    (degrees)
        ------    --------    ---------    --------
            1900   0.016744      23.4528      281.183
            2000   0.016704      23.4398      282.895
            2100   0.016663      23.4268      284.609

    """
    seconds_per_solar_day = 86400
    mean_tropical_year = mean_tropical_year * seconds_per_solar_day

    year_2000_equinox = datetime.datetime(2000, 3, 20, 7, 35, tzinfo=pytz.utc)

    # from appendix of Berger 1978
    M = (t - year_2000_equinox.timestamp()) % mean_tropical_year
    M = M / mean_tropical_year * 2 * np.pi
    M -= np.deg2rad(perihelion_longitude)

    # to get the elliptic anomaly E from the "mean anomaly" M
    # use eq. 6.37
    # https://link.springer.com/book/10.1007/978-3-662-53045-0)
    # r / a = (1 - e cos E )
    # E - e sin(E) = M
    def f(E):
        return E - e * np.sin(E) - M

    def fp(E):
        return 1 - e * np.cos(E)

    # newton iterations
    # initial guess
    E = M
    for _ in range(newton_iterations):
        E = E - f(E) / fp(E)

    rho = 1 - e * np.cos(E)
    return S0 / rho**2


def toa_incident_solar_radiation_accumulated(
    t,
    lat,
    lon,
    interval=3600,
    S0=1361,
    e=0.0167,
    perihelion_longitude=282.895,
    mean_tropical_year=365.2422,
):
    """Approximate ECMWF TISR with analytical formulas

    According to the ECWMF docs, the TISR variable is integrated over the
    preceeding hour.  Error is about 0.1% different from the ECMWF TISR
    variable.

    Parameters
    ----------
    t: linux timestamp
    lat, lon: latitude and longitude in degrees
    interval: the integral length in seconds over which the irradiance is integrated
    S0: the solar constant in W/m2. This is the mean irradiance received by
        earth over a year.
    e: the eccentricity of earths elliptical orbit
    perihelion_longitude: spatial angle from moving vernal equinox to perihelion with Sun as angle vertex.
        Perihelion is moment when earth is closest to sun. vernal equinox is
        the longitude when the Earth crosses the equator from South to North.


    Returns
    -------
    TOA incident solar radiation accumulated from [t-inteval, t] in J/m2

    Notes
    -----

    We make some approximations:

    The default orbital parameters are set to 2000 values.
    Over the period of 1900-2100 this will result in an error of at most 0.02%,
    so can be neglected for many applications.

    The irradiance is constant over the ``interval``.

    From ECWMF [docs](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Meanrates/fluxesandaccumulations)

        Such parameters, which are only available from forecasts, have undergone particular types of statistical processing (temporal mean or accumulation, respectively) over a period of time called the processing period. In addition, these parameters may, or may not, have been averaged in time, to produce monthly means.

        The accumulations (over the accumulation/processing period) in the short forecasts (from 06 and 18 UTC) of ERA5 are treated differently compared with those in ERA-Interim and operational data (where the accumulations are from the beginning of the forecast to the validity date/time). In the short forecasts of ERA5, the accumulations are since the previous post processing (archiving), so for:

        reanalysis: accumulations are over the hour (the accumulation/processing period) ending at the validity date/time
        ensemble: accumulations are over the 3 hours (the accumulation/processing period) ending at the validity date/time
        Monthly means (of daily means, stream=moda/edmo): accumulations have been scaled to have an "effective" processing period of one day, see section Monthly means
        Mean rate/flux parameters in ERA5 (e.g. Table 4 for surface and single levels) provide similar information to accumulations (e.g. Table 3 for surface and single levels), except they are expressed as temporal means, over the same processing periods, and so have units of "per second".

        Mean rate/flux parameters are easier to deal with than accumulations because the units do not vary with the processing period.
        The mean rate hydrological parameters (e.g. the "Mean total precipitation rate") have units of "kg m-2 s-1", which are equivalent to "mm s-1". They can be multiplied by 86400 seconds (24 hours) to convert to kg m-2 day-1 or mm day-1.
        Note that:

        For the CDS time, or validity time, of 00 UTC, the mean rates/fluxes and accumulations are over the hour (3 hours for the EDA) ending at 00 UTC i.e. the mean or accumulation is during part of the previous day.
        Mean rates/fluxes and accumulations are not available from the analyses.
        Mean rates/fluxes and accumulations at step=0 have values of zero because the length of the processing period is zero.

    """  # noqa
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)

    century = _timestamp_to_julian_century(t)
    ra, dec = _right_ascension_declination(century)
    interval_radians = interval / 86400 * 2 * np.pi
    # 0 <= h1 < 2 pi
    h1 = _local_hour_angle(century, lon, ra)
    h0 = h1 - interval_radians
    A = np.sin(lat) * np.sin(dec)
    B = np.cos(lat) * np.cos(dec)

    # assume irradiance is constant over the interval
    S = irradiance(t, S0, e, perihelion_longitude, mean_tropical_year)
    sec_per_rad = 86400 / (2 * np.pi)
    return S * _integrate_abs_cosz(A, B, h0, h1) * sec_per_rad


def _integrate_abs_cosz(A, B, h0, h1):
    """Analytically integrate max(A + B cos(h), 0) from h=h0 to h1"""

    hc = np.arccos(-A / B)

    def integrate_cosz(left, right):
        return A * (right - left) + B * (np.sin(right) - np.sin(left))

    def integrate_abs_cosz_from_zero_to(a):
        root1 = -hc + 2 * np.pi
        T = np.pi * 2

        # how many periods
        n = a // T

        # if there is a root
        a = a % T
        C = integrate_cosz(0, np.where(a < hc, a, hc))
        D = np.where(root1 < a, integrate_cosz(root1, a), 0)
        total = integrate_cosz(0, hc) + integrate_cosz(root1, 2 * np.pi)
        return C + D + total * n

    return np.where(
        np.isnan(hc),
        np.maximum(integrate_cosz(h0, h1), 0),
        integrate_abs_cosz_from_zero_to(h1) - integrate_abs_cosz_from_zero_to(h0),
    )


def _datetime_to_julian_century(time: datetime.datetime) -> float:
    return _days_from_2000(time) / 36525.0


def _days_from_2000(model_time):
    """Get the days since year 2000.

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> _days_from_2000(model_time)
    731.0
    """
    if isinstance(model_time, datetime.datetime):
        model_time = model_time.replace(tzinfo=pytz.utc)

    date_type = type(np.asarray(model_time).ravel()[0])
    if date_type not in [datetime.datetime]:
        raise ValueError(
            f"model_time has an invalid date type. It must be "
            f"datetime.datetime. Got {date_type}."
        )
    return _total_days(model_time - date_type(2000, 1, 1, 12, 0, 0, tzinfo=pytz.utc))


def _total_days(time_diff):
    """
    Total time in units of days
    """
    return np.asarray(time_diff).astype("timedelta64[us]") / np.timedelta64(1, "D")


def _timestamp_to_julian_century(timestamp):
    seconds_in_day = 86400
    days_in_julian_century = 36525.0
    return (timestamp - TIMESTAMP_2000) / days_in_julian_century / seconds_in_day


def _greenwich_mean_sidereal_time(jul_centuries):
    """
    Greenwich mean sidereal time, in radians.
    Reference:
        The AIAA 2006 implementation:
            http://www.celestrak.com/publications/AIAA/2006-6753/

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> c = _timestamp_to_julian_century(model_time.timestamp())
    >>> g_time = _greenwich_mean_sidereal_time(c)
    >>> abs(g_time - 4.903831411) < 1e-8
    True
    """
    theta = 67310.54841 + jul_centuries * (
        876600 * 3600
        + 8640184.812866
        + jul_centuries * (0.093104 - jul_centuries * 6.2 * 10e-6)
    )

    theta_radians = np.deg2rad(theta / 240.0) % (2 * np.pi)

    return theta_radians


def _local_mean_sidereal_time(julian_centuries, longitude):
    """
    Local mean sidereal time. requires longitude in radians.
    Ref:
        http://www.setileague.org/askdr/lmst.htm


    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> c = _timestamp_to_julian_century(model_time.timestamp())
    >>> l_time = _local_mean_sidereal_time(c, np.deg2rad(90))
    >>> abs(l_time - 6.474627737) < 1e-8
    True
    """
    return _greenwich_mean_sidereal_time(julian_centuries) + longitude


def _sun_ecliptic_longitude(julian_centuries):
    """
    Ecliptic longitude of the sun.
    Reference:
        http://www.geoastro.de/elevaz/basics/meeus.htm

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> c = _timestamp_to_julian_century(model_time.timestamp())
    >>> lon = _sun_ecliptic_longitude(c)
    >>> abs(lon - 17.469114444) < 1e-8
    True
    """

    # mean anomaly calculation
    mean_anomaly = np.deg2rad(
        357.52910
        + 35999.05030 * julian_centuries
        - 0.0001559 * julian_centuries * julian_centuries
        - 0.00000048 * julian_centuries * julian_centuries * julian_centuries
    )

    # mean longitude
    mean_longitude = np.deg2rad(
        280.46645 + 36000.76983 * julian_centuries + 0.0003032 * (julian_centuries**2)
    )

    d_l = np.deg2rad(
        (1.914600 - 0.004817 * julian_centuries - 0.000014 * (julian_centuries**2))
        * np.sin(mean_anomaly)
        + (0.019993 - 0.000101 * julian_centuries) * np.sin(2 * mean_anomaly)
        + 0.000290 * np.sin(3 * mean_anomaly)
    )

    # true longitude
    return mean_longitude + d_l


def _obliquity_star(julian_centuries):
    """
    return obliquity of the sun
    Use 5th order equation from
    https://en.wikipedia.org/wiki/Ecliptic#Obliquity_of_the_ecliptic

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> julian_centuries = _days_from_2000(model_time) / 36525.0
    >>> obl = _obliquity_star(julian_centuries)
    >>> abs(obl - 0.409088056) < 1e-8
    True
    """
    return np.deg2rad(
        23.0
        + 26.0 / 60
        + 21.406 / 3600.0
        - (
            46.836769 * julian_centuries
            - 0.0001831 * (julian_centuries**2)
            + 0.00200340 * (julian_centuries**3)
            - 0.576e-6 * (julian_centuries**4)
            - 4.34e-8 * (julian_centuries**5)
        )
        / 3600.0
    )


def _right_ascension_declination(julian_centuries):
    """
    Right ascension and declination of the sun.
    Ref:
        http://www.geoastro.de/elevaz/basics/meeus.htm

    Example:
    --------
    >>> model_time = datetime.datetime(2002, 1, 1, 12, 0, 0)
    >>> c = _timestamp_to_julian_century(model_time.timestamp())
    >>> out1, out2 = _right_ascension_declination(c)
    >>> abs(out1 - -1.363787213) < 1e-8
    True
    >>> abs(out2 - -0.401270126) < 1e-8
    True
    """
    eps = _obliquity_star(julian_centuries)
    eclon = _sun_ecliptic_longitude(julian_centuries)
    x = np.cos(eclon)
    y = np.cos(eps) * np.sin(eclon)
    z = np.sin(eps) * np.sin(eclon)
    r = np.sqrt(1.0 - z * z)
    # sun declination
    declination = np.arctan2(z, r)
    # right ascension
    right_ascension = 2 * np.arctan2(y, (x + r))
    return right_ascension, declination


def _local_hour_angle(julian_centuries, longitude, right_ascension):
    """
    Hour angle at model_time for the given longitude and right_ascension
    longitude in radians
    Ref:
        https://en.wikipedia.org/wiki/Hour_angle#Relation_with_the_right_ascension
    """
    return _local_mean_sidereal_time(julian_centuries, longitude) - right_ascension


def _star_cos_zenith(julian_centuries, lon, lat):
    """
    Return cosine of star zenith angle
    lon,lat in radians
    Ref:
        Azimuth:
            https://en.wikipedia.org/wiki/Solar_azimuth_angle#Formulas
        Zenith:
            https://en.wikipedia.org/wiki/Solar_zenith_angle
    """

    ra, dec = _right_ascension_declination(julian_centuries)
    h_angle = _local_hour_angle(julian_centuries, lon, ra)

    cosine_zenith = np.sin(lat) * np.sin(dec) + np.cos(lat) * np.cos(dec) * np.cos(
        h_angle
    )

    return cosine_zenith
```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/modafno.py
```python
# SPDX-FileCopyrightText: Copyright (c) 2023 - 2025 NVIDIA CORPORATION & AFFILIATES.
# SPDX-FileCopyrightText: All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from functools import partial
from typing import List, Literal, Type, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

# import physicsnemo  # noqa: F401 for docs
# import physicsnemo.models.layers.fft as fft
# import .fft as fft
from .fft import rfft2, real, imag, view_as_complex, irfft2
from .afno import AFNO2DLayer, AFNOMlp, PatchEmbed

from .modembed import ModEmbedNet

Tensor = torch.Tensor


class ScaleShiftMlp(nn.Module):
    """MLP used to compute the scale and shift parameters of the ModAFNO block

    Parameters
    ----------
    in_features : int
        Input feature size
    out_features : int
        Output feature size
    hidden_features : int, optional
        Hidden feature size, defaults to 2 * out_features
    hidden_layers : int, optional
        Number of hidden layers, defaults to 0
    activation_fn : nn.Module, optional
        Activation function, by default nn.GELU
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_features: Union[int, None] = None,
        hidden_layers: int = 0,
        activation_fn: Type[nn.Module] = nn.GELU,
    ):
        super().__init__()
        if hidden_features is None:
            hidden_features = out_features * 2

        sequence = [nn.Linear(in_features, hidden_features), activation_fn()]
        for _ in range(hidden_layers):
            sequence += [nn.Linear(hidden_features, hidden_features), activation_fn()]
        sequence.append(nn.Linear(hidden_features, out_features * 2))
        self.net = nn.Sequential(*sequence)

    def forward(self, x: Tensor):
        (scale, shift) = torch.chunk(self.net(x), 2, dim=1)
        return (1 + scale, shift)


class ModAFNOMlp(AFNOMlp):
    """Modulated MLP used inside ModAFNO

    Parameters
    ----------
    in_features : int
        Input feature size
    latent_features : int
        Latent feature size
    out_features : int
        Output feature size
    activation_fn :  nn.Module, optional
        Activation function, by default nn.GELU
    drop : float, optional
        Drop out rate, by default 0.0
    scale_shift_kwargs : dict, optional
        Options to the MLP that computes the scale-shift parameters
    """

    def __init__(
        self,
        in_features: int,
        latent_features: int,
        out_features: int,
        mod_features: int,
        activation_fn: nn.Module = nn.GELU(),
        drop: float = 0.0,
        scale_shift_kwargs: Union[dict, None] = None,
    ):
        super().__init__(
            in_features=in_features,
            latent_features=latent_features,
            out_features=out_features,
            activation_fn=activation_fn,
            drop=drop,
        )
        if scale_shift_kwargs is None:
            scale_shift_kwargs = {}
        self.scale_shift = ScaleShiftMlp(
            mod_features, latent_features, **scale_shift_kwargs
        )

    def forward(self, x: Tensor, mod_embed: Tensor) -> Tensor:
        (scale, shift) = self.scale_shift(mod_embed)

        scale_shift_shape = (scale.shape[0],) + (1,) * (x.ndim - 2) + (scale.shape[1],)
        scale = scale.view(*scale_shift_shape)
        shift = shift.view(*scale_shift_shape)

        x = self.fc1(x)
        x = x * scale + shift
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x


class ModAFNO2DLayer(AFNO2DLayer):
    """AFNO spectral convolution layer

    Parameters
    ----------
    hidden_size : int
        Feature dimensionality
    mod_features : int
        Number of modulation features
    num_blocks : int, optional
        Number of blocks used in the block diagonal weight matrix, by default 8
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1
    hidden_size_factor : int, optional
        Factor to increase spectral features by after weight multiplication, by default 1
    scale_shift_kwargs : dict, optional
        Options to the MLP that computes the scale-shift parameters
    scale_shift_mode: ["complex", "real"]
        If 'complex' (default), compute the scale-shift operation using complex
        operations. If 'real', use real operations.
    """

    def __init__(
        self,
        hidden_size: int,
        mod_features: int,
        num_blocks: int = 8,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1,
        hidden_size_factor: int = 1,
        scale_shift_kwargs: Union[dict, None] = None,
        scale_shift_mode: Literal["complex", "real"] = "complex",
    ):
        super().__init__(
            hidden_size=hidden_size,
            num_blocks=num_blocks,
            sparsity_threshold=sparsity_threshold,
            hard_thresholding_fraction=hard_thresholding_fraction,
            hidden_size_factor=hidden_size_factor,
        )

        if scale_shift_mode not in ("complex", "real"):
            raise ValueError("scale_shift_mode must be 'real' or 'complex'")
        self.scale_shift_mode = scale_shift_mode
        self.channel_mul = 1 if scale_shift_mode == "real" else 2
        if scale_shift_kwargs is None:
            scale_shift_kwargs = {}
        self.scale_shift = ScaleShiftMlp(
            mod_features,
            self.num_blocks
            * self.block_size
            * self.hidden_size_factor
            * self.channel_mul,
            **scale_shift_kwargs,
        )

    def forward(self, x: Tensor, mod_embed: Tensor) -> Tensor:
        bias = x

        dtype = x.dtype
        x = x.float()
        B, H, W, C = x.shape
        # Using ONNX friendly FFT functions
        # x = fft.rfft2(x, dim=(1, 2), norm="ortho")
        x = rfft2(x, dim=(1, 2), norm="ortho")
        # x_real, x_imag = fft.real(x), fft.imag(x)
        x_real, x_imag = real(x), imag(x)
        x_real = x_real.reshape(B, H, W // 2 + 1, self.num_blocks, self.block_size)
        x_imag = x_imag.reshape(B, H, W // 2 + 1, self.num_blocks, self.block_size)
        o1_shape = (
            B,
            H,
            W // 2 + 1,
            self.num_blocks,
            self.block_size * self.hidden_size_factor,
        )
        scale_shift_shape = (B, self.channel_mul, 1, o1_shape[3], o1_shape[4])

        o1_real = torch.zeros(o1_shape, device=x.device)
        o1_imag = torch.zeros(o1_shape, device=x.device)
        o2 = torch.zeros(x_real.shape + (2,), device=x.device)

        total_modes = min(H, W) // 2 + 1
        kept_modes = int(total_modes * self.hard_thresholding_fraction)

        o1_re = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                x_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w1[0],
            )
            - torch.einsum(
                "nyxbi,bio->nyxbo",
                x_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w1[1],
            )
            + self.b1[0]
        )

        o1_im = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                x_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w1[0],
            )
            + torch.einsum(
                "nyxbi,bio->nyxbo",
                x_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w1[1],
            )
            + self.b1[1]
        )

        # scale-shift operation
        (scale, shift) = self.scale_shift(mod_embed)
        scale = scale.view(*scale_shift_shape)
        shift = shift.view(*scale_shift_shape)
        if self.scale_shift_mode == "real":
            o1_re = o1_re * scale + shift
            o1_im = o1_im * scale + shift
        elif self.scale_shift_mode == "complex":
            (scale_re, scale_im) = torch.chunk(scale, 2, dim=1)
            (shift_re, shift_im) = torch.chunk(shift, 2, dim=1)
            (o1_re, o1_im) = (
                o1_re * scale_re - o1_im * scale_im + shift_re,
                o1_im * scale_re + o1_re * scale_im + shift_im,
            )

        o1_real[:, total_modes - kept_modes : total_modes + kept_modes, :kept_modes] = (
            F.relu(o1_re)
        )

        o1_imag[:, total_modes - kept_modes : total_modes + kept_modes, :kept_modes] = (
            F.relu(o1_im)
        )

        o2[
            :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes, ..., 0
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[0],
            )
            - torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[1],
            )
            + self.b2[0]
        )

        o2[
            :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes, ..., 1
        ] = (
            torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_imag[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[0],
            )
            + torch.einsum(
                "nyxbi,bio->nyxbo",
                o1_real[
                    :, total_modes - kept_modes : total_modes + kept_modes, :kept_modes
                ],
                self.w2[1],
            )
            + self.b2[1]
        )

        x = F.softshrink(o2, lambd=self.sparsity_threshold)
        # x = fft.view_as_complex(x)
        x = view_as_complex(x)
        # TODO(akamenev): replace the following branching with
        # a one-liner, something like x.reshape(..., -1).squeeze(-1),
        # but this currently fails during ONNX export.
        if torch.onnx.is_in_onnx_export():
            x = x.reshape(B, H, W // 2 + 1, C, 2)
        else:
            x = x.reshape(B, H, W // 2 + 1, C)
        # Using ONNX friendly FFT functions
        # x = fft.irfft2(x, s=(H, W), dim=(1, 2), norm="ortho")
        x = irfft2(x, s=(H, W), dim=(1, 2), norm="ortho")
        x = x.type(dtype)

        return x + bias


class Block(nn.Module):
    """AFNO block, spectral convolution and MLP

    Parameters
    ----------
    embed_dim : int
        Embedded feature dimensionality
    mod_dim : int
        Modululation input dimensionality
    num_blocks : int, optional
        Number of blocks used in the block diagonal weight matrix, by default 8
    mlp_ratio : float, optional
        Ratio of MLP latent variable size to input feature size, by default 4.0
    drop : float, optional
        Drop out rate in MLP, by default 0.0
    activation_fn: nn.Module, optional
        Activation function used in MLP, by default nn.GELU
    norm_layer : nn.Module, optional
        Normalization function, by default nn.LayerNorm
    double_skip : bool, optional
        Residual, by default True
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1
    modulate_filter: bool, optional
        Whether to compute the modulation for the FFT filter
    modulate_mlp: bool, optional
        Whether to compute the modulation for the MLP
    scale_shift_mode: ["complex", "real"]
        If 'complex' (default), compute the scale-shift operation using complex
        operations. If 'real', use real operations.
    """

    def __init__(
        self,
        embed_dim: int,
        mod_dim: int,
        num_blocks: int = 8,
        mlp_ratio: float = 4.0,
        drop: float = 0.0,
        activation_fn: nn.Module = nn.GELU(),
        norm_layer: nn.Module = nn.LayerNorm,
        double_skip: bool = True,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
        modulate_filter: bool = True,
        modulate_mlp: bool = True,
        scale_shift_mode: Literal["complex", "real"] = "real",
    ):
        super().__init__()
        self.norm1 = norm_layer(embed_dim)
        if modulate_filter:
            self.filter = ModAFNO2DLayer(
                embed_dim,
                mod_dim,
                num_blocks,
                sparsity_threshold,
                hard_thresholding_fraction,
                scale_shift_mode=scale_shift_mode,
            )
            self.apply_filter = lambda x, mod_embed: self.filter(x, mod_embed)
        else:
            self.filter = AFNO2DLayer(
                embed_dim, num_blocks, sparsity_threshold, hard_thresholding_fraction
            )
            self.apply_filter = lambda x, mod_embed: self.filter(x)

        self.norm2 = norm_layer(embed_dim)
        mlp_latent_dim = int(embed_dim * mlp_ratio)
        if modulate_mlp:
            self.mlp = ModAFNOMlp(
                in_features=embed_dim,
                latent_features=mlp_latent_dim,
                out_features=embed_dim,
                mod_features=mod_dim,
                activation_fn=activation_fn,
                drop=drop,
            )
            self.apply_mlp = lambda x, mod_embed: self.mlp(x, mod_embed)
        else:
            self.mlp = AFNOMlp(
                in_features=embed_dim,
                latent_features=mlp_latent_dim,
                out_features=embed_dim,
                activation_fn=activation_fn,
                drop=drop,
            )
            self.apply_mlp = lambda x, mod_embed: self.mlp(x)
        self.double_skip = double_skip
        self.modulate_filter = modulate_filter
        self.modulate_mlp = modulate_mlp

    def forward(self, x: Tensor, mod_embed: Tensor) -> Tensor:
        residual = x
        x = self.norm1(x)
        x = self.apply_filter(x, mod_embed)

        if self.double_skip:
            x = x + residual
            residual = x

        x = self.norm2(x)
        x = self.apply_mlp(x, mod_embed)
        x = x + residual
        return x


class ModAFNO(nn.Module):
    """Modulated Adaptive Fourier neural operator (ModAFNO) model.

    Parameters
    ----------
    inp_shape : List[int]
        Input image dimensions [height, width]
    in_channels : int, optional
        Number of input channels
    out_channels: int, optional
        Number of output channels
    embed_model: dict, optional
        Dictionary of arguments to pass to the `ModEmbedNet` embedding model
    patch_size : List[int], optional
        Size of image patches, by default [16, 16]
    embed_dim : int, optional
        Embedded channel size, by default 256
    mod_dim : int
        Modululation input dimensionality
    modulate_filter: bool, optional
        Whether to compute the modulation for the FFT filter, by default True
    modulate_mlp: bool, optional
        Whether to compute the modulation for the MLP, by default True
    scale_shift_mode: ["complex", "real"]
        If 'complex' (default), compute the scale-shift operation using complex
        operations. If 'real', use real operations.
    depth : int, optional
        Number of AFNO layers, by default 4
    mlp_ratio : float, optional
        Ratio of layer MLP latent variable size to input feature size, by default 4.0
    drop_rate : float, optional
        Drop out rate in layer MLPs, by default 0.0
    num_blocks : int, optional
        Number of blocks in the block-diag frequency weight matrices, by default 16
    sparsity_threshold : float, optional
        Sparsity threshold (softshrink) of spectral features, by default 0.01
    hard_thresholding_fraction : float, optional
        Threshold for limiting number of modes used [0,1], by default 1

    The default settings correspond to the implementation in the paper cited below.

    Example
    -------
    >>> import torch
    >>> from physicsnemo.models.afno import ModAFNO
    >>> model = ModAFNO(
    ...     inp_shape=[32, 32],
    ...     in_channels=2,
    ...     out_channels=1,
    ...     patch_size=(8, 8),
    ...     embed_dim=16,
    ...     depth=2,
    ...     num_blocks=2,
    ... )
    >>> input = torch.randn(32, 2, 32, 32) #(N, C, H, W)
    >>> time = torch.full((32, 1), 0.5)
    >>> output = model(input, time)
    >>> output.size()
    torch.Size([32, 1, 32, 32])

    Note
    ----
    Reference: Leinonen et al. "Modulated Adaptive Fourier Neural Operators
    for Temporal Interpolation of Weather Forecasts." arXiv preprint arXiv:TODO (2024).
    """

    def __init__(
        self,
        inp_shape: List[int],
        in_channels: int = 155,
        out_channels: int = 73,
        embed_model: Union[dict, None] = None,
        patch_size: List[int] = [2, 2],
        embed_dim: int = 512,
        mod_dim: int = 64,
        modulate_filter: bool = True,
        modulate_mlp: bool = True,
        scale_shift_mode: Literal["complex", "real"] = "complex",
        depth: int = 12,
        mlp_ratio: float = 2.0,
        drop_rate: float = 0.0,
        num_blocks: int = 1,
        sparsity_threshold: float = 0.01,
        hard_thresholding_fraction: float = 1.0,
    ) -> None:
        super().__init__()
        if len(inp_shape) != 2:
            raise ValueError("inp_shape should be a list of length 2")
        if len(patch_size) != 2:
            raise ValueError("patch_size should be a list of length 2")

        if not (
            inp_shape[0] % patch_size[0] == 0 and inp_shape[1] % patch_size[1] == 0
        ):
            raise ValueError(
                f"input shape {inp_shape} should be divisible by patch_size {patch_size}"
            )

        self.in_chans = in_channels
        self.out_chans = out_channels
        self.inp_shape = inp_shape
        self.patch_size = patch_size
        self.num_features = self.embed_dim = embed_dim
        self.num_blocks = num_blocks
        self.modulate_filter = modulate_filter
        self.modulate_mlp = modulate_mlp
        self.scale_shift_mode = scale_shift_mode
        norm_layer = partial(nn.LayerNorm, eps=1e-6)

        self.patch_embed = PatchEmbed(
            inp_shape=inp_shape,
            in_channels=self.in_chans,
            patch_size=self.patch_size,
            embed_dim=embed_dim,
        )
        num_patches = self.patch_embed.num_patches

        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, embed_dim))
        self.pos_drop = nn.Dropout(p=drop_rate)

        self.h = inp_shape[0] // self.patch_size[0]
        self.w = inp_shape[1] // self.patch_size[1]

        self.blocks = nn.ModuleList(
            [
                Block(
                    embed_dim=embed_dim,
                    mod_dim=mod_dim,
                    num_blocks=self.num_blocks,
                    mlp_ratio=mlp_ratio,
                    drop=drop_rate,
                    norm_layer=norm_layer,
                    sparsity_threshold=sparsity_threshold,
                    hard_thresholding_fraction=hard_thresholding_fraction,
                    modulate_filter=modulate_filter,
                    modulate_mlp=modulate_mlp,
                    scale_shift_mode=scale_shift_mode,
                )
                for i in range(depth)
            ]
        )

        self.head = nn.Linear(
            embed_dim,
            self.out_chans * self.patch_size[0] * self.patch_size[1],
            bias=False,
        )

        torch.nn.init.trunc_normal_(self.pos_embed, std=0.02)
        self.apply(self._init_weights)

        self.mod_additive_proj = nn.Linear(mod_dim, embed_dim)
        if not (modulate_mlp or modulate_filter):
            self.mod_embed_net = nn.Identity()
        else:
            embed_model = {} if embed_model is None else embed_model
            self.mod_embed_net = ModEmbedNet(**embed_model)

    def _init_weights(self, m: nn.Module):
        """Init model weights"""
        if isinstance(m, nn.Linear):
            torch.nn.init.trunc_normal_(m.weight, std=0.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward_features(self, x: Tensor, mod: Tensor) -> Tensor:
        """Forward pass of core ModAFNO"""
        B = x.shape[0]
        x = self.patch_embed(x)
        x = x + self.pos_embed
        x = self.pos_drop(x)

        mod_embed = self.mod_embed_net(mod)
        mod_additive = self.mod_additive_proj(mod_embed).unsqueeze(dim=(1))
        x = x + mod_additive

        x = x.reshape(B, self.h, self.w, self.embed_dim)
        for blk in self.blocks:
            x = blk(x, mod_embed=mod_embed)

        return x

    def forward(self, x: Tensor, mod: Tensor) -> Tensor:
        """The full ModAFNO model logic."""
        x = self.forward_features(x, mod)
        x = self.head(x)

        # Correct tensor shape back into [B, C, H, W]
        # [b h w (p1 p2 c_out)]
        out = x.view(list(x.shape[:-1]) + [self.patch_size[0], self.patch_size[1], -1])
        # [b h w p1 p2 c_out]
        out = torch.permute(out, (0, 5, 1, 3, 2, 4))
        # [b c_out, h, p1, w, p2]
        out = out.reshape(list(out.shape[:2]) + [self.inp_shape[0], self.inp_shape[1]])
        # [b c_out, (h*p1), (w*p2)]
        return out
```

## File: externals/fcn-regpgw/modAFNO_test/modAFNO_model/modembed.py
```python
# SPDX-FileCopyrightText: Copyright (c) 2023 - 2025 NVIDIA CORPORATION & AFFILIATES.
# SPDX-FileCopyrightText: All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Type

import torch
from torch import Tensor, nn


class PositionalEmbedding(nn.Module):
    """
    A module for generating positional embeddings based on timesteps.

    Parameters:
    -----------
    num_channels : int
        Number of channels for the embedding.
    """

    def __init__(self, num_channels: int):
        super().__init__()
        self.num_channels = num_channels

        freqs = torch.pi * torch.arange(
            start=1, end=self.num_channels // 2 + 1, dtype=torch.float32
        )
        self.register_buffer("freqs", freqs)

    def forward(self, x: Tensor) -> Tensor:
        x = x.view(-1).outer(self.freqs.to(x.dtype))
        x = torch.cat([x.cos(), x.sin()], dim=1)
        return x


class OneHotEmbedding(nn.Module):
    """
    A module for generating one-hot embeddings based on timesteps.

    Parameters:
    -----------
    num_channels : int
        Number of channels for the embedding.
    """

    def __init__(self, num_channels: int):
        super().__init__()
        self.num_channels = num_channels
        ind = torch.arange(num_channels)
        ind = ind.view(1, len(ind))
        self.register_buffer("indices", ind)

    def forward(self, t: Tensor) -> Tensor:
        ind = t * (self.num_channels - 1)
        return torch.clamp(1 - torch.abs(ind - self.indices), min=0)


class ModEmbedNet(nn.Module):
    """
    A network that generates a timestep embedding and processes it with an MLP.

    Parameters:
    -----------
    max_time : float, optional
        Maximum input time. The inputs to `forward` is should be in the range [0, max_time].
    dim : int, optional
        The dimensionality of the time embedding.
    depth : int, optional
        The number of layers in the MLP.
    activation_fn:
        The activation function, default GELU.
    method : str, optional
        The embedding method. Either "sinusoidal" (default) or "onehot".
    """

    def __init__(
        self,
        max_time: float = 1.0,
        dim: int = 64,
        depth: int = 1,
        activation_fn: Type[nn.Module] = nn.GELU,
        method: str = "sinusoidal",
    ):
        super().__init__()
        self.max_time = max_time
        self.method = method
        if method == "onehot":
            self.onehot_embed = OneHotEmbedding(dim)
        elif method == "sinusoidal":
            self.sinusoid_embed = PositionalEmbedding(dim)
        else:
            raise ValueError(f"Embedding '{method}' not supported")

        self.dim = dim

        blocks = []
        for _ in range(depth):
            blocks.extend([nn.Linear(dim, dim), activation_fn()])
        self.mlp = nn.Sequential(*blocks)

    def forward(self, t: Tensor) -> Tensor:
        t = t / self.max_time
        if self.method == "onehot":
            emb = self.onehot_embed(t)
        elif self.method == "sinusoidal":
            emb = self.sinusoid_embed(t)

        return self.mlp(emb)
```

## File: externals/fcn-regpgw/modAFNO_test/inference.py
```python
import numpy as np
import xarray
import torch
import tarfile, os
from datetime import datetime, timezone
from modAFNO_model.inference_helper import cos_zenith, rh_to_q
from modAFNO_model.modafno import ModAFNO

## Open tar file and extract contents to temporary directory
cached_file_name = "modAFNO_weight/fcinterp-modafno-2x2.mdlus"
local_path = "modAFNO_weight/model_weight"
@staticmethod
def safe_members(tar, local_path):
    for member in tar.getmembers():
        if (
            ".." in member.name
            or os.path.isabs(member.name)
            or os.path.realpath(os.path.join(local_path, member.name)).startswith(
                os.path.realpath(local_path)
            )
        ):
            yield member
        else:
            print(f"Skipping potentially malicious file: {member.name}")

if not os.path.exists(local_path):                  
    with tarfile.open(cached_file_name, "r") as tar:
        # Safely extract while supporting Python < 3.12
        extract_kwargs = dict(
            path=local_path,
            members=list(safe_members(tar, local_path)),
        )
        
        if "filter" in tar.extractall.__code__.co_varnames:
            extract_kwargs["filter"] = "data"
        tar.extractall(**extract_kwargs)  # noqa: S202

#%% load model
# load model checkpoint
model_dict = torch.load(
    f"{local_path}/model.pt", map_location="cpu"
)

# model precipnet model
model = ModAFNO(
    inp_shape=[720, 1440],
    in_channels=155,
    out_channels=73,
    embed_model={"dim": 64, 
                "depth": 1, 
                "method": "sinusoidal"},
    patch_size=(2, 2),
    embed_dim=512,
    mod_dim=64,
    modulate_filter=True,
    modulate_mlp=True,
    scale_shift_mode="complex",
    depth=12,
    num_blocks=1,
    mlp_ratio=2,   
    drop_rate=0.0,
    sparsity_threshold=0.01,
    hard_thresholding_fraction=1.0
)

# combine model
model_dict.pop('device_buffer', None)
model_dict.pop('backbone.device_buffer', None)
model.load_state_dict(model_dict,strict=True)


#%% 
## prepare data
lat = np.linspace(90, -90, 720, endpoint=False)
lon = np.linspace(0, 360, 1440, endpoint=False)

grid_y, grid_x = np.meshgrid(lat, lon, indexing="ij")
sincos_latlon = np.stack([np.sin(grid_y), np.cos(grid_y), np.sin(grid_x), np.cos(grid_x)], axis=0)

# setting
# input_folder = '/wk2/yungyun/code_space/FCNV2_test/output_data_2023072400'
input_folder = '/wk2/yungyun/code_space/FCNV2_test/output_IFS_2025072400'
files = os.listdir(input_folder)
# for i in range(len(files)):
IC_time = "2025072400"
device = 'cpu'
save_folder = 'test_interpolation_IFS'
os.makedirs(save_folder, exist_ok=True)

IC_time = datetime.strptime(IC_time,"%Y%m%d%H").strftime("%Y-%m-%dT%H")
IC_time = np.datetime64(f'{IC_time}:00:00','s')
# model
modAFNO_weight = 'modAFNO_weight'
input_center = np.load(f"{modAFNO_weight}/global_means.npy")[0,:73,:,:]
input_scale = np.load(f"{modAFNO_weight}/global_stds.npy")[0,:73,:,:]
lsm = xarray.open_dataset(f"{modAFNO_weight}/land_sea_mask.nc")["LSM"].values[ :, :-1]
orography = xarray.open_dataset(f"{modAFNO_weight}/orography.nc")["Z"].values[ :, :-1]
orography = (orography - orography.mean()) / orography.std()
pressure_level = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]
# intro_data = np.full([len(files),155,720,1440],0.0)
static_data = np.concatenate([sincos_latlon,orography,lsm], axis=0)
start_i = 0
for i in range(len(files)):
    # data1 = np.load(os.path.join(input_folder,files[i]))
    data1 = np.load(os.path.join(input_folder,f'output_weather_{(start_i+i)*6}h.npy'))
    x1_data = data1[:,:-1,:].copy()
    x1_data[60:73,:,:] = rh_to_q(data1[60:,:-1,:],data1[47:60,:-1,:],pressure_level)
    x1_data[  :73,:,:] = (x1_data[:73,:,:]-input_center)/input_scale
    
    data2 = np.load(os.path.join(input_folder,f'output_weather_{(start_i+i+1)*6}h.npy'))
    x2_data = data2[:,:-1,:].copy()
    x2_data[60:73,:,:] = rh_to_q(data2[60:,:-1,:],data2[47:60,:-1,:],pressure_level)
    x2_data[:73,:,:]   = (x2_data[:73,:,:]-input_center)/input_scale
    inter_data = np.concatenate([x1_data, x2_data],axis=0)
    
    for intro_i in range(6):
        target_time = (start_i+i)*6+intro_i
        time_data = cos_zenith([IC_time+np.timedelta64((start_i+i)*6, "h"), IC_time+np.timedelta64((start_i+i+1)*6, "h"), IC_time+np.timedelta64((start_i+i)*6+intro_i, "h")])
        total_data = np.concatenate([inter_data,time_data,static_data], axis=0)
        total_data = torch.Tensor(total_data[np.newaxis,...])
        t_norm = torch.Tensor([intro_i / 6])
        total_data = total_data.to(device)
        t_norm = t_norm.to(device)
        model = model.to(device)
        model.eval()
        print(f'start predict {target_time}h')
        out = model(total_data, t_norm)
        out = out.detach().numpy()
        out *= input_scale
        out += input_center    
        np.save(os.path.join(save_folder, f'output_weather_{target_time:0>3}h'),out.squeeze())
        print(f'save {target_time}h')
# intro_data = torch.Tensor(intro_data)
```
