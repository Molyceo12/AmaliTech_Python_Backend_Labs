"""Writing reports: the writer interface and its JSON implementation."""

from grade_analytics.writers.base import ReportWriter
from grade_analytics.writers.json_writer import JsonReportWriter

__all__ = ["JsonReportWriter", "ReportWriter"]
