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
from ecommerce_pipeline.exceptions import EcommerceError
from ecommerce_pipeline.logging_config import configure_logging

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
    print("Tables and indexes created.")


def seed() -> None:
    """Replace all rows with the sample data (run ``setup`` first)."""
    _with_pool(load_sample_data)
    print("Sample data loaded.")


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
    print("Product ranking (RANK() by units sold)")
    for product in ranking:
        print(
            f"  {product.sales_rank:>3}  {product.name:<20}"
            f" {product.units_sold:>6} units {product.revenue:>12}"
        )
    print("\nRevenue per customer (CTEs)")
    for customer in revenue:
        print(
            f"  {customer.name:<20} {customer.order_count:>4} orders"
            f" {customer.revenue:>12}"
        )


def benchmark() -> None:
    """EXPLAIN ANALYZE each query without and with its index (replaces the data)."""
    pool = create_pool(load_settings())
    try:
        results = run_benchmark(pool)
    finally:
        pool.closeall()
    for result in results:
        print(result.name)
        print(f"  before: {result.before.node_type:<18} {result.before.ms:>9.3f} ms")
        print(f"  after:  {result.after.node_type:<18} {result.after.ms:>9.3f} ms")
        print(f"  {result.speedup:.0f}x faster")
    print("Run `ecommerce seed` to go back to the small sample data.")


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
        logger.debug("Command %s failed", args.command, exc_info=True)
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
