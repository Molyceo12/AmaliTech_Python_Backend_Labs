"""Unit-test fixtures: a fake pool whose connection hands out one fake cursor."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def fake_pool() -> MagicMock:
    """A pool mock; its cursor is at ``fake_pool.cursor``."""
    pool = MagicMock()
    pool.cursor = pool.getconn.return_value.cursor.return_value.__enter__.return_value
    return pool
