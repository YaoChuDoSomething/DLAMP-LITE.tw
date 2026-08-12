# analysis/video_creator.py
"""Provides functionality to create MP4 videos from a sequence of images."""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def create_animation(
    image_paths: list[Path], output_video_path: Path, framerate: int = 1
) -> bool:
    """Creates an MP4 video from a list of image files using ffmpeg.

    Args:
        image_paths (List[Path]): A sorted list of paths to the input images.
        output_video_path (Path): The path to save the output MP4 file.
        framerate (int): The frame rate for the video. Defaults to 1.

    Returns:
        bool: True if the video was created successfully, False otherwise.
    """
    if not image_paths:
        logger.warning("No image paths provided to create_animation. Skipping.")
        return False

    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        logger.warning(
            "ffmpeg not found. Cannot create video. Please install ffmpeg."
        )
        return False

    # Sort paths to ensure correct order in the video
    sorted_paths = sorted(image_paths)

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt"
    ) as tmpfile:
        for img_path in sorted_paths:
            # Use resolve() to get an absolute path for ffmpeg
            tmpfile.write(f"file '{img_path.resolve()}'\n")
        temp_list_path = tmpfile.name

    command = [
        ffmpeg_path,
        "-y",  # Overwrite output file if it exists
        "-r", str(framerate),
        "-f", "concat",
        "-safe", "0",
        "-i", temp_list_path,
        "-c:v", "libx264",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-pix_fmt", "yuv420p",
        str(output_video_path),
    ]

    try:
        logger.info("Creating animation at %s", output_video_path)
        process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        logger.info("ffmpeg stdout:\n%s", process.stdout)
        logger.info("Animation created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("ffmpeg failed to create video.")
        logger.error("ffmpeg stderr:\n%s", e.stderr)
        return False
    finally:
        # Clean up the temporary file
        Path(temp_list_path).unlink()
