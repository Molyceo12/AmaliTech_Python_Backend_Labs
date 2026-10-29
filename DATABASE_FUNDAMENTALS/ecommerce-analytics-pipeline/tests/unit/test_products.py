"""Tests for product CRUD."""

from decimal import Decimal
from unittest.mock import MagicMock

from ecommerce_pipeline.repositories.products import INSERT_PRODUCT, add_product


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
