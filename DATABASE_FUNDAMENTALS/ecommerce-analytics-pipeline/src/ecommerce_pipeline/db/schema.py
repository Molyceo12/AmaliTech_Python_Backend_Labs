"""Run SQL files: the tables (``schema.sql``) and their indexes (``indexes.sql``)."""

import logging
from pathlib import Path

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection

logger = logging.getLogger(__name__)

SQL_DIR = Path(__file__).resolve().parents[3] / "sql"
SCHEMA_FILE = SQL_DIR / "schema.sql"
INDEXES_FILE = SQL_DIR / "indexes.sql"


def run_sql_file(pool: ThreadedConnectionPool, path: Path) -> None:
    """Run every statement in ``path`` in one transaction."""
    sql = path.read_text(encoding="utf-8")
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(sql)
    logger.info("Ran %s", path.name)


def create_tables(pool: ThreadedConnectionPool) -> None:
    """Create the tables (safe to run again)."""
    run_sql_file(pool, SCHEMA_FILE)


def create_indexes(pool: ThreadedConnectionPool) -> None:
    """Create the B-tree and GIN indexes (safe to run again)."""
    run_sql_file(pool, INDEXES_FILE)
