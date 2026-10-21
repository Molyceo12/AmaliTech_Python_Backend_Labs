"""Tests for the ``LogEntry`` model."""

import dataclasses

import pytest

from tests.helpers import make_entry


@pytest.mark.parametrize(
    ("status", "is_error"),
    [(200, False), (302, False), (399, False), (400, True), (404, True), (503, True)],
)
def test_is_error_for_4xx_and_5xx(status: int, is_error: bool) -> None:
    """Client (4xx) and server (5xx) responses are errors."""
    assert make_entry(status).is_error is is_error


def test_hour_comes_from_the_timestamp() -> None:
    """``hour`` is the hour of the request time."""
    assert make_entry().hour == 13


def test_entry_is_frozen() -> None:
    """Parsed entries cannot be changed by accident."""
    entry = make_entry()
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.status = 500  # type: ignore[misc]
