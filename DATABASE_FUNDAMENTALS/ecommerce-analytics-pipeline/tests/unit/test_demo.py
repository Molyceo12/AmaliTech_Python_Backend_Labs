"""Tests for the demo walk-through (every store mocked)."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline.cache.top_products import TopProduct
from ecommerce_pipeline.demo import CUSTOMER_ID, run_demo
from ecommerce_pipeline.repositories.orders import OrderSummary
from ecommerce_pipeline.repositories.products import ProductMatch


def test_demo_orders_the_cart_and_shows_cache_source(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """The Mongo cart is ordered in PostgreSQL; the 2nd top-10 call is cached."""
    mocker.patch(
        "ecommerce_pipeline.demo.find_by_metadata",
        return_value=[ProductMatch(1, "Shirt", Decimal("15.00"), {})],
    )
    mocker.patch("ecommerce_pipeline.demo.create_session", return_value="s1")
    mocker.patch("ecommerce_pipeline.demo.add_to_cart")
    mocker.patch("ecommerce_pipeline.demo.get_cart", return_value={1: 1})
    create_order = mocker.patch("ecommerce_pipeline.demo.create_order")
    mocker.patch(
        "ecommerce_pipeline.demo.get_customer_orders",
        return_value=[OrderSummary(7, datetime(2026, 10, 29), 1, Decimal("15.00"))],
    )
    mocker.patch(
        "ecommerce_pipeline.demo.get_top_products",
        return_value=[TopProduct(1, "Shirt", 12)],
    )
    pool, cache = MagicMock(), MagicMock()
    cache.exists.side_effect = [0, 1]
    run_demo(pool, cache, MagicMock())
    create_order.assert_called_once_with(pool, CUSTOMER_ID, {1: 1})
    out = capsys.readouterr().out
    assert "order 7: 1 items, 15.00" in out
    assert "from database: Shirt" in out
    assert "from cache: Shirt" in out
