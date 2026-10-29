"""Tests for order creation and reading (mocked database)."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from ecommerce_pipeline.exceptions import (
    CustomerNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
)
from ecommerce_pipeline.repositories.orders import (
    LOCK_PRODUCT,
    OrderSummary,
    create_order,
    get_customer_orders,
)

CUSTOMER = (1,)
ORDER_ID = (10,)


def test_create_order_commits_and_returns_the_id(fake_pool: MagicMock) -> None:
    """A valid order is committed; products are locked in id order."""
    fake_pool.cursor.fetchone.side_effect = [
        CUSTOMER,
        ORDER_ID,
        (Decimal("2.00"), 5),
        (Decimal("3.00"), 5),
    ]
    assert create_order(fake_pool, 1, {9: 1, 4: 2}) == 10
    locked = [
        c.args[1]
        for c in fake_pool.cursor.execute.call_args_list
        if c.args[0] == LOCK_PRODUCT
    ]
    assert locked == [(4,), (9,)]
    fake_pool.getconn.return_value.commit.assert_called_once()


@pytest.mark.parametrize(
    ("rows", "error"),
    [
        ([None], CustomerNotFoundError),
        ([CUSTOMER, ORDER_ID, None], ProductNotFoundError),
        ([CUSTOMER, ORDER_ID, (Decimal("2.00"), 1)], InsufficientStockError),
    ],
)
def test_create_order_error_rolls_back(
    fake_pool: MagicMock, rows: list[object], error: type[Exception]
) -> None:
    """Each problem raises its own error and nothing is committed."""
    fake_pool.cursor.fetchone.side_effect = rows
    with pytest.raises(error):
        create_order(fake_pool, 1, {4: 2})
    conn = fake_pool.getconn.return_value
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


@pytest.mark.parametrize("items", [{}, {4: 0}])
def test_create_order_rejects_bad_items_before_the_database(
    fake_pool: MagicMock, items: dict[int, int]
) -> None:
    """Empty orders and quantities below 1 never reach PostgreSQL."""
    with pytest.raises(ValueError):
        create_order(fake_pool, 1, items)
    fake_pool.getconn.assert_not_called()


def test_get_customer_orders_builds_summaries(fake_pool: MagicMock) -> None:
    """Each row becomes an ``OrderSummary``."""
    created = datetime(2026, 1, 1, tzinfo=UTC)
    fake_pool.cursor.fetchall.return_value = [(10, created, 3, Decimal("8.00"))]
    assert get_customer_orders(fake_pool, 1) == [
        OrderSummary(10, created, 3, Decimal("8.00"))
    ]
