"""Aggregations built with ``functools.reduce()``.

Each ``reduce`` walks the entries once and folds them into one value. An
iterator can only be read once, so pass a list (or a fresh iterator) to each
aggregation.
"""

from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from functools import partial, reduce
from itertools import chain
from operator import attrgetter

from log_analyzer.models import CountItem, LogEntry
from log_analyzer.patterns.validators import find_all_ips


def count_requests(entries: Iterable[LogEntry]) -> int:
    """Return the number of entries."""
    return reduce(lambda total, _entry: total + 1, entries, 0)


def total_bytes(entries: Iterable[LogEntry]) -> int:
    """Return the bytes sent; a missing size (``-`` in the log) counts as 0."""
    return reduce(lambda total, entry: total + (entry.size or 0), entries, 0)


def _add_one(
    key: Callable[[LogEntry], str], counts: dict[str, int], entry: LogEntry
) -> dict[str, int]:
    """Reduce step: add 1 to the count of this entry's key.

    The accumulator dict is updated in place and returned, so counting stays
    O(n) instead of copying the dict for every entry.
    """
    name = key(entry)
    counts[name] = counts.get(name, 0) + 1
    return counts


def count_by(
    key: Callable[[LogEntry], str], entries: Iterable[LogEntry]
) -> dict[str, int]:
    """Count entries per key, in first-seen order.

    Example: ``count_by(attrgetter("method"), entries)`` → ``{"GET": 801, ...}``.
    """
    return reduce(partial(_add_one, key), entries, {})


def _status_text(entry: LogEntry) -> str:
    """Status code as text, so it can be a JSON key."""
    return str(entry.status)


# Specialised counters: the key is fixed once with partial().
requests_per_status = partial(count_by, _status_text)
requests_per_method = partial(count_by, attrgetter("method"))
requests_per_ip = partial(count_by, attrgetter("ip"))
requests_per_url = partial(count_by, attrgetter("url"))


def unique_urls(entries: Iterable[LogEntry]) -> set[str]:
    """Return every distinct URL."""
    return reduce(lambda urls, entry: urls | {entry.url}, entries, set[str]())


def referrer_ips(entries: Iterable[LogEntry]) -> dict[str, int]:
    """Count the IPv4 addresses found inside referrer URLs, most frequent first.

    A raw IP in a referrer (e.g. ``http://10.0.0.5/admin``) often means
    internal or unusual traffic. ``re.findall`` finds every address.
    """
    found = chain.from_iterable(
        find_all_ips(entry.referrer) for entry in entries if entry.referrer
    )
    return dict(Counter(found).most_common())


def top_n(counts: Mapping[str, int], n: int) -> list[CountItem]:
    """Return the ``n`` biggest counts, largest first; ties sorted by name."""
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"name": name, "count": count} for name, count in ranked[:n]]


def error_rate(errors: int, total: int) -> float:
    """Return ``errors`` as a percentage of ``total`` (1 decimal; 0.0 if empty)."""
    return round(100 * errors / total, 1) if total else 0.0
