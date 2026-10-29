"""Integration test: the indexes change the plans on the bulk data."""

from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.analytics.benchmark import run_benchmark


def test_indexes_replace_sequential_scans(clean_pool: ThreadedConnectionPool) -> None:
    """Without indexes PostgreSQL reads every row; with them it uses the index."""
    for result in run_benchmark(clean_pool):
        assert result.before.node_type == "Seq Scan", result.name
        assert result.after.node_type != "Seq Scan", result.name
