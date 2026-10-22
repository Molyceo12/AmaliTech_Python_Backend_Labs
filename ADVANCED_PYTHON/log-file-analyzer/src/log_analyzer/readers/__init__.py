"""Reading log files: the reader interface, generators and batching."""

from log_analyzer.readers.base import LogReader
from log_analyzer.readers.batching import Batches
from log_analyzer.readers.log_reader import (
    FileLogReader,
    open_log,
    read_lines,
    read_many,
)

__all__ = [
    "Batches",
    "FileLogReader",
    "LogReader",
    "open_log",
    "read_lines",
    "read_many",
]
