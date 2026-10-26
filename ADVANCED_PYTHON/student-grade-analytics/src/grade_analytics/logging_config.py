"""Logging setup: one rotating log file for the whole ``grade_analytics`` package.

Only the command line calls ``setup_logging``; every other module just uses
``logging.getLogger(__name__)``.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

PACKAGE_LOGGER = "grade_analytics"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
MAX_BYTES = 1_000_000  # rotate after about 1 MB
BACKUP_COUNT = 3  # keep app.log.1 … app.log.3


def setup_logging(log_file: Path, level: str = "INFO") -> Optional[Path]:
    """Send the package's log records to a rotating file.

    Calling it again replaces the previous file handler, so lines are never
    written twice. If the file cannot be opened, a warning is printed and
    the run continues without a log file.

    Args:
        log_file: File to write (its folder is created if missing).
        level: Lowest level written, one of ``LOG_LEVELS``.

    Returns:
        The log file, or ``None`` if it could not be opened.
    """
    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.setLevel(level)
    for handler in logger.handlers[:]:
        if not isinstance(handler, logging.NullHandler):
            logger.removeHandler(handler)
            handler.close()
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
    except OSError as error:
        print(f"Warning: cannot write log file {log_file}: {error}", file=sys.stderr)
        return None
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    return log_file
