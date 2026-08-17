"""Unit tests for file utilities and secure tar extraction."""

import io
import tarfile
from pathlib import Path

import numpy as np
import torch

from fcn_regpgw.utils.file_util import (
    get_safe_tar_members,
    safe_extract_tar,
    safe_load_weights,
    save_numpy_atomic,
)


def test_safe_tar_members_rejects_traversal(tmp_path: Path) -> None:
    """Verify that get_safe_tar_members skips relative parent and absolute paths."""
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w") as tar:
        # Safe member
        info_safe = tarfile.TarInfo(name="model_weight/model.pt")
        info_safe.size = 5
        tar.addfile(info_safe, io.BytesIO(b"dummy"))

        # Path traversal member
        info_evil = tarfile.TarInfo(name="../evil.txt")
        info_evil.size = 5
        tar.addfile(info_evil, io.BytesIO(b"evil!"))

        # Absolute path member
        info_abs = tarfile.TarInfo(name="/tmp/abs.txt")
        info_abs.size = 5
        tar.addfile(info_abs, io.BytesIO(b"evil!"))

    tar_bytes.seek(0)
    with tarfile.open(fileobj=tar_bytes, mode="r") as tar:
        safe_members = list(get_safe_tar_members(tar, tmp_path))
        names = [m.name for m in safe_members]
        assert "model_weight/model.pt" in names
        assert "../evil.txt" not in names
        assert "/tmp/abs.txt" not in names


def test_safe_extract_tar(tmp_path: Path) -> None:
    """Verify safe extraction creates expected files without error."""
    archive_file = tmp_path / "test.tar"
    dest_dir = tmp_path / "extracted"

    with tarfile.open(archive_file, "w") as tar:
        info = tarfile.TarInfo(name="test_file.txt")
        content = b"sample content"
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))

    safe_extract_tar(archive_file, dest_dir)
    assert (dest_dir / "test_file.txt").is_file()
    assert (dest_dir / "test_file.txt").read_bytes() == b"sample content"


def test_safe_load_weights(tmp_path: Path) -> None:
    """Verify safe PyTorch weight loading with weights_only=True."""
    weights_path = tmp_path / "test_model.pt"
    dummy_dict = {"weight": torch.randn(4, 4), "bias": torch.zeros(4)}
    torch.save(dummy_dict, weights_path)

    loaded = safe_load_weights(weights_path, device="cpu")
    assert "weight" in loaded
    assert torch.equal(loaded["bias"], torch.zeros(4))


def test_save_numpy_atomic(tmp_path: Path) -> None:
    """Verify atomic numpy array save."""
    target_path = tmp_path / "sub" / "array.npy"
    arr = np.ones((5, 5), dtype=np.float32)
    save_numpy_atomic(target_path, arr)

    assert target_path.is_file()
    loaded = np.load(target_path)
    assert np.array_equal(arr, loaded)
