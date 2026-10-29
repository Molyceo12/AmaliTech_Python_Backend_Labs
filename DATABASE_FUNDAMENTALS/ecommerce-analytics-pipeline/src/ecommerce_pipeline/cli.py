"""Command line entry point: ``ecommerce <command>``."""

import argparse
import logging
import sys
from collections.abc import Callable

from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.db.pool import create_pool
from ecommerce_pipeline.db.schema import create_tables
from ecommerce_pipeline.exceptions import EcommerceError
from ecommerce_pipeline.logging_config import configure_logging

logger = logging.getLogger(__name__)


def setup() -> None:
    """Create the tables in PostgreSQL."""
    pool = create_pool(load_settings())
    try:
        create_tables(pool)
    finally:
        pool.closeall()
    print("Tables created.")


COMMANDS: dict[str, Callable[[], None]] = {"setup": setup}


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
