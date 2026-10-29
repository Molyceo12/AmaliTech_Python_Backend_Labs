"""Integration test: JSONB metadata search on the sample data."""

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.seed import load_sample_data
from ecommerce_pipeline.repositories.products import find_by_metadata


def test_find_by_metadata_uses_jsonb_containment(
    clean_pool: ThreadedConnectionPool,
) -> None:
    """``@>`` matches values inside arrays and plain keys."""
    load_sample_data(clean_pool)
    red = find_by_metadata(clean_pool, {"colors": ["red"]})
    assert [p.name for p in red] == [
        "Cotton T-Shirt",
        "Running Shoes",
        "Bluetooth Speaker",
        "Throw Pillow",
    ]
    shoes = find_by_metadata(clean_pool, {"category": "shoes", "sizes": ["40"]})
    assert [p.name for p in shoes] == ["Running Shoes", "Leather Sandals"]
