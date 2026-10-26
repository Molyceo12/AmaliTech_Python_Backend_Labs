"""Tests for the Grade, Student and Course models."""

import dataclasses

import pytest

from grade_analytics.exceptions import GradeAnalyticsError, InvalidGradeError
from grade_analytics.models import Course, Grade, ScoreRecord, letter_for
from tests.helpers import make_grade, make_student


@pytest.mark.parametrize("score", [0, 55.5, 100])
def test_grade_accepts_scores_in_range(score: float) -> None:
    """Scores from 0 to 100 (inclusive) are valid."""
    assert make_grade(score).score == score


@pytest.mark.parametrize("score", [-1, 100.1, 250])
def test_grade_rejects_scores_out_of_range(score: float) -> None:
    """Scores outside 0–100 raise InvalidGradeError."""
    with pytest.raises(InvalidGradeError, match="between 0 and 100"):
        make_grade(score)


def test_invalid_grade_error_is_a_grade_analytics_error() -> None:
    """Every tool error can be caught with the base class."""
    assert issubclass(InvalidGradeError, GradeAnalyticsError)


@pytest.mark.parametrize(
    ("score", "letter"),
    [(100, "A"), (90, "A"), (89.9, "B"), (80, "B"), (70, "C"), (60, "D"), (59.9, "F")],
)
def test_letter_bands(score: float, letter: str) -> None:
    """Each score maps to the right letter at the band boundaries."""
    assert letter_for(score) == letter
    assert make_grade(score).letter == letter


def test_letter_for_below_range_is_f() -> None:
    """letter_for falls back to F for scores below every band."""
    assert letter_for(-5) == "F"


def test_grade_is_frozen() -> None:
    """A Grade cannot be changed after it is created."""
    grade = make_grade(80)
    with pytest.raises(dataclasses.FrozenInstanceError):
        grade.score = 90  # type: ignore[misc]


def test_student_average() -> None:
    """The average is the mean of all the student's scores."""
    assert make_student(scores=(90, 80, 70)).average == 80


def test_student_without_grades_has_no_average() -> None:
    """A student with no grades has an average of None."""
    assert make_student().average is None


def test_student_grades_are_not_shared() -> None:
    """default_factory gives every student their own grades list."""
    first, second = make_student("S1"), make_student("S2")
    first.grades.append(make_grade())
    assert not second.grades


def test_course_fields() -> None:
    """Course stores its code, title and credits."""
    course = Course("CS101", "Intro to Programming", 4)
    assert (course.code, course.title, course.credits) == (
        "CS101",
        "Intro to Programming",
        4,
    )


def test_score_record_is_a_named_tuple() -> None:
    """ScoreRecord fields are reachable by name and by index."""
    record = ScoreRecord("S001", "CS101", "2026-S1", 88.0)
    assert record.score == record[3] == 88.0
    assert record._asdict()["course_code"] == "CS101"


def test_grade_equality() -> None:
    """Two grades with the same fields are equal (generated __eq__)."""
    assert Grade("CS101", "2026-S1", 80) == make_grade(80)
