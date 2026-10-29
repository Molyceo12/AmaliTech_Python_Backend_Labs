"""Shared fixtures. Integration tests skip when the Docker databases are down."""

from collections.abc import Iterator
from typing import Any

import pytest
import redis
from psycopg2.pool import ThreadedConnectionPool
from pymongo.database import Database

from ecommerce_pipeline.cache.top_products import CACHE_KEY
from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.nosql import create_mongo, create_redis
from ecommerce_pipeline.db.pool import create_pool, get_connection
from ecommerce_pipeline.db.schema import create_tables
from ecommerce_pipeline.exceptions import EcommerceError
from ecommerce_pipeline.sessions.carts import SESSIONS

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


@pytest.fixture
def redis_client() -> Iterator[redis.Redis]:
    """The real Redis from ``docker compose`` with the cache key removed, or skip."""
    try:
        client = create_redis(load_settings())
    except EcommerceError as error:
        pytest.skip(f"Redis not available: {error}")
    client.delete(CACHE_KEY)
    yield client
    client.delete(CACHE_KEY)
    client.close()


@pytest.fixture
def mongo_db() -> Iterator[Database[dict[str, Any]]]:
    """The real MongoDB with the sessions collection emptied, or skip."""
    try:
        db = create_mongo(load_settings())
    except EcommerceError as error:
        pytest.skip(f"MongoDB not available: {error}")
    db[SESSIONS].delete_many({})
    yield db
    db.client.close()
