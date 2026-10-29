"""Product CRUD. ``metadata`` (sizes, colors, ...) is stored as JSONB."""

import logging
from decimal import Decimal
from typing import Any

from psycopg2.extras import Json
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.rows import fetch_value

logger = logging.getLogger(__name__)

INSERT_PRODUCT = """
    INSERT INTO products (name, price, stock, metadata)
    VALUES (%s, %s, %s, %s)
    RETURNING product_id
"""


def add_product(
    pool: ThreadedConnectionPool,
    name: str,
    price: Decimal,
    stock: int,
    metadata: dict[str, Any] | None = None,
) -> int:
    """Insert a product and return the new ``product_id``."""
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(INSERT_PRODUCT, (name, price, stock, Json(metadata or {})))
        product_id: int = fetch_value(cursor)
    logger.info("Added product %d", product_id)
    return product_id
