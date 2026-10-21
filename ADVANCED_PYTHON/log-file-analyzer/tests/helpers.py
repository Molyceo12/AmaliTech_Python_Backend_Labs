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


def make_entry(  # pylint: disable=too-many-arguments
    status: int = 200,
    timestamp: datetime = TIMESTAMP,
    *,
    method: str = "GET",
    ip: str = "192.168.1.10",
    url: str = "/index.html",
    size: int | None = 512,
) -> LogEntry:
    """Return an entry; by default a GET of ``/index.html`` with status 200."""
    return LogEntry(
        ip=ip,
        timestamp=timestamp,
        method=method,
        url=url,
        protocol="HTTP/1.1",
        status=status,
        size=size,
    )


# Five small entries with known totals, used by the pipeline tests.
SAMPLE_ENTRIES = [
    make_entry(200, ip="10.0.0.1", url="/", size=100),
    make_entry(200, ip="10.0.0.1", url="/about", size=200),
    make_entry(404, ip="10.0.0.2", url="/missing", size=None),
    make_entry(500, method="POST", ip="10.0.0.3", url="/api", size=50),
    make_entry(302, method="POST", ip="10.0.0.1", url="/login", size=0),
]
