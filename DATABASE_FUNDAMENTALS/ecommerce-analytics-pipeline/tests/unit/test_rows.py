"""Tests for the result helpers."""

from unittest.mock import MagicMock

import pytest

from ecommerce_pipeline.db.rows import fetch_value


def test_fetch_value_returns_the_first_column() -> None:
    """The first value of the row is returned."""
    cur = MagicMock()
    cur.fetchone.return_value = (5, "x")
    assert fetch_value(cur) == 5


def test_fetch_value_raises_when_there_is_no_row() -> None:
    """An empty result is an error, not ``None``."""
    cur = MagicMock()
    cur.fetchone.return_value = None
    with pytest.raises(LookupError):
        fetch_value(cur)
