"""Memory comparison of collection approaches.

Run ``python -m grade_analytics.utils.memory`` to print the tables used in
the README's performance notes.
"""

import sys
import tracemalloc
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple

from grade_analytics.console import border, box_header, boxed
from grade_analytics.models import ScoreRecord

PEAK_LABELS = {
    "list": "list (load everything first)",
    "generator": "generator (one row at a time)",
}


@dataclass
class DataclassRecord:
    """A score record as a normal dataclass (keeps a per-object ``__dict__``)."""

    student_id: str
    course_code: str
    semester: str
    score: float


@dataclass(slots=True)
class SlotsRecord:
    """A score record as a ``slots=True`` dataclass (no per-object ``__dict__``)."""

    student_id: str
    course_code: str
    semester: str
    score: float


class MemoryRow(NamedTuple):
    """One line of a memory table."""

    approach: str
    total_bytes: int
    bytes_per_item: float


FIELDS = ("S001", "CS101", "2026-S1", 88.0)

# Builders for one record in each storage style, all holding the same values.
BUILDERS: Dict[str, Callable[[], Any]] = {
    "dict": lambda: dict(
        zip(("student_id", "course_code", "semester", "score"), FIELDS, strict=True)
    ),
    "tuple": lambda: FIELDS,
    "namedtuple (ScoreRecord)": lambda: ScoreRecord(*FIELDS),
    "dataclass": lambda: DataclassRecord(*FIELDS),
    "dataclass(slots=True)": lambda: SlotsRecord(*FIELDS),
}


def object_size(obj: object) -> int:
    """Size of one record object, including its ``__dict__`` if it has one.

    Field values are shared between records, so only the container cost is
    counted: that is what differs between the approaches.
    """
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(vars(obj))
    return size


def compare_record_sizes(count: int = 10_000) -> List[MemoryRow]:
    """Measure ``count`` records stored as dict, tuple, namedtuple and dataclasses.

    Args:
        count: Number of records to build per approach.

    Returns:
        One row per approach, smallest first.
    """
    rows = []
    for name, build in BUILDERS.items():
        if name == "tuple":  # build real copies, not one shared tuple
            records: List[Any] = [tuple(list(FIELDS)) for _ in range(count)]
        else:
            records = [build() for _ in range(count)]
        total = sys.getsizeof(records) + sum(object_size(r) for r in records)
        rows.append(MemoryRow(name, total, round(total / count, 1)))
    return sorted(rows, key=lambda row: row.total_bytes)


def _records(count: int) -> Iterator[ScoreRecord]:
    """Yield ``count`` score records one at a time (like the CSV reader)."""
    for index in range(count):
        yield ScoreRecord(f"S{index:05d}", "CS101", "2026-S1", float(index % 100))


def _peak_bytes(work: Callable[[], float]) -> int:
    """Run ``work`` and return the peak memory it allocated (``tracemalloc``)."""
    tracemalloc.start()
    try:
        work()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak


def compare_list_vs_generator(count: int = 10_000) -> Dict[str, int]:
    """Peak memory of averaging scores from a full list vs a generator.

    Args:
        count: Number of records processed.

    Returns:
        ``{"list": peak_bytes, "generator": peak_bytes}``.
    """

    def with_list() -> float:
        records = list(_records(count))
        return float(sum(record.score for record in records)) / count

    def with_generator() -> float:
        return float(sum(record.score for record in _records(count))) / count

    return {"list": _peak_bytes(with_list), "generator": _peak_bytes(with_generator)}


def aligned_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    """Return a text table with padded columns, one string per line.

    The first column is left-aligned and the number columns right-aligned,
    e.g. ``"dict                  |   1,925,176 |  192.5"``.
    """
    widths = [max(map(len, column)) for column in zip(headers, *rows, strict=True)]

    def line(cells: Sequence[str]) -> str:
        first, *numbers = cells
        padded = [
            cell.rjust(width) for cell, width in zip(numbers, widths[1:], strict=True)
        ]
        return " | ".join([first.ljust(widths[0]), *padded])

    rule = "-+-".join("-" * width for width in widths)
    return [line(headers), rule, *(line(row) for row in rows)]


def format_table(rows: List[MemoryRow]) -> List[str]:
    """Render the record sizes as an aligned table."""
    return aligned_table(
        ["Approach", "Total (bytes)", "Per record (bytes)"],
        [
            [row.approach, f"{row.total_bytes:,}", f"{row.bytes_per_item:g}"]
            for row in rows
        ],
    )


def format_peaks(peaks: Dict[str, int]) -> List[str]:
    """Render the list vs generator peaks as an aligned table."""
    return aligned_table(
        ["Approach", "Peak (bytes)"],
        [[PEAK_LABELS.get(name, name), f"{peak:,}"] for name, peak in peaks.items()],
    )


def _box(title: str, table: List[str]) -> str:
    """Put a table inside a bordered box with a title."""
    body = [boxed(), *map(boxed, table), boxed()]
    return "\n".join([box_header(title), *body, border()])


def main(count: int = 10_000) -> None:
    """Print both comparisons as aligned tables in bordered boxes."""
    sizes = format_table(compare_record_sizes(count))
    peaks = format_peaks(compare_list_vs_generator(count))
    print(_box(f"Memory for {count:,} score records", sizes))
    print()
    print(_box(f"Peak memory averaging {count:,} scores", peaks))


if __name__ == "__main__":
    main()
