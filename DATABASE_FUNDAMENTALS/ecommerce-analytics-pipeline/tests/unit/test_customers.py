"""Tests for customer CRUD."""

from unittest.mock import MagicMock

import pytest

from ecommerce_pipeline.exceptions import DuplicateEmailError
from ecommerce_pipeline.repositories.customers import (
    INSERT_CUSTOMER,
    UniqueViolation,
    add_customer,
)


def test_add_customer_returns_the_new_id(fake_pool: MagicMock) -> None:
    """The values are passed as parameters and the new id is returned."""
    fake_pool.cursor.fetchone.return_value = (7,)
    assert add_customer(fake_pool, "Ama", "ama@example.com") == 7
    fake_pool.cursor.execute.assert_called_once_with(
        INSERT_CUSTOMER, ("Ama", "ama@example.com")
    )
    assert "%s" in INSERT_CUSTOMER


def test_duplicate_email_raises_and_rolls_back(fake_pool: MagicMock) -> None:
    """A unique violation becomes ``DuplicateEmailError``."""
    fake_pool.cursor.execute.side_effect = UniqueViolation()
    with pytest.raises(DuplicateEmailError, match="ama@example.com"):
        add_customer(fake_pool, "Ama", "ama@example.com")
    fake_pool.getconn.return_value.rollback.assert_called_once()
