"""Command line entry point: ``ecommerce <command>``."""

import argparse
import logging
import sys
from collections.abc import Callable

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.pool import create_pool
from ecommerce_pipeline.db.schema import create_tables
from ecommerce_pipeline.db.seed import load_sample_data
from ecommerce_pipeline.exceptions import EcommerceError
from ecommerce_pipeline.logging_config import configure_logging

logger = logging.getLogger(__name__)


def _with_pool(action: Callable[[ThreadedConnectionPool], None]) -> None:
    """Open a pool, run ``action`` with it, and always close the pool."""
    pool = create_pool(load_settings())
    try:
        action(pool)
    finally:
        pool.closeall()


def setup() -> None:
    """Create the tables in PostgreSQL."""
    _with_pool(create_tables)
    print("Tables created.")


def seed() -> None:
    """Replace all rows with the sample data (run ``setup`` first)."""
    _with_pool(load_sample_data)
    print("Sample data loaded.")


COMMANDS: dict[str, Callable[[], None]] = {"setup": setup, "seed": seed}


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
