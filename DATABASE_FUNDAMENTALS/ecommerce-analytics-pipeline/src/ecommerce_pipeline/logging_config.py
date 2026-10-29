"""Where the pipeline's log messages go: a log file, and the terminal.

Every module logs with ``logging.getLogger(__name__)``, so all loggers sit
under the ``ecommerce_pipeline`` package logger configured here.
"""

import logging
import sys
from pathlib import Path

from ecommerce_pipeline.exceptions import LogSetupError

PACKAGE_LOGGER = "ecommerce_pipeline"
DEFAULT_LOG_FILE = Path("output/ecommerce.log")
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_OURS = "_ecommerce_handler"  # marks the handlers this module added


def configure_logging(
    log_file: str | Path = DEFAULT_LOG_FILE, verbose: bool = False
) -> Path:
    """Send every level to ``log_file`` and warnings (or everything) to stderr.

    Calling it again replaces the handlers it added before, so nothing is
    logged twice.

    Returns:
        The log file path.

    Raises:
        LogSetupError: If the log file or its folder cannot be created.
    """
    path = Path(log_file)
    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.setLevel(logging.DEBUG)
    for handler in list(logger.handlers):
        if getattr(handler, _OURS, False):
            logger.removeHandler(handler)
            handler.close()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
    except OSError as error:
        raise LogSetupError(f"Cannot write log file {path}: {error}") from error

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    for handler in (file_handler, console_handler):
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        setattr(handler, _OURS, True)
        logger.addHandler(handler)
    return path
