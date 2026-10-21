"""Generator vs. list: the same job done two ways, with memory and time measured.

The job is to count the error responses (4xx/5xx) in a log file.

Run ``python -m log_analyzer.utils.memory --copies 100`` to build a large log
in ``output/`` and print the tables used in the README.
"""

import argparse
import sys
import time
import tracemalloc
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import NamedTuple

from log_analyzer.parsing import parse_line, parse_timestamp
from log_analyzer.pipeline import count_requests, only_errors, parse_entries, select
from log_analyzer.readers import read_lines

DATA = Path(__file__).resolve().parents[3] / "data"
DEFAULT_SOURCE = DATA / "access.log"
DEFAULT_TARGET = Path("output/large_access.log")
DEFAULT_COPIES = 100

Job = Callable[[Path], int]


class Measurement(NamedTuple):
    """How one approach did on the same file."""

    approach: str
    result: int  # error responses counted
    peak_bytes: int  # highest memory use while running
    seconds: float


def errors_with_list(path: Path) -> int:
    """Count errors after loading every line and every entry into lists."""
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = [entry for entry in map(parse_line, lines) if entry is not None]
    return len([entry for entry in entries if entry.is_error])


def errors_with_generator(path: Path) -> int:
    """Count errors one line at a time: nothing is kept after it is counted."""
    return count_requests(select(only_errors, parse_entries(read_lines(path))))


def measure(approach: str, job: Job, path: Path) -> Measurement:
    """Run ``job`` on ``path`` twice: once for the time, once for peak memory.

    ``tracemalloc`` slows Python down a lot, so the time comes from a separate
    run without it. The timestamp cache is cleared before each run so neither
    approach starts warm.
    """
    parse_timestamp.cache_clear()
    start = time.perf_counter()
    result = job(path)
    seconds = time.perf_counter() - start

    parse_timestamp.cache_clear()
    tracemalloc.start()
    try:
        job(path)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return Measurement(approach, result, peak, seconds)


def compare(path: Path) -> list[Measurement]:
    """Measure both approaches on the same file.

    Raises:
        AssertionError: If the two approaches disagree (they must not).
    """
    rows = [
        measure("list (load everything)", errors_with_list, path),
        measure("generator (line by line)", errors_with_generator, path),
    ]
    if rows[0].result != rows[1].result:
        raise AssertionError("both approaches must count the same errors")
    return rows


def container_sizes(path: Path) -> tuple[int, int]:
    """Return ``sys.getsizeof`` of a list of all entries and of a generator.

    The list grows with the file; the generator object stays the same size.
    """
    entries = list(parse_entries(read_lines(path)))
    generator = parse_entries(read_lines(path))
    return sys.getsizeof(entries), sys.getsizeof(generator)


def make_large_log(source: Path, target: Path, copies: int) -> int:
    """Write ``source`` ``copies`` times into ``target``; return the lines written.

    Lines are copied one at a time from a generator, so even this helper
    never holds the large file in memory.

    Raises:
        ValueError: If ``copies`` is less than 1.
    """
    if copies < 1:
        raise ValueError("copies must be at least 1")
    target.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for _ in range(copies):
            for line in read_lines(source):
                handle.write(f"{line}\n")
                written += 1
    return written


def format_table(rows: Sequence[Measurement]) -> str:
    """Render the measurements as a Markdown table."""
    lines = [
        "| Approach | Errors counted | Peak memory | Time |",
        "|---|---:|---:|---:|",
    ]
    lines += [
        f"| {row.approach} | {row.result:,} | {row.peak_bytes / 1024:,.0f} KiB "
        f"| {row.seconds:.3f} s |"
        for row in rows
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> None:
    """Build a large log, compare both approaches and print the tables."""
    parser = argparse.ArgumentParser(description="Generator vs. list comparison.")
    parser.add_argument("--copies", type=int, default=DEFAULT_COPIES)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args(argv)

    lines = make_large_log(args.source, args.target, args.copies)
    print(f"Counting errors in {lines:,} log lines ({args.target})\n")
    rows = compare(args.target)
    print(format_table(rows))
    list_peak, generator_peak = rows[0].peak_bytes, rows[1].peak_bytes
    print(f"\nThe generator used {list_peak / generator_peak:,.0f}x less memory.")
    list_size, generator_size = container_sizes(args.target)
    print(
        f"sys.getsizeof: list of entries {list_size:,} bytes, "
        f"generator object {generator_size:,} bytes"
    )


if __name__ == "__main__":
    main()
