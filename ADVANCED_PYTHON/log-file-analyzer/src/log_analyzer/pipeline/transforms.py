"""Transform steps built with ``map()``: lines → entries → records.

Every function returns a lazy iterator, so nothing is processed until the
result is read.
"""

from collections.abc import Iterable, Iterator

from log_analyzer.models import LogEntry, LogRecord
from log_analyzer.parsing import parse_line


def parse_entries(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Parse every line and keep only the valid entries.

    ``map`` parses each line (``None`` for a bad one) and ``filter(None, ...)``
    drops the ``None`` results.
    """
    return filter(None, map(parse_line, lines))


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
