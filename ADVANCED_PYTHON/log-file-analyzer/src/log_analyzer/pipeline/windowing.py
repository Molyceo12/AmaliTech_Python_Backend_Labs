"""Grouping and windowing with ``itertools``: groupby, islice, takewhile."""

from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from functools import partial
from itertools import groupby, islice, takewhile
from typing import TypeVar

from log_analyzer.models import LogEntry
from log_analyzer.pipeline.filters import in_time_range, only_errors

T = TypeVar("T")
K = TypeVar("K", int, str)


def grouped(
    entries: Iterable[LogEntry], key: Callable[[LogEntry], K]
) -> Iterator[tuple[K, list[LogEntry]]]:
    """Yield ``(key, entries)`` pairs, one per distinct key, in key order.

    ``groupby`` only groups items that are next to each other, so the entries
    are sorted by the same key first.
    """
    for name, group in groupby(sorted(entries, key=key), key=key):
        yield name, list(group)


def _hour_text(entry: LogEntry) -> str:
    """Hour of the request as two digits, e.g. ``"09"``."""
    return f"{entry.hour:02d}"


def _status_text(entry: LogEntry) -> str:
    """Status code as text, so it can be a JSON key."""
    return str(entry.status)


def requests_per_hour(entries: Iterable[LogEntry]) -> dict[str, int]:
    """Count requests per hour of the day: ``{"00": 41, "01": 52, ...}``."""
    return {hour: len(group) for hour, group in grouped(entries, _hour_text)}


def errors_by_status(entries: Iterable[LogEntry]) -> dict[str, int]:
    """Count the 4xx/5xx responses per status code: ``{"404": 89, ...}``."""
    errors = filter(only_errors, entries)
    return {status: len(group) for status, group in grouped(errors, _status_text)}


def paginate(items: Iterable[T], page: int, per_page: int) -> list[T]:
    """Return one page of items; page 1 holds the first ``per_page`` items.

    ``islice`` skips to the page without building the earlier pages.

    Raises:
        ValueError: If ``page`` or ``per_page`` is less than 1.
    """
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be at least 1")
    start = (page - 1) * per_page
    return list(islice(items, start, start + per_page))


def until(end: datetime, entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
    """Yield entries made before ``end``, stopping at the first later one.

    Logs are written in time order, so ``takewhile`` can stop reading as soon
    as it passes ``end`` instead of checking the rest of the file.
    """
    return takewhile(lambda entry: entry.timestamp < end, entries)


def time_window(
    start: datetime, end: datetime, entries: Iterable[LogEntry]
) -> Iterator[LogEntry]:
    """Yield entries from ``start`` (included) to ``end`` (excluded).

    ``until`` (``takewhile``) stops reading at ``end``, so later entries are
    never checked; ``filter(in_time_range)`` then keeps only the entries
    inside the window. Like ``until``, this expects entries in time order.
    """
    return filter(partial(in_time_range, start, end), until(end, entries))
