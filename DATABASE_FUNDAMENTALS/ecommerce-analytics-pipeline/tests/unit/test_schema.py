"""Tests for creating the tables."""

from unittest.mock import MagicMock

from ecommerce_pipeline.db.schema import (
    INDEXES_FILE,
    SCHEMA_FILE,
    create_indexes,
    create_tables,
)


def test_schema_file_defines_the_four_tables() -> None:
    """``sql/schema.sql`` exists and creates every table."""
    ddl = SCHEMA_FILE.read_text(encoding="utf-8")
    for table in ("customers", "products", "orders", "order_items"):
        assert f"CREATE TABLE IF NOT EXISTS {table} " in ddl


def test_create_tables_runs_the_schema_file() -> None:
    """The whole DDL file is executed on a pooled connection."""
    pool = MagicMock()
    create_tables(pool)
    cursor = pool.getconn.return_value.cursor.return_value.__enter__.return_value
    cursor.execute.assert_called_once_with(SCHEMA_FILE.read_text(encoding="utf-8"))
    pool.getconn.return_value.commit.assert_called_once()


def test_create_indexes_runs_the_indexes_file() -> None:
    """The B-tree and GIN index file is executed and committed."""
    pool = MagicMock()
    create_indexes(pool)
    cursor = pool.getconn.return_value.cursor.return_value.__enter__.return_value
    sql = INDEXES_FILE.read_text(encoding="utf-8")
    cursor.execute.assert_called_once_with(sql)
    assert "USING GIN (metadata)" in sql
