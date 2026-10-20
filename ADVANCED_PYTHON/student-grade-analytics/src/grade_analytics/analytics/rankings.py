"""Ranking students by average score."""

from collections.abc import Iterable, Sequence
from typing import List, NamedTuple

from grade_analytics.analytics.statistics import percentile_rank
from grade_analytics.models import Student


class RankedStudent(NamedTuple):
    """A student with their place in the ranking.

    Attributes:
        rank: 1 for the best average; tied averages share a rank.
        student: The student.
        average: Their average score.
        percentile: Percentile rank of their average among all averages.
    """

    rank: int
    student: Student
    average: float
    percentile: float


def rank_students(students: Iterable[Student]) -> List[RankedStudent]:
    """Rank students by average score, highest first.

    Uses competition ranking: tied averages share a rank and the next rank
    skips ahead (1, 2, 2, 4). Students without grades are left out.

    Args:
        students: Students to rank.

    Returns:
        Ranked students, best first; ties keep their input order.
    """
    scored = [
        (student, student.average)
        for student in students
        if student.average is not None
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    averages = [average for _, average in scored]
    ranked: List[RankedStudent] = []
    for position, (student, average) in enumerate(scored, start=1):
        tied = bool(ranked) and average == ranked[-1].average
        rank = ranked[-1].rank if tied else position
        percentile = percentile_rank(average, averages)
        ranked.append(RankedStudent(rank, student, average, percentile))
    return ranked


def top_performers(ranked: Sequence[RankedStudent], n: int) -> List[RankedStudent]:
    """Return the best ``n`` students, plus anyone tied with the n-th.

    Args:
        ranked: Output of ``rank_students``.
        n: How many places to keep.

    Returns:
        The top students (may be more than ``n`` because of ties).

    Raises:
        ValueError: If ``n`` is less than 1.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    if len(ranked) <= n:
        return list(ranked)
    cutoff = ranked[n - 1].rank
    return [entry for entry in ranked if entry.rank <= cutoff]
