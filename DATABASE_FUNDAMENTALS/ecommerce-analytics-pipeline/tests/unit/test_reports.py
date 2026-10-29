"""Tests for the RANK and CTE reports (mocked cursor)."""

from decimal import Decimal
from unittest.mock import MagicMock

from ecommerce_pipeline.analytics.reports import (
    QUERIES_DIR,
    CustomerRevenue,
    ProductRank,
    product_ranking,
    revenue_per_customer,
)


def test_query_files_use_rank_and_ctes() -> None:
    """The ranking uses a window function; revenue is built with CTEs."""
    ranking = (QUERIES_DIR / "product_ranking.sql").read_text(encoding="utf-8")
    revenue = (QUERIES_DIR / "revenue_per_customer.sql").read_text(encoding="utf-8")
    assert "RANK() OVER" in ranking
    assert "WITH order_totals AS" in revenue
    assert "customer_revenue AS" in revenue


def test_product_ranking_builds_rows(fake_pool: MagicMock) -> None:
    """Each row of the ranking query becomes a ``ProductRank``."""
    fake_pool.cursor.fetchall.return_value = [(1, 4, "Shirt", 12, Decimal("180"))]
    assert product_ranking(fake_pool) == [
        ProductRank(1, 4, "Shirt", 12, Decimal("180"))
    ]


def test_revenue_per_customer_builds_rows(fake_pool: MagicMock) -> None:
    """Each row of the revenue query becomes a ``CustomerRevenue``."""
    fake_pool.cursor.fetchall.return_value = [(2, "Kofi", 3, Decimal("276"))]
    assert revenue_per_customer(fake_pool) == [
        CustomerRevenue(2, "Kofi", 3, Decimal("276"))
    ]
