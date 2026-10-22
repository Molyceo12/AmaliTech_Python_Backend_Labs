"""Writing reports: the writer interface and its JSON implementation."""

from log_analyzer.writers.base import ReportWriter
from log_analyzer.writers.json_writer import JsonReportWriter

__all__ = ["JsonReportWriter", "ReportWriter"]
