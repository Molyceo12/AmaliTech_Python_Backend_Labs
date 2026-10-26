"""Tests for the ``filter()`` predicates and the ``partial()`` filters."""

from functools import partial

import pytest

from log_analyzer.pipeline import (
    Predicate,
    by_method,
    by_status,
    by_status_range,
    only_errors,
    select,
    select_all,
)
from tests.helpers import SAMPLE_ENTRIES, make_entry


@pytest.mark.parametrize(
    ("status", "kept"), [(199, False), (200, True), (299, True), (300, False)]
)
def test_by_status_range_includes_both_ends(status: int, kept: bool) -> None:
    """``low`` and ``high`` are both inside the range."""
    assert by_status_range(200, 299, make_entry(status)) is kept


def test_only_errors_keeps_4xx_and_5xx() -> None:
    """``only_errors`` keeps exactly the 400–599 band."""
    statuses = [199, 200, 299, 300, 399, 400, 499, 500, 599, 600]
    kept = [status for status in statuses if only_errors(make_entry(status))]
    assert kept == [400, 499, 500, 599]


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


def test_by_method_compares_the_method() -> None:
    """Only entries with that HTTP method pass."""
    post = make_entry(method="POST")
    assert by_method("POST", post)
    assert not by_method("GET", post)


def test_select_is_filter() -> None:
    """``select`` keeps the entries that pass, in order."""
    errors = list(select(only_errors, SAMPLE_ENTRIES))
    assert [entry.status for entry in errors] == [404, 500]


def test_select_all_needs_every_predicate() -> None:
    """An entry must pass all the predicates to be kept."""
    only_post: Predicate = partial(by_method, "POST")
    kept = list(select_all([only_errors, only_post], SAMPLE_ENTRIES))
    assert [entry.url for entry in kept] == ["/api"]


def test_select_all_without_predicates_keeps_everything() -> None:
    """No predicates means nothing is filtered out."""
    assert list(select_all([], SAMPLE_ENTRIES)) == SAMPLE_ENTRIES
