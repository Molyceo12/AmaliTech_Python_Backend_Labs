"""Shared pytest fixtures: sample students and grades."""

import pytest

from grade_analytics.models import Grade, Student
from tests.helpers import make_grade, make_student


@pytest.fixture(name="sample_grades")
def fixture_sample_grades() -> list[Grade]:
    """Return grades covering every letter band (A, A, B, C, D, F)."""
    return [make_grade(score) for score in (95, 90, 85, 72, 61, 40)]


@pytest.fixture(name="sample_students")
def fixture_sample_students() -> list[Student]:
    """Return four students across two majors and two years."""
    return [
        make_student("S001", "Alice", "Computer Science", 1, (90, 80)),
        make_student("S002", "Brian", "Mathematics", 2, (70,)),
        make_student("S003", "Chantal", "Computer Science", 2, (60, 100)),
        make_student("S004", "David", "Mathematics", 1),
    ]
