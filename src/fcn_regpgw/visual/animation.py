"""Forecast animation compilation and video export utilities for FCN-RegPGW.

Assembles sequentially generated forecast plot frames into MP4 or GIF videos.
"""

import re
from collections.abc import Sequence
from pathlib import Path

from fcn_regpgw.utils.file_util import ensure_dir
from fcn_regpgw.utils.logging_util import get_logger

logger = get_logger(__name__)


def natural_sort_key(path: Path) -> int:
    """Extract first numeric integer from filename for natural sorting.

    Args:
        path (Path): File path.

    Returns:
        int: Extracted lead hour number, or 0 if not found.
    """
    match = re.search(r"(\d+)", path.name)
    return int(match.group(1)) if match else 0


class AnimationExporter:
    """Assembles image sequences into forecast video animations."""

    @staticmethod
    def export_video(
        image_paths: Sequence[str | Path],
        output_video_path: str | Path,
        fps: int = 2,
    ) -> Path:
        """Compile a sequence of PNG frames into an MP4 or GIF video.

        Args:
            image_paths (Sequence[Union[str, Path]]): Sequence of image paths.
            output_video_path (Union[str, Path]): Destination video path.
            fps (int): Playback frame rate in frames per second.

        Returns:
            Path: Resolved path to the exported video file.

        Raises:
            ValueError: If image_paths list is empty.
            ImportError: If imageio is not available.
        """
        paths = [Path(p) for p in image_paths if Path(p).is_file()]
        if not paths:
            raise ValueError("No valid image files provided for video export.")

        sorted_paths = sorted(paths, key=natural_sort_key)
        out_path = Path(output_video_path)
        ensure_dir(out_path.parent)

        logger.info(
            "Compiling %d image frames to video %s at %d fps",
            len(sorted_paths),
            out_path,
            fps,
        )

        try:
            import imageio.v2 as imageio  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "imageio package is required for video compilation."
            ) from exc

        with imageio.get_writer(str(out_path), fps=fps) as writer:
            for p in sorted_paths:
                frame = imageio.imread(str(p))
                writer.append_data(frame)

        logger.info("Successfully exported forecast video to %s", out_path)
        return out_path
