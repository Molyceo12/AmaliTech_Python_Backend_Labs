"""Tests for parsing log lines into ``LogEntry`` objects."""

import pytest

from log_analyzer.models import LogEntry
from log_analyzer.parsing import parse_line, parse_timestamp
from tests.helpers import COMBINED_LINE, COMMON_LINE, TIMESTAMP


def test_parse_timestamp_keeps_the_timezone() -> None:
    """The log timestamp becomes a timezone-aware datetime."""
    assert parse_timestamp("21/Oct/2026:13:55:36 +0000") == TIMESTAMP


def test_combined_line_becomes_a_full_entry() -> None:
    """Every field is converted to its type: int status/size, datetime time."""
    assert parse_line(COMBINED_LINE) == LogEntry(
        ip="192.168.1.10",
        timestamp=TIMESTAMP,
        method="GET",
        url="/index.html?page=2",
        protocol="HTTP/1.1",
        status=200,
        size=2326,
        referrer="https://example.com/",
        user_agent="Mozilla/5.0 (X11; Linux x86_64)",
    )


def test_common_line_has_no_size_referrer_or_agent() -> None:
    """``-`` size becomes ``None``; the common format has no referrer or agent."""
    entry = parse_line(COMMON_LINE)
    assert entry is not None
    assert entry.status == 302
    assert entry.size is None
    assert entry.referrer is None
    assert entry.user_agent is None


def test_dash_referrer_becomes_none() -> None:
    """A ``"-"`` referrer means there was none."""
    line = COMBINED_LINE.replace('"https://example.com/"', '"-"')
    entry = parse_line(line)
    assert entry is not None
    assert entry.referrer is None


@pytest.mark.parametrize("ip", ["999.1.1.1", "256.0.0.1", "192.168.01.10"])
def test_line_with_an_invalid_ip_gives_none(ip: str) -> None:
    """``is_valid_ip`` rejects IPs the loose log regex lets through."""
    assert parse_line(COMBINED_LINE.replace("192.168.1.10", ip)) is None


@pytest.mark.parametrize("referrer", ["not-a-url", "ftp://example.com/"])
def test_referrer_that_is_not_an_http_url_becomes_none(referrer: str) -> None:
    """``is_valid_url`` keeps only http(s) referrers; the line itself is kept."""
    line = COMBINED_LINE.replace("https://example.com/", referrer)
    entry = parse_line(line)
    assert entry is not None
    assert entry.referrer is None


def test_email_in_the_url_is_masked() -> None:
    """Emails in the path or query string never reach the report."""
    line = COMBINED_LINE.replace("/index.html?page=2", "/reset?email=ann@mail.com")
    entry = parse_line(line)
    assert entry is not None
    assert entry.url == "/reset?email=***@***"


def test_messy_whitespace_is_cleaned_before_matching() -> None:
    """Extra spaces, tabs and the line break do not stop a match."""
    messy = "  " + COMMON_LINE.replace(" ", "  ").replace("  [", "\t[") + "\n"
    assert parse_line(messy) == parse_line(COMMON_LINE)


@pytest.mark.parametrize(
    "line",
    [
        COMMON_LINE.replace("21/Oct", "32/Oct"),
        COMMON_LINE.replace("Oct", "Foo"),
        "not a log line",
        "",
    ],
    ids=["day 32", "bad month", "text", "empty"],
)
def test_bad_lines_give_none(line: str) -> None:
    """Lines that do not match, or have an impossible date, return ``None``."""
    assert parse_line(line) is None


def test_parse_line_works_with_filter_and_map() -> None:
    """``filter(None, map(parse_line, lines))`` keeps only the good entries."""
    entries = list(filter(None, map(parse_line, [COMBINED_LINE, "bad", COMMON_LINE])))
    assert [entry.ip for entry in entries] == ["192.168.1.10", "10.0.0.5"]
