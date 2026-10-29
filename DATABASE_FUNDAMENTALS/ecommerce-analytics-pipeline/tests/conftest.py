"""Shared fixtures. Integration tests skip when the Docker databases are down."""

from collections.abc import Iterator

import pytest
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.pool import create_pool
from ecommerce_pipeline.exceptions import EcommerceError


@pytest.fixture
def pool() -> Iterator[ThreadedConnectionPool]:
    """A pool to the real PostgreSQL from ``docker compose``, or skip."""
    try:
        real_pool = create_pool(load_settings())
    except EcommerceError as error:
        pytest.skip(f"PostgreSQL not available: {error}")
    yield real_pool
    real_pool.closeall()
