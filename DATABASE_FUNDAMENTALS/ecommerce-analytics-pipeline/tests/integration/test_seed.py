"""Integration test: load the sample data into the real PostgreSQL."""

from decimal import Decimal

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.seed import load_sample_data
from ecommerce_pipeline.repositories.orders import get_customer_orders

COUNT_ROWS = """
    SELECT (SELECT COUNT(*) FROM customers), (SELECT COUNT(*) FROM products),
           (SELECT COUNT(*) FROM orders), (SELECT COUNT(*) FROM order_items)
"""


def test_seed_twice_gives_the_same_rows(clean_pool: ThreadedConnectionPool) -> None:
    """Seeding again replaces the rows instead of adding duplicates."""
    load_sample_data(clean_pool)
    load_sample_data(clean_pool)
    with get_connection(clean_pool) as conn, conn.cursor() as cursor:
        cursor.execute(COUNT_ROWS)
        assert cursor.fetchone() == (10, 15, 20, 34)
    # Customer 1 has orders 14, 4 and 1 (newest first).
    orders = get_customer_orders(clean_pool, 1)
    assert [order.order_id for order in orders] == [14, 4, 1]
    assert orders[-1].total == Decimal("38.00")
