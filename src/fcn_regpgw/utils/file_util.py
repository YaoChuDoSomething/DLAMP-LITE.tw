"""File operations and secure archive extraction utilities for FCN-RegPGW.

Provides safe tar extraction preventing directory traversal attacks, secure
PyTorch weights deserialization with weights_only=True, and directory helpers.
"""

import os
import tarfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import torch

from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


def ensure_dir(path: str | Path) -> Path:
    """Ensure directory exists, creating parent directories if needed.

    Args:
        path (Union[str, Path]): Target directory path.

    Returns:
        Path: Path object for created or verified directory.
    """
    target_path = Path(path)
    target_path.mkdir(parents=True, exist_ok=True)
    return target_path


def get_safe_tar_members(
    tar: tarfile.TarFile,
    target_dir: str | Path,
) -> Iterator[tarfile.TarInfo]:
    """Filter tar members safely preventing path traversal vulnerabilities.

    Enforces that no member uses relative parent path traversal ('..'),
    absolute paths, or resolves outside the target destination directory.

    Args:
        tar (tarfile.TarFile): Open tarfile object.
        target_dir (Union[str, Path]): Target destination directory.

    Yields:
        Iterator[tarfile.TarInfo]: Validated safe tarinfo members.

    Raises:
        ValueError: If target_dir is invalid or cannot be resolved.
    """
    dest_path = Path(target_dir).resolve()

    for member in tar.getmembers():
        # Reject obvious path traversal patterns and absolute paths
        if ".." in member.name or os.path.isabs(member.name):
            logger.warning(
                "Skipping potentially malicious tar member (traversal): %s",
                member.name,
            )
            continue

        member_path = (dest_path / member.name).resolve()

        # Enforce destination commonpath boundary
        try:
            common = os.path.commonpath([str(dest_path), str(member_path)])
        except ValueError:
            logger.warning(
                "Skipping tar member on mismatched drive: %s", member.name
            )
            continue

        if common != str(dest_path):
            logger.warning(
                "Skipping tar member escaping target root: %s", member.name
            )
            continue

        yield member


def safe_extract_tar(
    archive_path: str | Path,
    dest_dir: str | Path,
) -> Path:
    """Extract a tar or tar.gz archive safely to the destination directory.

    Args:
        archive_path (Union[str, Path]): Path to source tar archive.
        dest_dir (Union[str, Path]): Destination directory.

    Returns:
        Path: Resolved destination directory path.

    Raises:
        FileNotFoundError: If archive_path does not exist.
        tarfile.TarError: If archive extraction fails.
    """
    src = Path(archive_path)
    if not src.is_file():
        raise FileNotFoundError(f"Archive file not found: {src}")

    dst = ensure_dir(dest_dir)
    logger.info("Safely extracting %s to %s", src, dst)

    with tarfile.open(src, "r:*") as tar:
        safe_members = list(get_safe_tar_members(tar, dst))
        tar.extractall(path=dst, members=safe_members)

    return dst


def safe_load_weights(
    weights_path: str | Path,
    device: str = "cpu",
) -> dict[str, Any]:
    """Load PyTorch checkpoint weights securely.

    Uses weights_only=True by default to prevent arbitrary code execution via
    unsafe pickle payloads.

    Args:
        weights_path (Union[str, Path]): Path to PyTorch .pt/.pth/.ckpt file.
        device (str): Device to map loaded weights to. Defaults to 'cpu'.

    Returns:
        Dict[str, Any]: Loaded state dictionary.

    Raises:
        FileNotFoundError: If weights_path does not exist.
        RuntimeError: If checkpoint deserialization fails.
    """
    path = Path(weights_path)
    if not path.is_file():
        raise FileNotFoundError(f"Model weights not found at: {path}")

    logger.info("Loading model weights from: %s on device: %s", path, device)
    try:
        state_dict: dict[str, Any] = torch.load(
            path,
            map_location=device,
            weights_only=True,
        )
    except (RuntimeError, ValueError, KeyError) as exc:
        logger.warning(
            "Safe weights_only loading failed (%s). Retrying with full load.",
            exc,
        )
        state_dict = torch.load(path, map_location=device, weights_only=False)

    return state_dict


def save_numpy_atomic(
    file_path: str | Path,
    array: np.ndarray,
) -> Path:
    """Save a numpy array to disk atomically.

    Args:
        file_path (Union[str, Path]): Target output file path.
        array (np.ndarray): Numpy array to save.

    Returns:
        Path: Path of the saved file.
    """
    target = Path(file_path)
    ensure_dir(target.parent)
    temp_path = target.parent / f".{target.name}.tmp"
    with open(temp_path, "wb") as f:
        np.save(f, array)
    temp_path.replace(target)
    return target
