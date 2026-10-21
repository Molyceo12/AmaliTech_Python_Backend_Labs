"""Tests for the ``@timer``, ``@cache`` and ``@log_call`` decorators."""

import logging

import pytest
from pytest_mock import MockerFixture

from log_analyzer.decorators import cache, last_duration, log_call, timer
from log_analyzer.parsing import parse_timestamp

TRACING = "log_analyzer.decorators.tracing"
TIMING = "log_analyzer.decorators.timing"


def test_timer_logs_and_remembers_the_time(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """The elapsed time is logged and kept for ``last_duration``."""
    mocker.patch(f"{TIMING}.time.perf_counter", side_effect=[1.0, 3.5])

    @timer
    def work() -> str:
        return "done"

    with caplog.at_level(logging.INFO, logger=TIMING):
        assert work() == "done"
    assert last_duration(work) == 2.5
    assert "work took 2.500 s" in caplog.text


def test_timer_still_records_when_the_function_fails(mocker: MockerFixture) -> None:
    """The time is kept and the exception is raised again."""
    mocker.patch(f"{TIMING}.time.perf_counter", side_effect=[0.0, 0.25])

    @timer
    def broken() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        broken()
    assert last_duration(broken) == 0.25


def test_last_duration_defaults_to_zero() -> None:
    """Untimed and not-yet-called functions report 0.0."""

    @timer
    def never_called() -> None:
        """Not called in this test."""

    assert last_duration(never_called) == 0.0
    assert last_duration(print) == 0.0


def test_cache_without_brackets_reuses_results() -> None:
    """The function body runs once per distinct argument."""
    calls: list[int] = []

    @cache
    def square(number: int) -> int:
        calls.append(number)
        return number * number

    assert [square(3), square(3), square(4)] == [9, 9, 16]
    assert calls == [3, 4]
    assert square.cache_info().hits == 1
    square.cache_clear()
    assert square.cache_info().currsize == 0


def test_cache_with_maxsize_drops_old_results() -> None:
    """``@cache(maxsize=1)`` keeps only the latest result."""

    @cache(maxsize=1)
    def double(number: int) -> int:
        return number * 2

    double(1)
    double(2)
    double(1)
    assert double.cache_info().misses == 3
    assert double.cache_info().maxsize == 1


def test_parse_timestamp_is_cached() -> None:
    """The parser uses ``@cache``: a repeated timestamp is a cache hit."""
    parse_timestamp.cache_clear()
    parse_timestamp("21/Oct/2026:13:55:36 +0000")
    parse_timestamp("21/Oct/2026:13:55:36 +0000")
    assert parse_timestamp.cache_info().hits == 1


def test_log_call_logs_arguments_and_result(caplog: pytest.LogCaptureFixture) -> None:
    """Calls and results are traced at DEBUG; long values are shortened."""

    @log_call
    def greet(name: str, *, punctuation: str = "!") -> str:
        return f"Hello {name}{punctuation}"

    with caplog.at_level(logging.DEBUG, logger=TRACING):
        assert greet("Ann", punctuation="?") == "Hello Ann?"
        greet("x" * 100)
    assert "Calling greet('Ann', punctuation='?')" in caplog.text
    assert "greet returned 'Hello Ann?'" in caplog.text
    assert "x" * 100 not in caplog.text


def test_log_call_logs_and_reraises_errors(caplog: pytest.LogCaptureFixture) -> None:
    """The exception is logged, then raised unchanged."""

    @log_call
    def fail() -> None:
        raise KeyError("missing")

    with caplog.at_level(logging.DEBUG, logger=TRACING), pytest.raises(KeyError):
        fail()
    assert "fail raised an exception" in caplog.text


def test_chained_decorators_keep_name_and_docstring(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """``functools.wraps`` keeps the original name and docstring; both run."""

    @timer
    @log_call
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    with caplog.at_level(logging.DEBUG):
        assert add(2, 3) == 5
    assert add.__name__ == "add"
    assert add.__doc__ == "Add two numbers."
    assert "Calling add(2, 3)" in caplog.text
    assert "add took" in caplog.text
