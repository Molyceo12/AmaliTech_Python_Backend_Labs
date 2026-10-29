"""Integration tests: orders against the real PostgreSQL."""

from decimal import Decimal

import pytest
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.rows import fetch_value
from ecommerce_pipeline.exceptions import DuplicateEmailError, InsufficientStockError
from ecommerce_pipeline.repositories.customers import add_customer
from ecommerce_pipeline.repositories.orders import create_order, get_customer_orders
from ecommerce_pipeline.repositories.products import add_product


def _value(pool: ThreadedConnectionPool, query: str, *params: object) -> int:
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(query, params)
        value: int = fetch_value(cursor)
    return value


def test_order_saves_items_and_reduces_stock(
    clean_pool: ThreadedConnectionPool,
) -> None:
    """A good order is saved with its items, and the stock goes down."""
    customer = add_customer(clean_pool, "Ama", "ama@example.com")
    shirt = add_product(clean_pool, "Shirt", Decimal("10.00"), 5, {"color": "red"})
    mug = add_product(clean_pool, "Mug", Decimal("4.50"), 3)
    create_order(clean_pool, customer, {shirt: 2, mug: 1})
    assert _value(clean_pool, "SELECT COUNT(*) FROM order_items") == 2
    assert (
        _value(clean_pool, "SELECT stock FROM products WHERE product_id = %s", shirt)
        == 3
    )
    [summary] = get_customer_orders(clean_pool, customer)
    assert summary.item_count == 3
    assert summary.total == Decimal("24.50")


def test_failed_order_leaves_no_rows(clean_pool: ThreadedConnectionPool) -> None:
    """Too little stock on the second product rolls back the whole order."""
    customer = add_customer(clean_pool, "Kofi", "kofi@example.com")
    shirt = add_product(clean_pool, "Shirt", Decimal("10.00"), 5)
    mug = add_product(clean_pool, "Mug", Decimal("4.50"), 1)
    with pytest.raises(InsufficientStockError):
        create_order(clean_pool, customer, {shirt: 2, mug: 2})
    assert _value(clean_pool, "SELECT COUNT(*) FROM orders") == 0
    assert _value(clean_pool, "SELECT COUNT(*) FROM order_items") == 0
    assert _value(clean_pool, "SELECT SUM(stock) FROM products") == 6


def test_duplicate_email_is_rejected(clean_pool: ThreadedConnectionPool) -> None:
    """The UNIQUE constraint on email is reported as ``DuplicateEmailError``."""
    add_customer(clean_pool, "Ama", "ama@example.com")
    with pytest.raises(DuplicateEmailError):
        add_customer(clean_pool, "Ama Two", "ama@example.com")
