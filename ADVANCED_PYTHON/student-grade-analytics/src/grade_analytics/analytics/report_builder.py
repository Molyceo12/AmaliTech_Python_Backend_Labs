"""Building the full report from loaded data."""

from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, List, cast

from grade_analytics.aggregators import (
    grade_distribution,
    group_by_major,
    group_by_year,
    ordered_sections,
)
from grade_analytics.analytics.rankings import rank_students, top_performers
from grade_analytics.analytics.statistics import summarize
from grade_analytics.analytics.trends import score_records, semester_trends
from grade_analytics.models import (
    Course,
    CourseSummary,
    GradeReport,
    LoadedData,
    Student,
    StudentSummary,
)


def _average(scores: List[float]) -> float:
    """Average rounded to 2 decimals (callers pass at least one score)."""
    return round(sum(scores) / len(scores), 2)


def averages_by_major(students: Iterable[Student]) -> Dict[str, float]:
    """Average score of every grade given to students of each major.

    Args:
        students: Students to group (``defaultdict`` by major).

    Returns:
        Major → average score; majors without any grades are left out.
    """
    averages: Dict[str, float] = {}
    for major, group in group_by_major(students).items():
        scores = [grade.score for student in group for grade in student.grades]
        if scores:
            averages[major] = _average(scores)
    return averages


def course_summaries(
    students: Iterable[Student], courses: Dict[str, Course]
) -> List[CourseSummary]:
    """Average score and number of grades per course, in catalog order.

    Args:
        students: Students whose grades are counted.
        courses: Course catalog from the data file.

    Returns:
        One summary per course that has grades.
    """
    scores: defaultdict[str, List[float]] = defaultdict(list)
    for student in students:
        for grade in student.grades:
            scores[grade.course_code].append(grade.score)
    return [
        {
            "code": course.code,
            "title": course.title,
            "credits": course.credits,
            "grades": len(scores[code]),
            "average": _average(scores[code]),
        }
        for code, course in courses.items()
        if scores[code]
    ]


def build_report(data: LoadedData, top_n: int = 5, window: int = 3) -> GradeReport:
    """Build every report section, in a fixed order (``OrderedDict``).

    Args:
        data: Students, courses and problems from the data file.
        top_n: How many top performers to list (ties included).
        window: How many semesters the rolling average covers.

    Returns:
        The report, ready to be written as JSON.

    Raises:
        ValueError: If ``top_n`` or ``window`` is less than 1.
    """
    students = data.students
    grades = [grade for student in students for grade in student.grades]
    scores = [grade.score for grade in grades]
    top: List[StudentSummary] = [
        {
            "rank": entry.rank,
            "student_id": entry.student.student_id,
            "name": entry.student.name,
            "major": entry.student.major,
            "average": round(entry.average, 2),
            "percentile": entry.percentile,
        }
        for entry in top_performers(rank_students(students), top_n)
    ]
    sections = ordered_sections(
        [
            ("total_students", len(students)),
            ("total_grades", len(grades)),
            ("statistics", summarize(scores)),
            ("grade_distribution", dict(grade_distribution(grades))),
            ("averages_by_major", averages_by_major(students)),
            (
                "students_per_year",
                {
                    str(year): len(group)
                    for year, group in sorted(group_by_year(students).items())
                },
            ),
            ("averages_by_course", course_summaries(students, data.courses)),
            ("top_performers", top),
            ("semester_trends", semester_trends(score_records(students), window)),
        ]
    )
    return cast(GradeReport, dict(sections))
