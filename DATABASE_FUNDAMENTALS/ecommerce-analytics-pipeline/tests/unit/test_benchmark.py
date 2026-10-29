"""Tests for the EXPLAIN ANALYZE benchmark (mocked database)."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline.analytics.benchmark import (
    BULK_DATA_FILE,
    DROP_INDEXES_FILE,
    QUERIES,
    BenchmarkResult,
    Plan,
    explain,
    run_benchmark,
)


def _json_plan(node_type: str, ms: float) -> tuple[list[dict[str, object]]]:
    """One row of ``EXPLAIN (FORMAT JSON)`` output, as psycopg2 returns it."""
    return ([{"Plan": {"Node Type": node_type}, "Execution Time": ms}],)


def test_explain_keeps_the_fastest_run() -> None:
    """Each query runs ``RUNS`` times; the fastest plan is kept."""
    cur = MagicMock()
    cur.fetchone.side_effect = [
        _json_plan("Seq Scan", 9.0),
        _json_plan("Seq Scan", 4.0),
        _json_plan("Seq Scan", 7.0),
    ]
    plan = explain(cur, "SELECT 1 WHERE 1 = %s", (1,))
    assert plan == Plan("Seq Scan", 4.0)
    query, params = cur.execute.call_args.args
    assert query == "EXPLAIN (ANALYZE, FORMAT JSON) SELECT 1 WHERE 1 = %s"
    assert params == (1,)


def test_speedup_divides_before_by_after() -> None:
    """10 ms before and 0.5 ms after is 20 times faster."""
    result = BenchmarkResult("q", Plan("Seq Scan", 10.0), Plan("Index Scan", 0.5))
    assert result.speedup == pytest.approx(20.0)


def test_run_benchmark_measures_before_and_after_the_indexes(
    mocker: MockerFixture,
) -> None:
    """Data is loaded and indexes dropped before, and created between runs."""
    calls: list[str] = []
    mocker.patch(
        "ecommerce_pipeline.analytics.benchmark.load_sample_data",
        side_effect=lambda _: calls.append("sample"),
    )
    mocker.patch(
        "ecommerce_pipeline.analytics.benchmark.run_sql_file",
        side_effect=lambda _, path: calls.append(path.name),
    )
    mocker.patch(
        "ecommerce_pipeline.analytics.benchmark.create_indexes",
        side_effect=lambda _: calls.append("indexes"),
    )
    slow, fast = Plan("Seq Scan", 10.0), Plan("Index Scan", 1.0)

    def measure(_: object) -> list[Plan]:
        calls.append("measure")
        return [fast if "indexes" in calls else slow] * len(QUERIES)

    mocker.patch("ecommerce_pipeline.analytics.benchmark._measure", side_effect=measure)
    results = run_benchmark(MagicMock())
    assert calls == [
        "sample",
        BULK_DATA_FILE.name,
        DROP_INDEXES_FILE.name,
        "measure",
        "indexes",
        "measure",
    ]
    assert [r.name for r in results] == list(QUERIES)
    assert all(r.before == slow and r.after == fast for r in results)
