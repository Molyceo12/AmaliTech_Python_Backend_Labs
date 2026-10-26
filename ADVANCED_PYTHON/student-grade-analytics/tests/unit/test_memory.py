"""Tests for the memory comparison of collection approaches."""

import pytest

from grade_analytics.utils.memory import (
    MemoryRow,
    compare_list_vs_generator,
    compare_record_sizes,
    format_peaks,
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


def test_format_table_pads_every_column() -> None:
    """Names are left-aligned and numbers right-aligned under their header."""
    table = format_table([MemoryRow("dict", 1_925_176, 192.5)])
    assert table == [
        "Approach | Total (bytes) | Per record (bytes)",
        "---------+---------------+-------------------",
        "dict     |     1,925,176 |              192.5",
    ]


def test_format_peaks_uses_readable_labels() -> None:
    """``list`` and ``generator`` are spelled out in the peak table."""
    table = format_peaks({"list": 1_675_424, "generator": 902})
    assert table[2].startswith("list (load everything first)")
    assert table[3].endswith("902")


def test_main_prints_both_tables_in_boxes(capsys: pytest.CaptureFixture[str]) -> None:
    """The module's main prints both tables inside bordered boxes."""
    main(200)
    printed = capsys.readouterr().out
    assert "Memory for 200 score records" in printed
    assert "generator (one row at a time)" in printed
    assert printed.splitlines()[0] == ":" * 98
