"""Reports from ``sql/queries/``: product ranking (RANK) and revenue (CTEs)."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.schema import SQL_DIR

QUERIES_DIR = SQL_DIR / "queries"


@dataclass(frozen=True)
class ProductRank:
    """A product's place in the best-seller ranking."""

    sales_rank: int
    product_id: int
    name: str
    units_sold: int
    revenue: Decimal


@dataclass(frozen=True)
class CustomerRevenue:
    """How many orders a customer placed and what they spent."""

    customer_id: int
    name: str
    order_count: int
    revenue: Decimal


def _run_query(pool: ThreadedConnectionPool, name: str) -> list[tuple[Any, ...]]:
    """Run ``sql/queries/<name>.sql`` and return all rows."""
    query = (QUERIES_DIR / f"{name}.sql").read_text(encoding="utf-8")
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def product_ranking(pool: ThreadedConnectionPool) -> list[ProductRank]:
    """Every product ranked by units sold (``RANK()`` window function)."""
    return [ProductRank(*row) for row in _run_query(pool, "product_ranking")]


def revenue_per_customer(pool: ThreadedConnectionPool) -> list[CustomerRevenue]:
    """Every customer with orders, highest revenue first (CTEs)."""
    return [CustomerRevenue(*row) for row in _run_query(pool, "revenue_per_customer")]
