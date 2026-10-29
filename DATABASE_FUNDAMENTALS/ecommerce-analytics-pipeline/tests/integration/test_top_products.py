"""Integration test: the top products cache with real Redis and PostgreSQL."""

import redis
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.cache.top_products import (
    CACHE_KEY,
    TTL_SECONDS,
    get_top_products,
)
from ecommerce_pipeline.db.seed import load_sample_data


def test_first_call_fills_the_cache_second_reads_it(
    clean_pool: ThreadedConnectionPool, redis_client: redis.Redis
) -> None:
    """A miss stores the list with a TTL; the next call returns the same list."""
    load_sample_data(clean_pool)
    first = get_top_products(clean_pool, redis_client)
    assert len(first) == 10
    assert first[0].name == "Cotton T-Shirt"  # 12 units in the sample data
    assert 0 < int(redis_client.ttl(CACHE_KEY)) <= TTL_SECONDS
    assert get_top_products(clean_pool, redis_client) == first
