"""Where the tool's own log messages go: a log file, and the terminal with ``-v``.

Every module logs with ``logging.getLogger(__name__)``, so all loggers sit
under the ``log_analyzer`` package logger configured here.
"""

import logging
import sys
from pathlib import Path

from log_analyzer.exceptions import LogAnalyzerError

PACKAGE_LOGGER = "log_analyzer"
DEFAULT_LOG_FILE = Path("output/log-analyzer.log")
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
_OURS = "_log_analyzer_handler"  # marks the handlers this module added
# Pass ``extra={SHOWN_TO_USER: True}`` for a message the CLI already prints
# itself: it still goes to the file, but is not repeated in the terminal.
SHOWN_TO_USER = "shown_to_user"


def _not_shown_yet(record: logging.LogRecord) -> bool:
    """Console filter: skip records the CLI already printed for the user."""
    return not getattr(record, SHOWN_TO_USER, False)


class LogSetupError(LogAnalyzerError):
    """The log file cannot be opened."""


def _remove_our_handlers(logger: logging.Logger) -> None:
    """Close the handlers a previous call added, so runs never log twice."""
    for handler in list(logger.handlers):
        if getattr(handler, _OURS, False):
            logger.removeHandler(handler)
            handler.close()


def configure_logging(
    log_file: str | Path = DEFAULT_LOG_FILE, verbose: bool = False
) -> Path:
    """Send every level to ``log_file`` and warnings (or everything) to stderr.

    The file always gets DEBUG and up, with a timestamp, and is appended to
    on each run. The terminal shows only WARNING and up, or everything with
    ``verbose``, so the bordered boxes stay clean.

    Returns:
        The log file path.

    Raises:
        LogSetupError: If the log file or its folder cannot be created.
    """
    path = Path(log_file)
    logger = logging.getLogger(PACKAGE_LOGGER)
    logger.setLevel(logging.DEBUG)
    _remove_our_handlers(logger)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
    except OSError as error:
        raise LogSetupError(f"Cannot write log file {path}: {error}") from error

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    console_handler.addFilter(_not_shown_yet)
    for handler in (file_handler, console_handler):
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        setattr(handler, _OURS, True)
        logger.addHandler(handler)
    return path
