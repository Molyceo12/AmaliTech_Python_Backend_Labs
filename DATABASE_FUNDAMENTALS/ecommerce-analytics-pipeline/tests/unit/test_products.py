"""Tests for product CRUD."""

from decimal import Decimal
from unittest.mock import MagicMock

from ecommerce_pipeline.repositories.products import (
    FIND_BY_METADATA,
    INSERT_PRODUCT,
    ProductMatch,
    add_product,
    find_by_metadata,
)


def test_add_product_stores_metadata_as_json(fake_pool: MagicMock) -> None:
    """Metadata is wrapped for JSONB and the new id is returned."""
    fake_pool.cursor.fetchone.return_value = (3,)
    product_id = add_product(fake_pool, "Shirt", Decimal("9.99"), 5, {"color": "red"})
    assert product_id == 3
    query, params = fake_pool.cursor.execute.call_args.args
    assert query == INSERT_PRODUCT
    assert params[:3] == ("Shirt", Decimal("9.99"), 5)
    assert params[3].adapted == {"color": "red"}


def test_add_product_without_metadata_stores_an_empty_object(
    fake_pool: MagicMock,
) -> None:
    """No metadata becomes ``{}``, matching the column default."""
    fake_pool.cursor.fetchone.return_value = (4,)
    add_product(fake_pool, "Mug", Decimal("4.50"), 10)
    assert fake_pool.cursor.execute.call_args.args[1][3].adapted == {}


def test_find_by_metadata_passes_the_filter_as_json(fake_pool: MagicMock) -> None:
    """The filter goes as a JSONB parameter and rows become ``ProductMatch``."""
    fake_pool.cursor.fetchall.return_value = [
        (1, "Shirt", Decimal("9.99"), {"colors": ["red"]})
    ]
    found = find_by_metadata(fake_pool, {"colors": ["red"]})
    assert found == [ProductMatch(1, "Shirt", Decimal("9.99"), {"colors": ["red"]})]
    query, params = fake_pool.cursor.execute.call_args.args
    assert query == FIND_BY_METADATA
    assert params[0].adapted == {"colors": ["red"]}
