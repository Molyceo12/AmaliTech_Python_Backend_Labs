"""Typed structure of the JSON report (``TypedDict``)."""

from typing import Dict, List, Optional, TypedDict


class StudentSummary(TypedDict):
    """One student's line in the report."""

    student_id: str
    name: str
    major: str
    average: Optional[float]
    percentile: Optional[float]


class StatisticsSummary(TypedDict):
    """Overall score statistics (``None`` when there are no scores)."""

    count: int
    mean: Optional[float]
    median: Optional[float]
    mode: Optional[float]
    lowest: Optional[float]
    highest: Optional[float]


class SemesterTrend(TypedDict):
    """Average score of one semester and how it moves over time."""

    semester: str
    grades: int
    average: float
    rolling_average: float
    change: Optional[float]


class GradeReport(TypedDict):
    """The full report written to JSON.

    Keys follow the order the report sections are built in.
    """

    total_students: int
    statistics: StatisticsSummary
    grade_distribution: Dict[str, int]
    averages_by_major: Dict[str, float]
    top_performers: List[StudentSummary]
    semester_trends: List[SemesterTrend]
