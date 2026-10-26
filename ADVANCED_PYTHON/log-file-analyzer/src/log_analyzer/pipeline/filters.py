"""Filter steps built with ``filter()`` and ``functools.partial()``.

Predicates take their settings first and the entry last, so ``partial`` can
fix the settings and leave a one-argument function that ``filter`` can use:
``filter(partial(by_method, "GET"), entries)``.
"""

from collections.abc import Callable, Collection, Iterable, Iterator
from functools import partial

from log_analyzer.models import LogEntry

Predicate = Callable[[LogEntry], bool]


def by_status_range(low: int, high: int, entry: LogEntry) -> bool:
    """Keep entries whose status is between ``low`` and ``high`` (both included)."""
    return low <= entry.status <= high


def by_status(codes: Collection[int], entry: LogEntry) -> bool:
    """Keep entries whose status is one of ``codes``."""
    return entry.status in codes


def by_method(method: str, entry: LogEntry) -> bool:
    """Keep entries with this HTTP method, e.g. ``"GET"``."""
    return entry.method == method


# Specialised filter: the settings are fixed once with partial().
only_errors: Predicate = partial(by_status_range, 400, 599)


def select(predicate: Predicate, entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
    """Keep the entries that pass ``predicate`` (a named ``filter()``)."""
    return filter(predicate, entries)


def select_all(
    predicates: Iterable[Predicate], entries: Iterable[LogEntry]
) -> Iterator[LogEntry]:
    """Keep the entries that pass every predicate.

    Example: ``select_all([only_errors, partial(by_method, "POST")], entries)``.
    """
    checks = tuple(predicates)
    return filter(lambda entry: all(check(entry) for check in checks), entries)
