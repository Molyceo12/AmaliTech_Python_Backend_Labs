"""Tests for the itertools helpers: groupby, islice, takewhile."""

from collections.abc import Iterator
from datetime import timedelta
from operator import attrgetter

import pytest

from log_analyzer.models import LogEntry
from log_analyzer.pipeline import (
    errors_by_status,
    grouped,
    paginate,
    requests_per_hour,
    time_window,
    until,
)
from tests.helpers import TIMESTAMP, make_entry

HOUR = timedelta(hours=1)


def at(hours: float, status: int = 200) -> LogEntry:
    """Return an entry ``hours`` after ``TIMESTAMP`` (13:55:36)."""
    return make_entry(status, TIMESTAMP + hours * HOUR)


def test_grouped_sorts_before_grouping() -> None:
    """Keys that are not next to each other still end up in one group."""
    entries = [make_entry(200), make_entry(404), make_entry(200)]
    groups = list(grouped(entries, attrgetter("status")))
    assert [(status, len(group)) for status, group in groups] == [(200, 2), (404, 1)]


def test_requests_per_hour() -> None:
    """Hours are two-digit keys in order."""
    entries = [at(0), at(0.01), at(1), at(-5)]
    assert requests_per_hour(entries) == {"08": 1, "13": 2, "14": 1}


def test_errors_by_status_counts_only_errors() -> None:
    """2xx/3xx responses are left out."""
    entries = [make_entry(status) for status in (200, 404, 500, 404, 302)]
    assert errors_by_status(entries) == {"404": 2, "500": 1}


@pytest.mark.parametrize(
    ("page", "expected"),
    [(1, [0, 1, 2]), (2, [3, 4, 5]), (4, [9]), (5, [])],
    ids=["first", "middle", "last partial", "past the end"],
)
def test_paginate(page: int, expected: list[int]) -> None:
    """Pages of 3 over 10 items."""
    assert paginate(range(10), page, 3) == expected


@pytest.mark.parametrize(("page", "per_page"), [(0, 5), (1, 0)])
def test_paginate_rejects_values_below_one(page: int, per_page: int) -> None:
    """Pages and page sizes start at 1."""
    with pytest.raises(ValueError, match="at least 1"):
        paginate([1, 2, 3], page, per_page)


def test_until_stops_at_the_first_later_entry() -> None:
    """``takewhile`` stops reading; later entries are never pulled."""
    pulled: list[LogEntry] = []

    def entries() -> Iterator[LogEntry]:
        for entry in (at(0), at(1), at(2), at(3)):
            pulled.append(entry)
            yield entry

    kept = list(until(TIMESTAMP + 1.5 * HOUR, entries()))
    assert kept == [at(0), at(1)]
    assert len(pulled) == 3  # the 2-hour entry was read to stop, the 3-hour one was not


def test_time_window_includes_start_and_excludes_end() -> None:
    """``dropwhile`` skips before ``start``; ``takewhile`` stops at ``end``."""
    entries = [at(0), at(1), at(2), at(3)]
    window = list(time_window(TIMESTAMP + HOUR, TIMESTAMP + 3 * HOUR, entries))
    assert window == [at(1), at(2)]
