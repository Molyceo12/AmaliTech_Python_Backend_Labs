"""Sample log lines and builders shared by the tests."""

from datetime import UTC, datetime
from pathlib import Path

from log_analyzer.models import LogEntry

DATA = Path(__file__).resolve().parents[1] / "data"

COMBINED_LINE = (
    '192.168.1.10 - - [21/Oct/2026:13:55:36 +0000] "GET /index.html?page=2 HTTP/1.1" '
    '200 2326 "https://example.com/" "Mozilla/5.0 (X11; Linux x86_64)"'
)
COMMON_LINE = (
    '10.0.0.5 - frank [21/Oct/2026:09:05:00 +0000] "POST /login HTTP/1.0" 302 -'
)
TIMESTAMP = datetime(2026, 10, 21, 13, 55, 36, tzinfo=UTC)


def make_entry(status: int = 200, timestamp: datetime = TIMESTAMP) -> LogEntry:
    """Return a simple GET entry with the given status and time."""
    return LogEntry(
        ip="192.168.1.10",
        timestamp=timestamp,
        method="GET",
        url="/index.html",
        protocol="HTTP/1.1",
        status=status,
        size=512,
    )
