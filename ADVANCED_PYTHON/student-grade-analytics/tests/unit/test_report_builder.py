"""Tests for building the full report."""

import pytest

from grade_analytics.analytics import averages_by_major, build_report
from grade_analytics.models import Course, LoadedData, Student
from tests.helpers import make_student


def loaded(students: list[Student]) -> LoadedData:
    """Wrap students with a one-course catalog."""
    return LoadedData(students, {"CS101": Course("CS101", "Intro", 4)}, [])


def test_sections_in_fixed_order(sample_students: list[Student]) -> None:
    """Sections come out in the order the report defines (OrderedDict)."""
    assert list(build_report(loaded(sample_students))) == [
        "total_students",
        "total_grades",
        "statistics",
        "grade_distribution",
        "averages_by_major",
        "students_per_year",
        "averages_by_course",
        "top_performers",
        "semester_trends",
    ]


def test_report_values(sample_students: list[Student]) -> None:
    """Totals, groups, courses and top performers match the sample data."""
    report = build_report(loaded(sample_students), top_n=2)
    assert (report["total_students"], report["total_grades"]) == (4, 5)
    assert report["statistics"]["mean"] == 80.0
    assert report["grade_distribution"] == {"A": 2, "B": 1, "C": 1, "D": 1, "F": 0}
    assert report["averages_by_major"] == {
        "Computer Science": 82.5,
        "Mathematics": 70.0,
    }
    assert report["students_per_year"] == {"1": 2, "2": 2}
    assert report["averages_by_course"] == [
        {"code": "CS101", "title": "Intro", "credits": 4, "grades": 5, "average": 80.0}
    ]
    assert [t["student_id"] for t in report["top_performers"]] == ["S001", "S003"]
    assert report["top_performers"][0]["rank"] == 1


def test_course_without_grades_is_left_out() -> None:
    """Courses in the catalog with no grades are not listed."""
    data = LoadedData([make_student(scores=(80,))], {"X1": Course("X1", "X", 1)}, [])
    assert not build_report(data)["averages_by_course"]


def test_majors_without_grades_are_left_out() -> None:
    """A major whose students have no grades has no average."""
    assert not averages_by_major([make_student()])


def test_empty_data() -> None:
    """No students gives an empty but valid report."""
    report = build_report(LoadedData([], {}, []))
    assert report["total_students"] == 0
    assert not report["top_performers"]
    assert report["statistics"]["mean"] is None


def test_invalid_top_n(sample_students: list[Student]) -> None:
    """top_n must be at least 1."""
    with pytest.raises(ValueError):
        build_report(loaded(sample_students), top_n=0)
