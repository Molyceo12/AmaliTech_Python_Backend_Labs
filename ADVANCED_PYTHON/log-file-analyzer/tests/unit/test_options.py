"""Tests for ``AnalyzerOptions``."""

from datetime import timedelta

from log_analyzer.pipeline import only_errors
from log_analyzer.services import AnalyzerOptions
from tests.helpers import TIMESTAMP, make_entry


def test_no_options_means_no_filters() -> None:
    """By default everything is kept."""
    options = AnalyzerOptions()
    assert not options.predicates()
    assert not options.describe()


def test_each_option_adds_a_filter() -> None:
    """Status codes, errors only and method each add one predicate."""
    options = AnalyzerOptions(statuses=(404, 500), errors_only=True, method="post")
    checks = options.predicates()
    assert len(checks) == 3
    assert checks[0](make_entry(404))
    assert not checks[0](make_entry(403))
    assert checks[1] is only_errors
    assert checks[2](make_entry(method="POST"))  # method is upper-cased


def test_describe_lists_active_filters() -> None:
    """The report shows the filters as text."""
    options = AnalyzerOptions(
        statuses=(404,),
        errors_only=True,
        method="get",
        start=TIMESTAMP,
        end=TIMESTAMP + timedelta(hours=1),
    )
    assert options.describe() == {
        "statuses": "404",
        "errors_only": "yes",
        "method": "GET",
        "from": "2026-10-21T13:55:36+00:00",
        "to": "2026-10-21T14:55:36+00:00",
    }
