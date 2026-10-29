"""Shared fixtures. Integration tests skip when the Docker databases are down."""

from collections.abc import Iterator

import pytest
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.pool import create_pool, get_connection
from ecommerce_pipeline.db.schema import create_tables
from ecommerce_pipeline.exceptions import EcommerceError

EMPTY_TABLES = (
    "TRUNCATE order_items, orders, products, customers RESTART IDENTITY CASCADE"
)


@pytest.fixture(name="pool")
def fixture_pool() -> Iterator[ThreadedConnectionPool]:
    """A pool to the real PostgreSQL from ``docker compose``, or skip."""
    try:
        real_pool = create_pool(load_settings())
    except EcommerceError as error:
        pytest.skip(f"PostgreSQL not available: {error}")
    yield real_pool
    real_pool.closeall()


@pytest.fixture
def clean_pool(pool: ThreadedConnectionPool) -> ThreadedConnectionPool:
    """The real pool with the tables created and emptied."""
    create_tables(pool)
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(EMPTY_TABLES)
    return pool
