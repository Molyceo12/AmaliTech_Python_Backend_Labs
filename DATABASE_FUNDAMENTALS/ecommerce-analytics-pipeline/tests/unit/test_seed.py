"""Tests for loading the sample data."""

from unittest.mock import MagicMock

from ecommerce_pipeline.db.seed import SAMPLE_DATA_FILE, load_sample_data


def test_sample_data_file_empties_then_fills_every_table() -> None:
    """The file truncates first, then inserts into all four tables."""
    sql = SAMPLE_DATA_FILE.read_text(encoding="utf-8")
    assert sql.index("TRUNCATE") < sql.index("INSERT")
    for table in ("customers", "products", "orders", "order_items"):
        assert f"INSERT INTO {table} " in sql


def test_load_sample_data_runs_the_file(fake_pool: MagicMock) -> None:
    """The whole sample data file is executed and committed."""
    load_sample_data(fake_pool)
    fake_pool.cursor.execute.assert_called_once_with(
        SAMPLE_DATA_FILE.read_text(encoding="utf-8")
    )
    fake_pool.getconn.return_value.commit.assert_called_once()
