"""Tests for score records and semester trends."""

import inspect

import pytest

from grade_analytics.analytics import score_records, semester_trends
from grade_analytics.models import ScoreRecord
from tests.helpers import make_grade, make_student


def records(*pairs: tuple[str, float]) -> list[ScoreRecord]:
    """Build ScoreRecords from (semester, score) pairs."""
    return [ScoreRecord("S1", "CS101", semester, score) for semester, score in pairs]


def test_score_records_flatten_grades() -> None:
    """Every grade becomes one ScoreRecord, yielded lazily."""
    student = make_student("S001", scores=(80,))
    student.grades.append(make_grade(60, course_code="CS102", semester="2026-S2"))
    generated = score_records([student])
    assert inspect.isgenerator(generated)
    assert list(generated) == [
        ScoreRecord("S001", "CS101", "2026-S1", 80),
        ScoreRecord("S001", "CS102", "2026-S2", 60),
    ]


def test_semesters_sorted_with_average_and_change() -> None:
    """Semesters come out oldest first with their average and change."""
    trends = semester_trends(
        records(("2026-S1", 80), ("2025-S2", 60), ("2026-S1", 90), ("2025-S2", 70))
    )
    assert [
        (t["semester"], t["grades"], t["average"], t["change"]) for t in trends
    ] == [
        ("2025-S2", 2, 65.0, None),
        ("2026-S1", 2, 85.0, 20.0),
    ]


def test_rolling_average_uses_last_window_semesters() -> None:
    """With window=2 the rolling average only covers the last two semesters."""
    trends = semester_trends(
        records(("S1", 60), ("S2", 70), ("S3", 80), ("S4", 100)), window=2
    )
    assert [t["rolling_average"] for t in trends] == [60.0, 65.0, 75.0, 90.0]


def test_no_records_gives_no_trends() -> None:
    """No scores means no semesters."""
    assert not semester_trends([])


def test_bad_window() -> None:
    """The window must be at least 1."""
    with pytest.raises(ValueError, match="at least 1"):
        semester_trends([], window=0)
