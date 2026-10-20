"""Grouping students with ``defaultdict``."""

from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, List

from grade_analytics.models import Student


def group_by_major(students: Iterable[Student]) -> Dict[str, List[Student]]:
    """Group students by their major.

    Args:
        students: Students to group.

    Returns:
        Major → students in that major, in input order.
    """
    groups: defaultdict[str, List[Student]] = defaultdict(list)
    for student in students:
        groups[student.major].append(student)
    return dict(groups)


def group_by_year(students: Iterable[Student]) -> Dict[int, List[Student]]:
    """Group students by their year of study.

    Args:
        students: Students to group.

    Returns:
        Year → students in that year, in input order.
    """
    groups: defaultdict[int, List[Student]] = defaultdict(list)
    for student in students:
        groups[student.year].append(student)
    return dict(groups)


def scores_by_semester(students: Iterable[Student]) -> Dict[str, List[float]]:
    """Collect every score per semester.

    Args:
        students: Students whose grades are collected.

    Returns:
        Semester → all scores given in that semester.
    """
    scores: defaultdict[str, List[float]] = defaultdict(list)
    for student in students:
        for grade in student.grades:
            scores[grade.semester].append(grade.score)
    return dict(scores)
