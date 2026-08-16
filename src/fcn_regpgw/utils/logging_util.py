"""Logging configuration and utilities for FCN-RegPGW.

Provides structured module-level loggers complying with repo standards.
"""

import logging
import sys


def get_logger(
    name: str,
    level: int = logging.INFO,
    format_str: str | None = None,
) -> logging.Logger:
    """Retrieve or configure a standard logging.Logger instance.

    Args:
        name (str): Logger name, typically __name__.
        level (int): Logging severity level. Defaults to logging.INFO.
        format_str (Optional[str]): Custom formatter template.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = (
            format_str
            or "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
        )
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
