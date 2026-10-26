"""Turning one access log line into a ``LogEntry``."""

from datetime import datetime

from log_analyzer.decorators import cache
from log_analyzer.models import LogEntry
from log_analyzer.parsing.base import LogParser
from log_analyzer.patterns import LOG_FORMATS, TIMESTAMP_FORMAT
from log_analyzer.patterns.cleaning import mask_emails, normalize_whitespace
from log_analyzer.patterns.validators import is_valid_ip, is_valid_url

NO_VALUE = "-"  # what logs write for a missing size or referrer


@cache
def parse_timestamp(text: str) -> datetime:
    """Turn ``"21/Oct/2026:13:55:36 +0000"`` into a timezone-aware datetime.

    Cached: busy logs repeat the same second many times and ``strptime`` is
    slow. Invalid dates are not cached (the error is raised every time).

    Raises:
        ValueError: If the text does not follow ``TIMESTAMP_FORMAT``.
    """
    return datetime.strptime(text, TIMESTAMP_FORMAT)


def _optional(value: str | None) -> str | None:
    """Return ``None`` for a missing or ``-`` field, else the value."""
    return None if value in (None, NO_VALUE) else value


def _url_or_none(value: str | None) -> str | None:
    """Return the referrer when it is a real http(s) URL, else ``None``."""
    return value if value is not None and is_valid_url(value) else None


def parse_line(line: str) -> LogEntry | None:
    """Parse one log line in the combined or common format.

    Repeated spaces and the line break are cleaned first. Formats are tried
    from the most detailed (``LOG_FORMATS``), and the named groups of the
    first match become the entry's fields. The validators then check the
    values the regex only shaped: the IP must be real (each part 0–255), the
    referrer must be an http(s) URL, and emails in the URL are masked.

    Args:
        line: One raw line from an access log.

    Returns:
        The parsed entry, or ``None`` when no format matches, the IP is not
        valid or the date is invalid; this lets callers write
        ``filter(None, map(parse_line, lines))``.
    """
    cleaned = normalize_whitespace(line)
    for pattern in LOG_FORMATS:
        match = pattern.match(cleaned)
        if match is None:
            continue
        fields = match.groupdict()
        if not is_valid_ip(fields["ip"]):
            return None
        try:
            timestamp = parse_timestamp(fields["timestamp"])
        except ValueError:
            return None
        size = _optional(fields["size"])
        return LogEntry(
            ip=fields["ip"],
            timestamp=timestamp,
            method=fields["method"],
            url=mask_emails(fields["url"]),
            protocol=fields["protocol"],
            status=int(fields["status"]),
            size=None if size is None else int(size),
            referrer=_url_or_none(fields.get("referrer")),
            user_agent=_optional(fields.get("user_agent")),
        )
    return None


class ApacheLogParser(LogParser):
    """Parses the Apache/Nginx combined and common formats (``LOG_FORMATS``)."""

    def parse(self, line: str) -> LogEntry | None:
        """Parse one line with ``parse_line``; ``None`` for a bad line."""
        return parse_line(line)
