from __future__ import annotations

import logging

from ._version import __version__

logging.getLogger(__name__).addHandler(logging.NullHandler())

LOGGER_FORMAT = "[{levelname}: {filename}:{lineno}]: {message}"


def start_logging(
    level: int | str = logging.DEBUG,
    fmt: str = LOGGER_FORMAT,
) -> logging.Handler:
    """
    Start logging activity.

    Adapted from urllib3/__init__.py
    """
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=fmt, style="{"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug("Logging enabled for %s", __name__)

    return handler


from ._ext import setup  # noqa: E402,TCH001

__all__ = ["setup", "__version__"]
