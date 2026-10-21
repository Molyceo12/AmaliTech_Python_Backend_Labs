"""Typed structure of the report data (``TypedDict``)."""

from typing import TypedDict


class LogRecord(TypedDict):
    """One log entry as a plain dict, ready for JSON."""

    ip: str
    timestamp: str  # ISO 8601, e.g. "2026-10-21T13:55:36+00:00"
    method: str
    url: str
    protocol: str
    status: int
    size: int | None
    referrer: str | None
    user_agent: str | None


class CountItem(TypedDict):
    """One row of a "top" list, e.g. the busiest IPs."""

    name: str
    count: int


class LogSummary(TypedDict):
    """Totals and counts for a set of log entries."""

    total_requests: int
    total_bytes: int
    error_count: int
    error_rate: float  # percentage of 4xx/5xx responses, 1 decimal
    requests_per_status: dict[str, int]
    requests_per_method: dict[str, int]
    top_ips: list[CountItem]
    top_urls: list[CountItem]
    unique_urls: int


class PageSection(TypedDict):
    """One page of the selected entries."""

    number: int
    per_page: int
    entries: list[LogRecord]


class LogReport(TypedDict):
    """The full report written to JSON."""

    files: list[str]
    total_lines: int
    parsed_lines: int
    skipped_lines: int
    filters: dict[str, str]
    summary: LogSummary
    requests_per_hour: dict[str, int]
    errors_by_status: dict[str, int]
    page: PageSection
