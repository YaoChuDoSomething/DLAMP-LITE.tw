import logging
import tarfile
from pathlib import Path

from dlamp.runtime_config import get_runtime_config

logging.basicConfig(
    filename=Path(__file__).parent.resolve() / "unzip.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("dev")


def main():
    logger.info("start to unzip")

    config = get_runtime_config()
    file_dir = config.data_path
    tar_gz_files = sorted(file_dir.glob("*.tar.gz"))

    for tar_gz_file in tar_gz_files:
        # new dir
        new_dir_name = tar_gz_file.name.split(".")[0]
        new_dir = Path(tar_gz_file.parent / new_dir_name)
        new_dir.mkdir(parents=True, exist_ok=True)

        # extraction
        tar_gz_file = str(tar_gz_file)
        new_dir = str(new_dir)
        try:
            if tar_gz_file.endswith("tar.gz"):
                with tarfile.open(tar_gz_file, "r:gz") as tar:
                    tar.extractall(new_dir)
            elif tar_gz_file.endswith("tar"):
                with tarfile.open(tar_gz_file, "r:") as tar:
                    tar.extractall(new_dir)
        except Exception as e:  # noqa: BLE001 - broad error boundary on archive extraction
            logger.error(e)

        # done
        logger.info(f"{tar_gz_file} has been extracted to {new_dir}")


def move_files():
    config = get_runtime_config()
    file_dir = config.data_path
    target_subdir = ["rwf_202005-06", "rwf_202105-06"]

    for subdir in target_subdir:
        subdir = file_dir / subdir

        for file in subdir.iterdir():
            new_dir = file_dir / f"rwf_{file.name[:6]}"
            if not new_dir.exists():
                new_dir.mkdir(parents=True, exist_ok=True)

            # move file to new dir
            file.rename(new_dir / file.name)

        logger.info("%s has been moved to %s", subdir, new_dir)


if __name__ == "__main__":
    main()
