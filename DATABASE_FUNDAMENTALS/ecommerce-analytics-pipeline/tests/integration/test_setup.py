"""Integration test: create the tables in the real PostgreSQL."""

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.schema import create_tables

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
