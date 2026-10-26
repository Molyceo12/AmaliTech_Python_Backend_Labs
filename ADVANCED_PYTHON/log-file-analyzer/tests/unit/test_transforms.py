"""Tests for the ``map()`` transform steps."""

from collections.abc import Iterator

from log_analyzer.pipeline import (
    parse_entries,
    to_record,
    to_records,
)
from tests.helpers import COMBINED_LINE, COMMON_LINE, make_entry


def test_parse_entries_drops_bad_lines() -> None:
    """Only lines that parse become entries, in their original order."""
    entries = list(parse_entries([COMBINED_LINE, "bad", "", COMMON_LINE]))
    assert [entry.ip for entry in entries] == ["192.168.1.10", "10.0.0.5"]


def test_parse_entries_is_lazy() -> None:
    """Nothing is parsed until the result is read."""
    read: list[str] = []

    def lines() -> Iterator[str]:
        for line in (COMBINED_LINE, COMMON_LINE):
            read.append(line)
            yield line

    entries = parse_entries(lines())
    assert not read
    next(entries)
    assert read == [COMBINED_LINE]


def test_to_record_gives_a_plain_dict() -> None:
    """An entry becomes a JSON-ready dict with an ISO timestamp."""
    record = to_record(make_entry(404, size=None))
    assert record == {
        "ip": "192.168.1.10",
        "timestamp": "2026-10-21T13:55:36+00:00",
        "method": "GET",
        "url": "/index.html",
        "protocol": "HTTP/1.1",
        "status": 404,
        "size": None,
        "referrer": None,
        "user_agent": None,
    }


def test_to_records_maps_every_entry() -> None:
    """One record per entry."""
    records = list(to_records([make_entry(200), make_entry(500)]))
    assert [record["status"] for record in records] == [200, 500]
