"""Command line entry point: ``ecommerce <command>``."""

import argparse
import logging
import sys
from collections.abc import Callable
from contextlib import ExitStack

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.analytics.benchmark import run_benchmark
from ecommerce_pipeline.analytics.reports import product_ranking, revenue_per_customer
from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.nosql import create_mongo, create_redis
from ecommerce_pipeline.db.pool import create_pool
from ecommerce_pipeline.db.schema import create_indexes, create_tables
from ecommerce_pipeline.db.seed import load_sample_data
from ecommerce_pipeline.demo import run_demo
from ecommerce_pipeline.display import print_table
from ecommerce_pipeline.exceptions import EcommerceError
from ecommerce_pipeline.logging_config import FILE_ONLY, configure_logging

logger = logging.getLogger(__name__)

# Reports print this many rows of each table.
TOP = 10


def _with_pool(*actions: Callable[[ThreadedConnectionPool], None]) -> None:
    """Open a pool, run each action with it, and always close the pool."""
    pool = create_pool(load_settings())
    try:
        for action in actions:
            action(pool)
    finally:
        pool.closeall()


def setup() -> None:
    """Create the tables and their indexes in PostgreSQL."""
    _with_pool(create_tables, create_indexes)
    print_table("ecommerce setup", ["result"], [["Tables and indexes created."]])


def seed() -> None:
    """Replace all rows with the sample data (run ``setup`` first)."""
    _with_pool(load_sample_data)
    print_table("ecommerce seed", ["result"], [["Sample data loaded."]])


def demo() -> None:
    """Show PostgreSQL, JSONB, Redis and MongoDB working together."""
    settings = load_settings()
    # ExitStack closes every connection that was opened, even on errors.
    with ExitStack() as stack:
        pool = create_pool(settings)
        stack.callback(pool.closeall)
        cache = create_redis(settings)
        stack.callback(cache.close)
        mongo = create_mongo(settings)
        stack.callback(mongo.client.close)
        run_demo(pool, cache, mongo)


def report() -> None:
    """Print the top 10 of the product ranking and of revenue per customer."""
    pool = create_pool(load_settings())
    try:
        ranking = product_ranking(pool)[:TOP]
        revenue = revenue_per_customer(pool)[:TOP]
    finally:
        pool.closeall()
    print_table(
        "Product ranking (RANK() by units sold)",
        ["rank", "product", "units", "revenue"],
        [[p.sales_rank, p.name, p.units_sold, p.revenue] for p in ranking],
    )
    print_table(
        "\nRevenue per customer (CTEs)",
        ["customer", "orders", "revenue"],
        [[c.name, c.order_count, c.revenue] for c in revenue],
    )


def benchmark() -> None:
    """EXPLAIN ANALYZE each query without and with its index (replaces the data)."""
    pool = create_pool(load_settings())
    try:
        results = run_benchmark(pool)
    finally:
        pool.closeall()
    print_table(
        "EXPLAIN ANALYZE without and with the index",
        ["query", "before", "ms", "after", "ms", "speedup"],
        [
            [
                r.name,
                r.before.node_type,
                round(r.before.ms, 3),
                r.after.node_type,
                round(r.after.ms, 3),
                f"{r.speedup:.0f}x faster",
            ]
            for r in results
        ],
    )
    print_table(
        "\nNext step",
        ["note"],
        [["Run `ecommerce seed` to go back to the small sample data."]],
    )


COMMANDS: dict[str, Callable[[], None]] = {
    "setup": setup,
    "seed": seed,
    "demo": demo,
    "report": report,
    "benchmark": benchmark,
}


def main(argv: list[str] | None = None) -> int:
    """Run one command and return the exit code (0 ok, 1 error)."""
    parser = argparse.ArgumentParser(
        prog="ecommerce", description="E-commerce analytics pipeline"
    )
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        configure_logging(verbose=args.verbose)
        COMMANDS[args.command]()
    except EcommerceError as error:
        # ERROR with the traceback in the log file; the terminal gets the table.
        logger.error(
            "Command %s failed: %s",
            args.command,
            error,
            exc_info=True,
            extra={FILE_ONLY: True},
        )
        print_table(
            "Error", ["command", "message"], [[args.command, error]], file=sys.stderr
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
