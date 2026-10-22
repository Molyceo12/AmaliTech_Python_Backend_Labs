"""Parsing log lines: the parser interface and its regex implementation."""

from log_analyzer.parsing.base import LogParser
from log_analyzer.parsing.parser import (
    ApacheLogParser,
    parse_line,
    parse_line_strict,
    parse_timestamp,
)

__all__ = [
    "ApacheLogParser",
    "LogParser",
    "parse_line",
    "parse_line_strict",
    "parse_timestamp",
]
