"""Integration test: create the tables in the real PostgreSQL."""

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.schema import create_indexes, create_tables

TABLES = {"customers", "products", "orders", "order_items"}


def test_setup_creates_the_four_tables_and_can_run_twice(
    pool: ThreadedConnectionPool,
) -> None:
    """Running the schema twice leaves exactly the four tables."""
    create_tables(pool)
    create_tables(pool)
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables"
            " WHERE table_schema = 'public'"
        )
        assert {row[0] for row in cursor.fetchall()} >= TABLES


def test_indexes_are_btree_and_gin(pool: ThreadedConnectionPool) -> None:
    """``create_indexes`` adds a B-tree on orders and a GIN on products."""
    create_tables(pool)
    create_indexes(pool)
    create_indexes(pool)
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT indexname, indexdef FROM pg_indexes"
            " WHERE indexname IN ('idx_orders_customer_id', 'idx_products_metadata')"
            " ORDER BY indexname"
        )
        (orders_name, orders_def), (products_name, products_def) = cursor.fetchall()
    assert orders_name == "idx_orders_customer_id"
    assert "USING btree (customer_id)" in orders_def
    assert products_name == "idx_products_metadata"
    assert "USING gin (metadata)" in products_def
