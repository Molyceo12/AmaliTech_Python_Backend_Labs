"""Tests for the ``reduce()`` aggregations, on entries with known totals."""

from dataclasses import replace
from operator import attrgetter

from log_analyzer.pipeline import (
    count_by,
    count_requests,
    error_rate,
    referrer_ips,
    requests_per_ip,
    requests_per_method,
    requests_per_status,
    requests_per_url,
    top_n,
    total_bytes,
    unique_urls,
)
from tests.helpers import SAMPLE_ENTRIES, make_entry


def test_count_requests() -> None:
    """One per entry; works on any iterable."""
    assert count_requests(SAMPLE_ENTRIES) == 5
    assert count_requests(iter(SAMPLE_ENTRIES)) == 5


def test_total_bytes_counts_missing_size_as_zero() -> None:
    """100 + 200 + (None → 0) + 50 + 0."""
    assert total_bytes(SAMPLE_ENTRIES) == 350


def test_count_by_any_key() -> None:
    """Counts per key, in first-seen order."""
    counts = count_by(attrgetter("ip"), SAMPLE_ENTRIES)
    assert counts == {"10.0.0.1": 3, "10.0.0.2": 1, "10.0.0.3": 1}
    assert list(counts) == ["10.0.0.1", "10.0.0.2", "10.0.0.3"]


def test_specialised_counters() -> None:
    """The partial counters group by status, method, IP and URL."""
    assert requests_per_status(SAMPLE_ENTRIES) == {
        "200": 2,
        "404": 1,
        "500": 1,
        "302": 1,
    }
    assert requests_per_method(SAMPLE_ENTRIES) == {"GET": 3, "POST": 2}
    assert requests_per_ip(SAMPLE_ENTRIES)["10.0.0.1"] == 3
    assert requests_per_url(SAMPLE_ENTRIES)["/about"] == 1


def test_unique_urls() -> None:
    """Each URL once."""
    assert unique_urls(SAMPLE_ENTRIES) == {"/", "/about", "/missing", "/api", "/login"}


def test_top_n_sorts_by_count_then_name() -> None:
    """Largest first; equal counts are ordered by name."""
    counts = {"b": 2, "a": 2, "c": 5, "d": 1}
    assert top_n(counts, 3) == [
        {"name": "c", "count": 5},
        {"name": "a", "count": 2},
        {"name": "b", "count": 2},
    ]
    assert len(top_n(counts, 10)) == 4


def test_error_rate() -> None:
    """Percentage with one decimal, and 0.0 when there are no requests."""
    assert error_rate(2, 5) == 40.0
    assert error_rate(1, 3) == 33.3
    assert error_rate(0, 0) == 0.0


def test_empty_input_gives_zeros() -> None:
    """Every aggregation has a sensible empty result."""
    assert count_requests([]) == 0
    assert total_bytes([]) == 0
    assert requests_per_status([]) == {}
    assert unique_urls([]) == set()


def test_referrer_ips_counts_addresses_in_referrers() -> None:
    """Every IP inside a referrer is counted; entries without one are ignored."""
    entries = [
        replace(make_entry(), referrer="http://10.0.0.5/a"),
        replace(make_entry(), referrer="http://10.0.0.5/b?from=8.8.8.8"),
        replace(make_entry(), referrer="https://example.com/"),
        make_entry(),
    ]
    assert referrer_ips(entries) == {"10.0.0.5": 2, "8.8.8.8": 1}
