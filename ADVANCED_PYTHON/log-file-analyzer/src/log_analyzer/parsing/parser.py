"""Turning one access log line into a ``LogEntry``."""

from datetime import datetime

from log_analyzer.exceptions import LogParseError
from log_analyzer.models import LogEntry
from log_analyzer.patterns import LOG_FORMATS, TIMESTAMP_FORMAT
from log_analyzer.patterns.cleaning import normalize_whitespace

NO_VALUE = "-"  # what logs write for a missing size or referrer


def parse_timestamp(text: str) -> datetime:
    """Turn ``"21/Oct/2026:13:55:36 +0000"`` into a timezone-aware datetime.

    Raises:
        ValueError: If the text does not follow ``TIMESTAMP_FORMAT``.
    """
    return datetime.strptime(text, TIMESTAMP_FORMAT)


def _optional(value: str | None) -> str | None:
    """Return ``None`` for a missing or ``-`` field, else the value."""
    return None if value in (None, NO_VALUE) else value


def parse_line(line: str) -> LogEntry | None:
    """Parse one log line in the combined or common format.

    Repeated spaces and the line break are cleaned first. Formats are tried
    from the most detailed (``LOG_FORMATS``), and the named groups of the
    first match become the entry's fields.

    Args:
        line: One raw line from an access log.

    Returns:
        The parsed entry, or ``None`` when no format matches or the date is
        invalid; this lets callers write ``filter(None, map(parse_line, lines))``.
    """
    cleaned = normalize_whitespace(line)
    for pattern in LOG_FORMATS:
        match = pattern.match(cleaned)
        if match is None:
            continue
        fields = match.groupdict()
        try:
            timestamp = parse_timestamp(fields["timestamp"])
        except ValueError:
            return None
        size = _optional(fields["size"])
        return LogEntry(
            ip=fields["ip"],
            timestamp=timestamp,
            method=fields["method"],
            url=fields["url"],
            protocol=fields["protocol"],
            status=int(fields["status"]),
            size=None if size is None else int(size),
            referrer=_optional(fields.get("referrer")),
            user_agent=_optional(fields.get("user_agent")),
        )
    return None


def parse_line_strict(line: str, line_number: int) -> LogEntry:
    """Parse one log line and raise an error instead of returning ``None``.

    Args:
        line: One raw line from an access log.
        line_number: Line of the entry in its file (for the error message).

    Raises:
        LogParseError: If the line is not a valid common or combined log line.
    """
    entry = parse_line(line)
    if entry is None:
        raise LogParseError(
            line_number, "does not match the common or combined log format"
        )
    return entry
