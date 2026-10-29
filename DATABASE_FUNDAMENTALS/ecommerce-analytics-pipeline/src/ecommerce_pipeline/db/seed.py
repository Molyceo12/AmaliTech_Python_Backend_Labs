"""Load the sample data from ``sql/sample_data.sql``."""

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.schema import SQL_DIR, run_sql_file

SAMPLE_DATA_FILE = SQL_DIR / "sample_data.sql"


def load_sample_data(pool: ThreadedConnectionPool) -> None:
    """Replace all rows with the sample data (safe to run again)."""
    run_sql_file(pool, SAMPLE_DATA_FILE)
