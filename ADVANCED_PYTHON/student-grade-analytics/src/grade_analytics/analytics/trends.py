"""Grade trends over semesters, smoothed with a ``deque`` rolling average."""

from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import List, Optional

from grade_analytics.aggregators import RollingAverage
from grade_analytics.models import ScoreRecord, SemesterTrend, Student


def score_records(students: Iterable[Student]) -> Iterator[ScoreRecord]:
    """Yield one lightweight ``ScoreRecord`` per grade (a generator).

    Args:
        students: Students whose grades are flattened.

    Yields:
        ``ScoreRecord(student_id, course_code, semester, score)``.
    """
    for student in students:
        for grade in student.grades:
            yield ScoreRecord(
                student.student_id, grade.course_code, grade.semester, grade.score
            )


def semester_trends(
    records: Iterable[ScoreRecord], window: int = 3
) -> List[SemesterTrend]:
    """Average score per semester, with a rolling average and the change.

    Semesters are sorted by label (``"2025-S2"`` < ``"2026-S1"``). The
    rolling average covers the last ``window`` semesters, kept in a
    ``deque(maxlen=window)`` by ``RollingAverage``.

    Args:
        records: Score records, e.g. from ``score_records``.
        window: How many semesters the rolling average covers.

    Returns:
        One trend entry per semester, oldest first.

    Raises:
        ValueError: If ``window`` is less than 1.
    """
    rolling = RollingAverage(window)
    by_semester: defaultdict[str, List[float]] = defaultdict(list)
    for record in records:
        by_semester[record.semester].append(record.score)

    trends: List[SemesterTrend] = []
    previous: Optional[float] = None
    for semester in sorted(by_semester):
        scores = by_semester[semester]
        average = sum(scores) / len(scores)
        trends.append(
            {
                "semester": semester,
                "grades": len(scores),
                "average": round(average, 2),
                "rolling_average": round(rolling.add(average), 2),
                "change": None if previous is None else round(average - previous, 2),
            }
        )
        previous = average
    return trends
