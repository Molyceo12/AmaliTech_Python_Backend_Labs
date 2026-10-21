"""Transform steps built with ``map()``: lines → entries → records.

Every function returns a lazy iterator, so nothing is processed until the
result is read.
"""

import dataclasses
from collections.abc import Iterable, Iterator

from log_analyzer.models import LogEntry, LogRecord
from log_analyzer.parsing import parse_line
from log_analyzer.patterns.cleaning import strip_query_string


def parse_entries(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Parse every line and keep only the valid entries.

    ``map`` parses each line (``None`` for a bad one) and ``filter(None, ...)``
    drops the ``None`` results.
    """
    return filter(None, map(parse_line, lines))


def clean_url(entry: LogEntry) -> LogEntry:
    """Return a copy of ``entry`` without the URL's query string.

    Entries are frozen, so ``dataclasses.replace`` builds a new one.
    """
    return dataclasses.replace(entry, url=strip_query_string(entry.url))


def clean_urls(entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
    """Remove the query string from every entry's URL."""
    return map(clean_url, entries)


def to_record(entry: LogEntry) -> LogRecord:
    """Turn an entry into a plain dict, with the timestamp as ISO text."""
    return {
        "ip": entry.ip,
        "timestamp": entry.timestamp.isoformat(),
        "method": entry.method,
        "url": entry.url,
        "protocol": entry.protocol,
        "status": entry.status,
        "size": entry.size,
        "referrer": entry.referrer,
        "user_agent": entry.user_agent,
    }


def to_records(entries: Iterable[LogEntry]) -> Iterator[LogRecord]:
    """Turn every entry into a plain dict."""
    return map(to_record, entries)
