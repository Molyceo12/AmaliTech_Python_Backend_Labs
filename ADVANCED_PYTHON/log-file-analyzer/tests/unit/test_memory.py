"""Tests for the generator vs. list memory comparison."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from log_analyzer.utils import memory
from log_analyzer.utils.memory import (
    Measurement,
    compare,
    container_sizes,
    errors_with_generator,
    errors_with_list,
    format_table,
    make_large_log,
    measure,
)
from tests.helpers import DATA

SOURCE = DATA / "access.log"  # 1,200 lines, 305 errors


@pytest.fixture(name="large_log", scope="module")
def fixture_large_log(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Return a 6,000-line log (5 copies of the sample), built once."""
    target = tmp_path_factory.mktemp("memory") / "large.log"
    make_large_log(SOURCE, target, 5)
    return target


def test_both_approaches_count_the_same_errors() -> None:
    """Same job, same answer."""
    assert errors_with_list(SOURCE) == errors_with_generator(SOURCE) == 305


def test_make_large_log_writes_every_copy(large_log: Path) -> None:
    """5 copies of 1,200 lines."""
    lines = large_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 6000
    assert lines[0] == lines[1200]


def test_make_large_log_needs_at_least_one_copy(tmp_path: Path) -> None:
    """Zero copies is a mistake, not an empty file."""
    with pytest.raises(ValueError, match="at least 1"):
        make_large_log(SOURCE, tmp_path / "x.log", 0)


def test_measure_records_result_memory_and_time(large_log: Path) -> None:
    """A measurement has the job's result, a peak and a time."""
    row = measure("generator", errors_with_generator, large_log)
    assert row.approach == "generator"
    assert row.result == 5 * 305
    assert row.peak_bytes > 0
    assert row.seconds > 0


def test_generator_peak_memory_is_lower_than_the_list(large_log: Path) -> None:
    """Streaming keeps far less in memory than loading everything."""
    list_row, generator_row = compare(large_log)
    assert list_row.result == generator_row.result
    assert generator_row.peak_bytes * 5 < list_row.peak_bytes


def test_compare_rejects_different_answers(
    large_log: Path, mocker: MockerFixture
) -> None:
    """If the two approaches ever disagree, the comparison stops."""
    mocker.patch.object(memory, "errors_with_list", return_value=-1)
    with pytest.raises(AssertionError, match="same errors"):
        compare(large_log)


def test_generator_object_size_does_not_grow(large_log: Path) -> None:
    """The list grows with the file; the generator object does not."""
    small_list, small_generator = container_sizes(SOURCE)
    large_list, large_generator = container_sizes(large_log)
    assert large_list > small_list
    assert large_generator == small_generator


def test_format_table() -> None:
    """A Markdown table with one row per approach."""
    rows = [Measurement("list", 1500, 2048, 0.5), Measurement("gen", 1500, 1024, 0.4)]
    assert format_table(rows).splitlines() == [
        "| Approach | Errors counted | Peak memory | Time |",
        "|---|---:|---:|---:|",
        "| list | 1,500 | 2 KiB | 0.500 s |",
        "| gen | 1,500 | 1 KiB | 0.400 s |",
    ]


def test_main_prints_the_comparison(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The demo builds the log, then prints the table and the size line."""
    target = tmp_path / "out" / "large.log"
    memory.main(["--copies", "2", "--target", str(target)])
    printed = capsys.readouterr().out
    assert "Counting errors in 2,400 log lines" in printed
    assert "| generator (line by line) | 610 |" in printed
    assert "less memory" in printed
    assert "generator object" in printed
