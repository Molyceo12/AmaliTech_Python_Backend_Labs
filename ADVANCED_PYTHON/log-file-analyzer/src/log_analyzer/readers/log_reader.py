"""Reading log files lazily with generators.

The files are read one line at a time, so even a huge log never has to fit
in memory.
"""

import logging
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from itertools import chain
from pathlib import Path
from typing import TextIO

from log_analyzer.exceptions import (
    LogFileError,
    LogFileNotFoundError,
    LogFilePermissionError,
)
from log_analyzer.readers.base import LogReader

logger = logging.getLogger(__name__)


@contextmanager
def open_log(path: str | Path) -> Iterator[TextIO]:
    """Open a log file for reading and always close it afterwards.

    Undecodable bytes are replaced instead of stopping the whole run.

    Raises:
        LogFileNotFoundError: If the file does not exist.
        LogFilePermissionError: If there is no permission to read it.
        LogFileError: If it cannot be opened for another reason (e.g. a folder).
    """
    log_path = Path(path)
    try:
        handle = log_path.open(encoding="utf-8", errors="replace")
    except FileNotFoundError as error:
        raise LogFileNotFoundError(f"Log file not found: {log_path}") from error
    except PermissionError as error:
        raise LogFilePermissionError(
            f"No permission to read log file: {log_path}"
        ) from error
    except OSError as error:
        raise LogFileError(f"Cannot open log file {log_path}: {error}") from error
    logger.debug("Opened log file %s", log_path)
    try:
        with handle:
            yield handle
    finally:  # also runs when a reader stops early
        logger.debug("Closed log file %s", log_path)


def read_lines(path: str | Path) -> Iterator[str]:
    """Yield the lines of a log file one at a time, without the line break.

    This is a generator: nothing is opened until the first line is asked for,
    so a missing file raises its error on the first ``next()``.

    Raises:
        LogFileError: If the file cannot be opened (see ``open_log``).
    """
    with open_log(path) as handle:
        for line in handle:
            yield line.rstrip("\r\n")


def read_many(paths: Iterable[str | Path]) -> Iterator[str]:
    """Yield the lines of several log files as one stream, file after file.

    ``itertools.chain`` joins the per-file generators without reading ahead.
    """
    return chain.from_iterable(map(read_lines, paths))


class FileLogReader(LogReader):
    """Reads plain-text log files with generators (``read_many``)."""

    def read(self, paths: Iterable[str | Path]) -> Iterator[str]:
        """Yield the lines of every file, one at a time, file after file.

        Raises:
            LogFileError: If a file cannot be opened (see ``open_log``).
        """
        return read_many(paths)
