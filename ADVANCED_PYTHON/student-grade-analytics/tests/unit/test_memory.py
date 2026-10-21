"""Tests for the memory comparison of collection approaches."""

import pytest

from grade_analytics.utils.memory import (
    MemoryRow,
    compare_list_vs_generator,
    compare_record_sizes,
    format_table,
    main,
)


def test_record_sizes_are_ordered_smallest_first() -> None:
    """slots dataclass is smallest, dict is largest, namedtuple equals tuple."""
    rows = {row.approach: row for row in compare_record_sizes(500)}
    sizes = [row.total_bytes for row in compare_record_sizes(500)]
    assert sizes == sorted(sizes)
    assert rows["dataclass(slots=True)"].total_bytes < rows["dataclass"].total_bytes
    assert rows["dataclass"].total_bytes < rows["dict"].total_bytes
    assert rows["namedtuple (ScoreRecord)"].total_bytes == rows["tuple"].total_bytes


def test_generator_peak_is_much_lower_than_list() -> None:
    """Streaming records keeps peak memory far below loading them all."""
    peaks = compare_list_vs_generator(2_000)
    assert peaks["generator"] * 10 < peaks["list"]


def test_format_table() -> None:
    """Rows become a Markdown table with thousands separators."""
    table = format_table([MemoryRow("dict", 1_925_176, 192.5)])
    assert table.splitlines() == [
        "| Approach | Total (bytes) | Per record (bytes) |",
        "|---|---:|---:|",
        "| dict | 1,925,176 | 192.5 |",
    ]


def test_main_prints_both_tables(capsys: pytest.CaptureFixture[str]) -> None:
    """The module's main prints the size table and the peak table."""
    main(200)
    printed = capsys.readouterr().out
    assert "Memory for 200 score records" in printed
    assert "| generator |" in printed
