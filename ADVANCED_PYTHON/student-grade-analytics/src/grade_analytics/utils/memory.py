"""Memory comparison of collection approaches.

Run ``python -m grade_analytics.utils.memory`` to print the tables used in
the README's performance notes.
"""

import sys
import tracemalloc
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple

from grade_analytics.models import ScoreRecord


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


def format_table(rows: List[MemoryRow]) -> str:
    """Render memory rows as a Markdown table."""
    lines = [
        "| Approach | Total (bytes) | Per record (bytes) |",
        "|---|---:|---:|",
    ]
    lines += [
        f"| {row.approach} | {row.total_bytes:,} | {row.bytes_per_item:g} |"
        for row in rows
    ]
    return "\n".join(lines)


def main(count: int = 10_000) -> None:
    """Print both comparisons as Markdown tables."""
    print(f"Memory for {count:,} score records\n")
    print(format_table(compare_record_sizes(count)))
    peaks = compare_list_vs_generator(count)
    print(f"\nPeak memory averaging {count:,} scores\n")
    print("| Approach | Peak (bytes) |\n|---|---:|")
    for name, peak in peaks.items():
        print(f"| {name} | {peak:,} |")


if __name__ == "__main__":
    main()
