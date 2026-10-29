"""PostgreSQL connection pool, and one transaction per borrowed connection."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.config import Settings
from ecommerce_pipeline.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10


def create_pool(settings: Settings) -> ThreadedConnectionPool:
    """Open a thread-safe pool of PostgreSQL connections.

    Raises:
        DatabaseConnectionError: If PostgreSQL cannot be reached.
    """
    address = f"{settings.postgres_host}:{settings.postgres_port}"
    try:
        pool = ThreadedConnectionPool(
            MIN_CONNECTIONS,
            MAX_CONNECTIONS,
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
        )
    except psycopg2.OperationalError as error:
        raise DatabaseConnectionError(
            f"Cannot connect to PostgreSQL at {address}: {error}"
        ) from error
    logger.info("Opened PostgreSQL pool at %s/%s", address, settings.postgres_db)
    return pool


@contextmanager
def get_connection(pool: ThreadedConnectionPool) -> Iterator[connection]:
    """Borrow a connection: commit if the block succeeds, roll back if it raises."""
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.warning("Transaction rolled back")
        raise
    finally:
        pool.putconn(conn)
