"""Tests for parsing log lines into ``LogEntry`` objects."""

import pytest

from log_analyzer.exceptions import LogParseError
from log_analyzer.models import LogEntry
from log_analyzer.parsing import parse_line, parse_line_strict, parse_timestamp
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


def test_strict_parser_returns_the_entry() -> None:
    """Good lines parse the same way as ``parse_line``."""
    assert parse_line_strict(COMMON_LINE, 1) == parse_line(COMMON_LINE)


def test_strict_parser_raises_with_the_line_number() -> None:
    """Bad lines raise ``LogParseError`` naming the line."""
    with pytest.raises(LogParseError, match="Line 7: does not match") as error:
        parse_line_strict("bad line", 7)
    assert error.value.line_number == 7
