"""Everything loaded from a data file."""

from dataclasses import dataclass
from typing import Dict, List

from grade_analytics.models.course import Course
from grade_analytics.models.problem import RowProblem
from grade_analytics.models.student import Student


@dataclass(frozen=True)
class LoadedData:
    """Students, courses and skipped rows from one data file.

    Attributes:
        students: Students with their grades, in first-seen order.
        courses: Course code → course, in first-seen order.
        problems: Rows that were skipped, and why.
    """

    students: List[Student]
    courses: Dict[str, Course]
    problems: List[RowProblem]
