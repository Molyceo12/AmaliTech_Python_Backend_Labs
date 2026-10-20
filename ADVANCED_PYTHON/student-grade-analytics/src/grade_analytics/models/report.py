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
    """Overall score statistics."""

    mean: Optional[float]
    median: Optional[float]
    mode: Optional[float]


class GradeReport(TypedDict):
    """The full report written to JSON.

    Keys follow the order the report sections are built in.
    """

    total_students: int
    statistics: StatisticsSummary
    grade_distribution: Dict[str, int]
    averages_by_major: Dict[str, float]
    top_performers: List[StudentSummary]
    semester_trends: Dict[str, List[float]]
