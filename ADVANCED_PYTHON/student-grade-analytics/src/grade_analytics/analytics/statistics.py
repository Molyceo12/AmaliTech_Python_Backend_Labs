"""Basic statistics: mean, median, mode and percentile rank."""

from collections import Counter
from collections.abc import Sequence
from typing import Optional

from grade_analytics.models import StatisticsSummary


def mean(scores: Sequence[float]) -> Optional[float]:
    """Return the average score, or ``None`` when there are no scores."""
    if not scores:
        return None
    return sum(scores) / len(scores)


def median(scores: Sequence[float]) -> Optional[float]:
    """Return the middle score (average of the two middle ones for an even count).

    Args:
        scores: Scores in any order.

    Returns:
        The median, or ``None`` when there are no scores.
    """
    if not scores:
        return None
    ordered = sorted(scores)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def mode(scores: Sequence[float]) -> Optional[float]:
    """Return the most common score, counted with ``Counter``.

    Args:
        scores: Scores in any order.

    Returns:
        The most common score; the highest one when several tie. ``None``
        when there are no scores or every score appears exactly once
        (more than one score).
    """
    counts = Counter(scores)
    if not counts:
        return None
    top = max(counts.values())
    if top == 1 and len(counts) > 1:
        return None
    return max(score for score, count in counts.items() if count == top)


def percentile_rank(score: float, scores: Sequence[float]) -> float:
    """Return the percentage of scores that are lower than or equal to ``score``.

    Args:
        score: The score to rank.
        scores: All scores it is compared with.

    Returns:
        Percentile rank from 0 to 100, rounded to 1 decimal.

    Raises:
        ValueError: If ``scores`` is empty.
    """
    if not scores:
        raise ValueError("cannot rank against an empty list of scores")
    at_or_below = sum(1 for other in scores if other <= score)
    return round(100 * at_or_below / len(scores), 1)


def _rounded(value: Optional[float]) -> Optional[float]:
    """Round to 2 decimals for the report, keeping ``None``."""
    return None if value is None else round(value, 2)


def summarize(scores: Sequence[float]) -> StatisticsSummary:
    """Build the statistics section of the report.

    Args:
        scores: Every score in the data set.

    Returns:
        Count, mean, median, mode, lowest and highest score (2 decimals).
    """
    return {
        "count": len(scores),
        "mean": _rounded(mean(scores)),
        "median": _rounded(median(scores)),
        "mode": _rounded(mode(scores)),
        "lowest": min(scores) if scores else None,
        "highest": max(scores) if scores else None,
    }
