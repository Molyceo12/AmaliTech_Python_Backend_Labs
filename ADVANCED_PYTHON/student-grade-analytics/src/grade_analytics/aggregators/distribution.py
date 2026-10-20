"""Grade distribution with ``Counter``."""

from collections import Counter
from collections.abc import Iterable

from grade_analytics.models import Grade

LETTERS = ("A", "B", "C", "D", "F")


def grade_distribution(grades: Iterable[Grade]) -> Counter[str]:
    """Count how many grades fall in each letter band.

    Args:
        grades: Grades to count.

    Returns:
        A ``Counter`` mapping letter (A–F) to count; every letter is present,
        even with a count of 0, so reports always show all bands.
    """
    counts: Counter[str] = Counter(dict.fromkeys(LETTERS, 0))
    counts.update(grade.letter for grade in grades)
    return counts
