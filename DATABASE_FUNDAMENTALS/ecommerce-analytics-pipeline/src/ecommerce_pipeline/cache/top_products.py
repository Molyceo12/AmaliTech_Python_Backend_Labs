"""Top 10 best-selling products: read from Redis, fall back to PostgreSQL."""

import json
import logging
from dataclasses import asdict, dataclass

import redis
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection

logger = logging.getLogger(__name__)

CACHE_KEY = "top_products"
# Best sellers change slowly, so a 5-minute-old list is fine.
TTL_SECONDS = 300
TOP_PRODUCTS = """
    SELECT p.product_id, p.name, SUM(oi.quantity)::int AS units_sold
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.name
    ORDER BY units_sold DESC, p.product_id
    LIMIT 10
"""


@dataclass(frozen=True)
class TopProduct:
    """A product and how many units of it were sold."""

    product_id: int
    name: str
    units_sold: int


def get_top_products(
    pool: ThreadedConnectionPool, cache: redis.Redis
) -> list[TopProduct]:
    """Return the 10 best sellers from the cache, or from PostgreSQL on a miss."""
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        logger.info("Cache hit: %s", CACHE_KEY)
        return [TopProduct(**item) for item in json.loads(str(cached))]
    logger.info("Cache miss: %s", CACHE_KEY)
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(TOP_PRODUCTS)
        products = [TopProduct(*row) for row in cursor.fetchall()]
    cache.set(CACHE_KEY, json.dumps([asdict(p) for p in products]), ex=TTL_SECONDS)
    return products
