from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class RuntimeConfigError(Exception):
    """Raised when the runtime config fails validation."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime config driven by environment variables.

    Model code, data source, data path, and derived paths are all
    validated at construction time so that a mismatch of
    ``DLAMP_EXP_CODE`` fails loudly at startup rather than silently
    loading the wrong standardization.

    Constants set by the constructor are used in the same way as the
    previous module-level defaults but are explicitly validated.

    The singleton is threaded through the entrypoints and the
    deepened module layer. Callers that cannot use a constructor pass
    should call ``get_runtime_config()`` to retrieve the current
    singleton.
    """

    model_code: str
    data_source: str
    data_path: Path
    standardization_path: Path
    data_config_path: Path
    var_suffix: str = "WE01H0202500"

    @classmethod
    def from_env(cls) -> RuntimeConfig:
        """Build ``RuntimeConfig`` from environment variables with
        eager validation of the required files.

        Raises ``RuntimeConfigError`` when ``DLAMP_EXP_CODE`` points to
        a model version that has no matching *standardization* or *data
        config* files on disk.
        """
        model_code = os.environ.get("DLAMP_EXP_CODE", "20250627")
        data_source = os.environ.get("DLAMP_DATA_SOURCE", "OP_ERA5")
        data_path = Path(os.environ.get("DLAMP_DATA_PATH", "/wk2/yaochu/CASE_DATA/Pool/"))

        from dlamp.const import REPO_ROOT

        standardization_path = REPO_ROOT / "assets" / "standardization" / f"z_score_3h_{model_code}.json"
        data_config_path = REPO_ROOT / "config" / "data" / f"rwrf_{model_code}.yaml"

        missing = []
        if not standardization_path.exists():
            missing.append(f"standardization: {standardization_path}")
        if not data_config_path.exists():
            missing.append(f"data config: {data_config_path}")

        if missing:
            raise RuntimeConfigError(
                f"DLAMP_EXP_CODE '{model_code}' requires:\n" + "\n".join(f"  {m} [NOT FOUND]" for m in missing)
            )

        return cls(
            model_code=model_code,
            data_source=data_source,
            data_path=data_path,
            standardization_path=standardization_path,
            data_config_path=data_config_path,
        )

    @property
    def standardization_json_path(self) -> Path:
        return self.standardization_path


_singleton: RuntimeConfig | None = None


def get_runtime_config() -> RuntimeConfig:
    """Return (or construct) the singleton RuntimeConfig for the current
    process. The config is built lazily: the first call to
    ``get_runtime_config()`` performs env-var reading, path construction,
    and file existence validation. Subsequent calls reuse the cached instance.

    .. note:: If multiple entrypoints are run in the same process
              (e.g. tests), the last call wins.
    """
    global _singleton
    if _singleton is None:
        _singleton = RuntimeConfig.from_env()
    return _singleton


def get_runtime_config_error() -> str | None:
    """Return the last validation error raised by
    ``RuntimeConfig.from_env()``. Only has a value after a failed
    instantiation."""
    return getattr(get_runtime_config, "_last_error", None)
