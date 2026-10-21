"""Chaining the steps into one readable pipeline.

Example: the error entries of some log lines, with clean URLs::

    errors = pipe(lines, parse_entries, clean_urls, partial(select, only_errors), list)

The steps run left to right, like reading the sentence.
"""

from collections.abc import Callable, Iterable
from functools import reduce
from typing import Any

from log_analyzer.models import LogEntry, LogSummary
from log_analyzer.pipeline.aggregations import (
    count_requests,
    error_rate,
    requests_per_ip,
    requests_per_method,
    requests_per_status,
    requests_per_url,
    top_n,
    total_bytes,
    unique_urls,
)
from log_analyzer.pipeline.filters import only_errors, select

Step = Callable[[Any], Any]


def pipe(value: Any, *steps: Step) -> Any:
    """Pass ``value`` through every step, left to right.

    ``pipe(x, f, g)`` is ``g(f(x))``; with no steps it returns ``value``.
    """
    return reduce(lambda result, step: step(result), steps, value)


def compose(*steps: Step) -> Step:
    """Return one function that runs ``steps`` left to right.

    Example: ``errors_of = compose(parse_entries, partial(select, only_errors))``.
    """
    return lambda value: pipe(value, *steps)


def summarize(entries: Iterable[LogEntry], top: int = 5) -> LogSummary:
    """Build the totals and counts for a set of entries.

    The entries are turned into a list once, because every aggregation reads
    them from the start.

    Args:
        entries: Parsed log entries.
        top: How many IPs and URLs the "top" lists keep.
    """
    items = list(entries)
    total = count_requests(items)
    errors = count_requests(select(only_errors, items))
    return {
        "total_requests": total,
        "total_bytes": total_bytes(items),
        "error_count": errors,
        "error_rate": error_rate(errors, total),
        "requests_per_status": requests_per_status(items),
        "requests_per_method": requests_per_method(items),
        "top_ips": top_n(requests_per_ip(items), top),
        "top_urls": top_n(requests_per_url(items), top),
        "unique_urls": len(unique_urls(items)),
    }
