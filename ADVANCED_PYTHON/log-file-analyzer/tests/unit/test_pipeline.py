"""Tests for chaining steps with ``pipe``/``compose`` and for ``summarize``."""

from functools import partial

from log_analyzer.pipeline import (
    clean_urls,
    compose,
    only_errors,
    parse_entries,
    pipe,
    select,
    summarize,
)
from tests.helpers import COMBINED_LINE, COMMON_LINE, SAMPLE_ENTRIES


def test_pipe_without_steps_returns_the_value() -> None:
    """Nothing to do: the value comes back."""
    assert pipe(5) == 5


def test_pipe_runs_steps_left_to_right() -> None:
    """``pipe(x, f, g)`` is ``g(f(x))``."""
    assert pipe(3, lambda x: x + 1, lambda x: x * 10) == 40


def test_compose_matches_pipe() -> None:
    """A composed function gives the same result as piping."""
    steps = (parse_entries, clean_urls, partial(select, only_errors), list)
    lines = [COMBINED_LINE, COMMON_LINE.replace(" 302 ", " 404 ")]
    assert compose(*steps)(lines) == pipe(lines, *steps)


def test_pipeline_on_log_lines() -> None:
    """Lines → entries → clean URLs → errors only."""
    lines = [COMBINED_LINE, "bad", COMMON_LINE.replace(" 302 ", " 500 ")]
    errors = pipe(lines, parse_entries, clean_urls, partial(select, only_errors), list)
    assert [(entry.ip, entry.status) for entry in errors] == [("10.0.0.5", 500)]


def test_summarize_small_entries() -> None:
    """Totals and counts for the five sample entries."""
    summary = summarize(SAMPLE_ENTRIES, top=2)
    assert summary == {
        "total_requests": 5,
        "total_bytes": 350,
        "error_count": 2,
        "error_rate": 40.0,
        "requests_per_status": {"200": 2, "404": 1, "500": 1, "302": 1},
        "requests_per_method": {"GET": 3, "POST": 2},
        "top_ips": [{"name": "10.0.0.1", "count": 3}, {"name": "10.0.0.2", "count": 1}],
        "top_urls": [{"name": "/", "count": 1}, {"name": "/about", "count": 1}],
        "unique_urls": 5,
    }


def test_summarize_accepts_an_iterator() -> None:
    """A one-time iterator still feeds every aggregation."""
    assert summarize(iter(SAMPLE_ENTRIES)) == summarize(SAMPLE_ENTRIES)


def test_summarize_no_entries() -> None:
    """An empty log gives zeros, not errors."""
    summary = summarize([])
    assert summary["total_requests"] == 0
    assert summary["error_rate"] == 0.0
    assert summary["top_ips"] == []


def test_summarize_sample_log(access_lines: list[str]) -> None:
    """On ``data/access.log`` the status counts add up to the 1,200 requests."""
    summary = summarize(parse_entries(access_lines))
    assert summary["total_requests"] == 1200
    assert sum(summary["requests_per_status"].values()) == 1200
    assert sum(summary["requests_per_method"].values()) == 1200
    assert len(summary["top_ips"]) == 5
