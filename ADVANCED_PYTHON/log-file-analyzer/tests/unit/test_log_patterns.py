"""Tests for the compiled log format patterns and their named groups."""

import pytest

from log_analyzer.patterns import COMBINED_LOG, COMMON_LOG, LOG_FORMATS
from tests.helpers import COMBINED_LINE, COMMON_LINE


def test_combined_pattern_captures_every_named_group() -> None:
    """A combined line gives all nine fields by name."""
    match = COMBINED_LOG.match(COMBINED_LINE)
    assert match is not None
    assert match.groupdict() == {
        "ip": "192.168.1.10",
        "timestamp": "21/Oct/2026:13:55:36 +0000",
        "method": "GET",
        "url": "/index.html?page=2",
        "protocol": "HTTP/1.1",
        "status": "200",
        "size": "2326",
        "referrer": "https://example.com/",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }


def test_common_pattern_captures_the_shared_fields() -> None:
    """A common line gives the seven shared fields; ``-`` size is kept as text."""
    match = COMMON_LOG.match(COMMON_LINE)
    assert match is not None
    assert match["ip"] == "10.0.0.5"
    assert match["method"] == "POST"
    assert match["status"] == "302"
    assert match["size"] == "-"


def test_each_pattern_matches_only_its_own_format() -> None:
    """Combined needs the two quoted extras; common must end after the size."""
    assert COMBINED_LOG.match(COMMON_LINE) is None
    assert COMMON_LOG.match(COMBINED_LINE) is None


def test_combined_format_is_tried_first() -> None:
    """The most detailed format comes first in ``LOG_FORMATS``."""
    assert LOG_FORMATS == (COMBINED_LOG, COMMON_LOG)


@pytest.mark.parametrize(
    "line",
    [
        '1.2.3.4 - - [21/Oct/2026:13:55:36 +0000] "GET / HTTP/1.1" 2000 10',
        '1.2.3.4 - - [21/Oct/2026:13:55:36 +0000] "GET / HTTP/1.1" 20 10',
        '1.2.3.4 - - 21/Oct/2026:13:55:36 +0000 "GET / HTTP/1.1" 200 10',
        "1.2.3.4 - - [21/Oct/2026:13:55:36 +0000] GET / HTTP/1.1 200 10",
        '1.2.3.4 - - [21/Oct/2026:13:55:36 +0000] "get / HTTP/1.1" 200 10',
        'host.example - - [21/Oct/2026:13:55:36 +0000] "GET / HTTP/1.1" 200 10',
        "not a log line",
        "",
    ],
    ids=[
        "4-digit status",
        "2-digit status",
        "no brackets",
        "no quotes",
        "lowercase method",
        "hostname not ip",
        "text",
        "empty",
    ],
)
def test_bad_lines_match_no_format(line: str) -> None:
    """Broken lines are rejected by every pattern."""
    assert all(pattern.match(line) is None for pattern in LOG_FORMATS)
