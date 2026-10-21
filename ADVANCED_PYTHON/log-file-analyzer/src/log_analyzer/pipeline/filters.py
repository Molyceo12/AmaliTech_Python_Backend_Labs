"""Filter steps built with ``filter()`` and ``functools.partial()``.

Predicates take their settings first and the entry last, so ``partial`` can
fix the settings and leave a one-argument function that ``filter`` can use:
``filter(partial(by_method, "GET"), entries)``.
"""

from collections.abc import Callable, Collection, Iterable, Iterator
from datetime import datetime
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


def by_ip(ip: str, entry: LogEntry) -> bool:
    """Keep entries from this client IP address."""
    return entry.ip == ip


def in_time_range(start: datetime, end: datetime, entry: LogEntry) -> bool:
    """Keep entries from ``start`` (included) up to ``end`` (excluded)."""
    return start <= entry.timestamp < end


# Specialised filters: the settings are fixed once with partial().
only_success: Predicate = partial(by_status_range, 200, 299)
only_redirects: Predicate = partial(by_status_range, 300, 399)
only_client_errors: Predicate = partial(by_status_range, 400, 499)
only_server_errors: Predicate = partial(by_status_range, 500, 599)
only_errors: Predicate = partial(by_status_range, 400, 599)
only_get: Predicate = partial(by_method, "GET")
only_post: Predicate = partial(by_method, "POST")


def select(predicate: Predicate, entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
    """Keep the entries that pass ``predicate`` (a named ``filter()``)."""
    return filter(predicate, entries)


def select_all(
    predicates: Iterable[Predicate], entries: Iterable[LogEntry]
) -> Iterator[LogEntry]:
    """Keep the entries that pass every predicate.

    Example: ``select_all([only_errors, only_post], entries)``.
    """
    checks = tuple(predicates)
    return filter(lambda entry: all(check(entry) for check in checks), entries)
