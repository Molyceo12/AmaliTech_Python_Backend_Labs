"""Orders: ``create_order`` is one ACID transaction, ``get_customer_orders`` reads."""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from psycopg2.extensions import cursor
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.rows import fetch_value
from ecommerce_pipeline.exceptions import (
    CustomerNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
)

logger = logging.getLogger(__name__)

CUSTOMER_EXISTS = "SELECT 1 FROM customers WHERE customer_id = %s"
INSERT_ORDER = "INSERT INTO orders (customer_id) VALUES (%s) RETURNING order_id"
# FOR UPDATE locks the row, so two orders cannot both sell the last unit.
LOCK_PRODUCT = "SELECT price, stock FROM products WHERE product_id = %s FOR UPDATE"
INSERT_ITEM = """
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (%s, %s, %s, %s)
"""
REDUCE_STOCK = "UPDATE products SET stock = stock - %s WHERE product_id = %s"
CUSTOMER_ORDERS = """
    SELECT o.order_id, o.created_at,
           SUM(oi.quantity)::int AS item_count,
           SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id = %s
    GROUP BY o.order_id
    ORDER BY o.created_at DESC, o.order_id DESC
"""


@dataclass(frozen=True)
class OrderSummary:
    """One order of a customer, with its total computed in SQL."""

    order_id: int
    created_at: datetime
    item_count: int
    total: Decimal


def create_order(
    pool: ThreadedConnectionPool, customer_id: int, items: Mapping[int, int]
) -> int:
    """Create an order from ``{product_id: quantity}`` and return its id.

    Everything runs in one transaction: on any error nothing is saved.

    Raises:
        ValueError: If there are no items or a quantity is below 1.
        CustomerNotFoundError: If the customer does not exist.
        ProductNotFoundError: If a product does not exist.
        InsufficientStockError: If a product has too few units in stock.
    """
    if not items or min(items.values()) < 1:
        raise ValueError("An order needs at least one item, each quantity >= 1")
    with get_connection(pool) as conn, conn.cursor() as cur:
        cur.execute(CUSTOMER_EXISTS, (customer_id,))
        if cur.fetchone() is None:
            raise CustomerNotFoundError(f"Customer {customer_id} does not exist")
        cur.execute(INSERT_ORDER, (customer_id,))
        order_id: int = fetch_value(cur)
        # Lock products in id order so two orders never wait on each other.
        for product_id, quantity in sorted(items.items()):
            _add_item(cur, order_id, product_id, quantity)
    logger.info("Created order %d for customer %d", order_id, customer_id)
    return order_id


def _add_item(cur: cursor, order_id: int, product_id: int, quantity: int) -> None:
    """Lock the product, check its stock, add the item and reduce the stock."""
    cur.execute(LOCK_PRODUCT, (product_id,))
    row = cur.fetchone()
    if row is None:
        raise ProductNotFoundError(f"Product {product_id} does not exist")
    price, stock = row
    if stock < quantity:
        raise InsufficientStockError(
            f"Product {product_id}: {quantity} requested, {stock} in stock"
        )
    cur.execute(INSERT_ITEM, (order_id, product_id, quantity, price))
    cur.execute(REDUCE_STOCK, (quantity, product_id))


def get_customer_orders(
    pool: ThreadedConnectionPool, customer_id: int
) -> list[OrderSummary]:
    """Return the customer's orders, newest first (empty if there are none)."""
    with get_connection(pool) as conn, conn.cursor() as cur:
        cur.execute(CUSTOMER_ORDERS, (customer_id,))
        return [OrderSummary(*row) for row in cur.fetchall()]
