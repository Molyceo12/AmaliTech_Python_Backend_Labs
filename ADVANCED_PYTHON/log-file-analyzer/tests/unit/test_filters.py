"""Tests for the ``filter()`` predicates and the ``partial()`` filters."""

from datetime import timedelta
from functools import partial

import pytest

from log_analyzer.pipeline import (
    Predicate,
    by_ip,
    by_method,
    by_status,
    by_status_range,
    in_time_range,
    only_client_errors,
    only_errors,
    only_get,
    only_post,
    only_redirects,
    only_server_errors,
    only_success,
    select,
    select_all,
)
from tests.helpers import SAMPLE_ENTRIES, TIMESTAMP, make_entry


@pytest.mark.parametrize(
    ("status", "kept"), [(199, False), (200, True), (299, True), (300, False)]
)
def test_by_status_range_includes_both_ends(status: int, kept: bool) -> None:
    """``low`` and ``high`` are both inside the range."""
    assert by_status_range(200, 299, make_entry(status)) is kept


@pytest.mark.parametrize(
    ("predicate", "kept_statuses"),
    [
        (only_success, [200, 299]),
        (only_redirects, [300, 399]),
        (only_client_errors, [400, 499]),
        (only_server_errors, [500, 599]),
        (only_errors, [400, 499, 500, 599]),
    ],
    ids=["success", "redirects", "client errors", "server errors", "errors"],
)
def test_status_partials_keep_their_range(
    predicate: Predicate, kept_statuses: list[int]
) -> None:
    """Each ready-made filter keeps exactly its status band."""
    statuses = [199, 200, 299, 300, 399, 400, 499, 500, 599, 600]
    kept = [status for status in statuses if predicate(make_entry(status))]
    assert kept == kept_statuses


def test_partial_fixes_the_settings() -> None:
    """``only_errors`` is ``by_status_range`` with 400–599 already filled in."""
    assert isinstance(only_errors, partial)
    # pylint reads only_errors as the wrapped function and misses partial's fields.
    assert only_errors.func is by_status_range  # pylint: disable=no-member
    assert only_errors.args == (400, 599)  # pylint: disable=no-member


def test_by_status_keeps_listed_codes() -> None:
    """Only the given codes pass."""
    assert by_status({404, 500}, make_entry(404))
    assert not by_status({404, 500}, make_entry(200))


def test_method_filters() -> None:
    """``by_method`` and its GET/POST partials compare the method."""
    post = make_entry(method="POST")
    assert by_method("POST", post)
    assert only_post(post)
    assert not only_get(post)


def test_by_ip() -> None:
    """Only entries from that client pass."""
    assert by_ip("10.0.0.9", make_entry(ip="10.0.0.9"))
    assert not by_ip("10.0.0.9", make_entry())


def test_time_range_includes_start_and_excludes_end() -> None:
    """``start <= timestamp < end``."""
    hour = timedelta(hours=1)
    in_hour = partial(in_time_range, TIMESTAMP, TIMESTAMP + hour)
    assert in_hour(make_entry(timestamp=TIMESTAMP))
    assert in_hour(make_entry(timestamp=TIMESTAMP + hour / 2))
    assert not in_hour(make_entry(timestamp=TIMESTAMP + hour))
    assert not in_hour(make_entry(timestamp=TIMESTAMP - hour))


def test_select_is_filter() -> None:
    """``select`` keeps the entries that pass, in order."""
    errors = list(select(only_errors, SAMPLE_ENTRIES))
    assert [entry.status for entry in errors] == [404, 500]


def test_select_all_needs_every_predicate() -> None:
    """An entry must pass all the predicates to be kept."""
    kept = list(select_all([only_errors, only_post], SAMPLE_ENTRIES))
    assert [entry.url for entry in kept] == ["/api"]


def test_select_all_without_predicates_keeps_everything() -> None:
    """No predicates means nothing is filtered out."""
    assert list(select_all([], SAMPLE_ENTRIES)) == SAMPLE_ENTRIES
