"""Create the tables by running ``sql/schema.sql``."""

import logging
from pathlib import Path

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection

logger = logging.getLogger(__name__)

SCHEMA_FILE = Path(__file__).resolve().parents[3] / "sql" / "schema.sql"


def create_tables(pool: ThreadedConnectionPool) -> None:
    """Run the schema DDL in one transaction (safe to run again)."""
    ddl = SCHEMA_FILE.read_text(encoding="utf-8")
    with get_connection(pool) as conn, conn.cursor() as cursor:
        cursor.execute(ddl)
    logger.info("Tables created from %s", SCHEMA_FILE.name)
