"""Tests for turning raw records into students and courses."""

import logging

import pytest

from grade_analytics.models import Course, Grade, LoadedData, RowProblem
from grade_analytics.readers import RawRecord, build_students
from tests.helpers import ROW_DATA


def record(line: int = 2, **changes: str) -> RawRecord:
    """Build a RawRecord from the valid row with some fields changed."""
    return RawRecord(line, {**ROW_DATA, **changes})


def test_rows_are_grouped_into_students() -> None:
    """Rows with the same student id become one student with all grades."""
    data = build_students(
        [
            record(2),
            record(3, course_code="CS102", score="80"),
            record(4, student_id="S002", name="Brian", year="2", score="70"),
        ]
    )
    assert not data.problems
    assert [s.student_id for s in data.students] == ["S001", "S002"]
    assert data.students[0].grades == [
        Grade("CS101", "2026-S1", 92.0),
        Grade("CS102", "2026-S1", 80.0),
    ]
    assert (data.students[1].name, data.students[1].year) == ("Brian", 2)


def test_courses_use_optional_columns() -> None:
    """course_title and credits fill the Course; the first row wins."""
    data = build_students(
        [
            record(2, course_title="Intro to Programming", credits="4"),
            record(3, student_id="S002", course_title="Other title", credits="2"),
        ]
    )
    assert data.courses == {"CS101": Course("CS101", "Intro to Programming", 4)}


def test_courses_default_when_columns_missing() -> None:
    """Without the optional columns the title is the code and credits are 1."""
    assert build_students([record(2)]).courses == {"CS101": Course("CS101", "CS101", 1)}


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"name": ""}, "'name' is empty"),
        ({"year": "two"}, "year 'two' is not a whole number"),
        ({"score": "eighty"}, "score 'eighty' is not a number"),
        ({"score": "120"}, "Score must be between 0 and 100, got 120"),
        ({"score": "nan"}, "Score must be between 0 and 100, got nan"),
        ({"credits": "three"}, "credits 'three' is not a whole number"),
    ],
    ids=[
        "empty-field",
        "bad-year",
        "text-score",
        "score-too-high",
        "nan-score",
        "bad-credits",
    ],
)
def test_bad_rows_are_skipped_and_reported(
    changes: dict[str, str], reason: str, caplog: pytest.LogCaptureFixture
) -> None:
    """A bad row is skipped with its line number and logged as a warning."""
    with caplog.at_level(logging.WARNING, logger="grade_analytics"):
        data = build_students([record(2), record(3, **changes)])
    assert [s.student_id for s in data.students] == ["S001"]
    assert len(data.students[0].grades) == 1
    assert data.problems == [RowProblem(3, reason)]
    assert [r.levelname for r in caplog.records] == ["WARNING"]
    assert caplog.records[0].getMessage() == f"Skipped line 3: {reason}"


def test_no_records_gives_no_students() -> None:
    """An empty input gives empty results."""
    assert build_students([]) == LoadedData([], {}, [])
