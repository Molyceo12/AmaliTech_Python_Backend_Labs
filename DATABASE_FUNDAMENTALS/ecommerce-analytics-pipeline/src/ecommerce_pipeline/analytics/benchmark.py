"""EXPLAIN ANALYZE before and after the indexes, on thousands of rows."""

import logging
from dataclasses import dataclass
from typing import Any

from psycopg2.extensions import cursor
from psycopg2.extras import Json
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.rows import fetch_value
from ecommerce_pipeline.db.schema import SQL_DIR, create_indexes, run_sql_file
from ecommerce_pipeline.db.seed import load_sample_data

logger = logging.getLogger(__name__)

BULK_DATA_FILE = SQL_DIR / "bulk_data.sql"
DROP_INDEXES_FILE = SQL_DIR / "drop_indexes.sql"
# Run each query a few times and keep the fastest, to reduce noise.
RUNS = 3
# name -> (query, parameters); each one is helped by one index.
QUERIES: dict[str, tuple[str, tuple[Any, ...]]] = {
    "Orders of one customer (B-tree)": (
        "SELECT order_id, created_at FROM orders WHERE customer_id = %s",
        (12345,),
    ),
    "Products by metadata brand (GIN)": (
        "SELECT product_id, name FROM products WHERE metadata @> %s",
        (Json({"brand": "Brand-42"}),),
    ),
}


@dataclass(frozen=True)
class Plan:
    """The top node of a query plan and how long the query took."""

    node_type: str
    ms: float


@dataclass(frozen=True)
class BenchmarkResult:
    """One query measured without and with its index."""

    name: str
    before: Plan
    after: Plan

    @property
    def speedup(self) -> float:
        """How many times faster the query is with the index."""
        return self.before.ms / self.after.ms


def explain(cur: cursor, query: str, params: tuple[Any, ...]) -> Plan:
    """Run ``EXPLAIN ANALYZE`` ``RUNS`` times and return the fastest plan."""
    plans = []
    for _ in range(RUNS):
        # Both parts are constants from this file; values still go as %s params.
        cur.execute("EXPLAIN (ANALYZE, FORMAT JSON) " + query, params)
        result = fetch_value(cur)[0]
        plans.append(Plan(result["Plan"]["Node Type"], result["Execution Time"]))
    return min(plans, key=lambda plan: plan.ms)


def _measure(pool: ThreadedConnectionPool) -> list[Plan]:
    """Explain every benchmark query, in ``QUERIES`` order."""
    with get_connection(pool) as conn, conn.cursor() as cur:
        return [explain(cur, query, params) for query, params in QUERIES.values()]


def run_benchmark(pool: ThreadedConnectionPool) -> list[BenchmarkResult]:
    """Load bulk data, measure without indexes, add them, measure again.

    This replaces all rows with the sample data plus the bulk rows.
    """
    load_sample_data(pool)
    run_sql_file(pool, BULK_DATA_FILE)
    run_sql_file(pool, DROP_INDEXES_FILE)
    before = _measure(pool)
    create_indexes(pool)
    after = _measure(pool)
    results = [
        BenchmarkResult(name, b, a)
        for name, b, a in zip(QUERIES, before, after, strict=True)
    ]
    for result in results:
        logger.info("%s: %.1fx faster", result.name, result.speedup)
    return results
