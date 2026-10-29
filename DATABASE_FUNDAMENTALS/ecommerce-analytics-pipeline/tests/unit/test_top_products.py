"""Tests for the top products cache (mocked Redis and PostgreSQL)."""

import json
from unittest.mock import MagicMock

from ecommerce_pipeline.cache.top_products import (
    CACHE_KEY,
    TTL_SECONDS,
    TopProduct,
    get_top_products,
)


def test_cache_hit_skips_postgres(fake_pool: MagicMock) -> None:
    """A cached list is returned without touching PostgreSQL."""
    cache = MagicMock()
    cache.get.return_value = json.dumps(
        [{"product_id": 1, "name": "Shirt", "units_sold": 9}]
    )
    assert get_top_products(fake_pool, cache) == [TopProduct(1, "Shirt", 9)]
    fake_pool.getconn.assert_not_called()


def test_cache_miss_runs_sql_and_stores_with_ttl(fake_pool: MagicMock) -> None:
    """On a miss the SQL runs and the result is cached with the TTL."""
    cache = MagicMock()
    cache.get.return_value = None
    fake_pool.cursor.fetchall.return_value = [(1, "Shirt", 9)]
    assert get_top_products(fake_pool, cache) == [TopProduct(1, "Shirt", 9)]
    key, value = cache.set.call_args.args
    assert key == CACHE_KEY
    assert json.loads(value) == [{"product_id": 1, "name": "Shirt", "units_sold": 9}]
    assert cache.set.call_args.kwargs == {"ex": TTL_SECONDS}
