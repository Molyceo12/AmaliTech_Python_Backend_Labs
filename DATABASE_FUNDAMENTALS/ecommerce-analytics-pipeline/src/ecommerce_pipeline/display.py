"""Print rows as a table framed with ``:`` lines."""

import textwrap
from collections.abc import Sequence
from decimal import Decimal
from typing import Any, TextIO

BORDER = ":"
NUMBERS = (int, float, Decimal)
# Every table is this wide, so they line up in the terminal.
TABLE_WIDTH = 100
# A wrapped column never gets narrower than this.
MIN_WIDTH = 10


def _widths(cells: list[list[str]]) -> list[int]:
    """Column widths that make the table ``TABLE_WIDTH`` wide (borders included)."""
    count = len(cells[0])
    widths = [max(len(row[i]) for row in cells) for i in range(count)]
    extra = TABLE_WIDTH - (3 * count + 1) - sum(widths)
    if extra < 0:
        # Too wide: the widest column wraps onto more lines.
        widest = widths.index(max(widths))
        widths[widest] = max(widths[widest] + extra, MIN_WIDTH)
        return widths
    # Too narrow: share the space left between the columns.
    return [
        width + extra // count + (i < extra % count) for i, width in enumerate(widths)
    ]


def _row_lines(row: list[str], widths: list[int], right: list[bool]) -> list[str]:
    """One table row; a long cell wraps onto extra lines."""
    wrapped = [
        textwrap.wrap(cell, width) or [""]
        for cell, width in zip(row, widths, strict=True)
    ]
    lines = []
    for k in range(max(len(parts) for parts in wrapped)):
        texts = [parts[k] if k < len(parts) else "" for parts in wrapped]
        padded = [
            text.rjust(width) if is_right else text.ljust(width)
            for text, width, is_right in zip(texts, widths, right, strict=True)
        ]
        lines.append(f"{BORDER} " + f" {BORDER} ".join(padded) + f" {BORDER}")
    return lines


def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Return the table as text; number columns are aligned to the right."""
    cells = [list(headers), *[[str(value) for value in row] for row in rows]]
    widths = _widths(cells)
    right = [
        bool(rows) and all(isinstance(row[i], NUMBERS) for row in rows)
        for i in range(len(headers))
    ]
    header = _row_lines(cells[0], widths, right)
    body = [line for row in cells[1:] for line in _row_lines(row, widths, right)]
    rule = BORDER * len(header[0])
    return "\n".join([rule, *header, rule, *([*body, rule] if rows else [])])


def print_table(
    title: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    file: TextIO | None = None,
) -> None:
    """Print a title, then the table under it (to stdout unless ``file`` is set)."""
    print(title, file=file)
    print(format_table(headers, rows), file=file)
