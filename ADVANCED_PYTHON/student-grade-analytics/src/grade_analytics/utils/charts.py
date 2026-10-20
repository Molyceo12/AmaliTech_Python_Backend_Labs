"""Text charts for the terminal (no plotting library needed)."""

from collections.abc import Mapping

BAR = "#"


def bar_chart(counts: Mapping[str, int], width: int = 40) -> str:
    """Draw a horizontal bar chart, one line per label.

    Bars are scaled so the largest count is ``width`` characters long.

    Args:
        counts: Label → count, drawn in this order.
        width: Length of the longest bar.

    Returns:
        The chart as text, e.g. ``"A | ######## 4"``; empty for no labels.
    """
    if not counts:
        return ""
    label_width = max(len(label) for label in counts)
    largest = max(counts.values())
    lines = []
    for label, count in counts.items():
        length = round(width * count / largest) if largest else 0
        bar_and_count = f"{BAR * length} {count}" if length else str(count)
        lines.append(f"{label.ljust(label_width)} | {bar_and_count}")
    return "\n".join(lines)
