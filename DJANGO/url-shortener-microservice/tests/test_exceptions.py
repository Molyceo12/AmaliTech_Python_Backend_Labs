"""Tests for the JSON error handler."""

from url_shortener.exceptions import json_exception_handler


def test_other_exceptions_are_left_to_django() -> None:
    """A non-API error is not turned into a JSON body (Django shows a 500)."""
    assert json_exception_handler(ValueError("boom"), {}) is None
