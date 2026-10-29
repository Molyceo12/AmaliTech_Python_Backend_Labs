"""Integration tests: the reports on the sample data."""

from decimal import Decimal

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.analytics.reports import product_ranking, revenue_per_customer
from ecommerce_pipeline.db.seed import load_sample_data


def test_product_ranking_shares_ranks_on_ties(
    clean_pool: ThreadedConnectionPool,
) -> None:
    """RANK() gives ties the same rank and skips the next one."""
    load_sample_data(clean_pool)
    ranking = product_ranking(clean_pool)
    assert len(ranking) == 15
    assert (ranking[0].name, ranking[0].units_sold) == ("Cotton T-Shirt", 12)
    # Earbuds and Phone Charger both sold 4 units: both rank 4, the next is 6.
    assert [p.sales_rank for p in ranking[3:6]] == [4, 4, 6]


def test_revenue_per_customer_matches_hand_totals(
    clean_pool: ThreadedConnectionPool,
) -> None:
    """Kofi: order 2 (105.00) + order 8 (51.00) + order 19 (120.00) = 276.00."""
    load_sample_data(clean_pool)
    top = revenue_per_customer(clean_pool)[0]
    assert (top.name, top.order_count, top.revenue) == (
        "Kofi Boateng",
        3,
        Decimal("276.00"),
    )
