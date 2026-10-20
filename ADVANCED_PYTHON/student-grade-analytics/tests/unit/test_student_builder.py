"""Tests for turning raw records into students."""

import pytest

from grade_analytics.models import Grade, RowProblem
from grade_analytics.readers import RawRecord, build_students
from tests.helpers import ROW_DATA


def record(line: int = 2, **changes: str) -> RawRecord:
    """Build a RawRecord from the valid row with some fields changed."""
    return RawRecord(line, {**ROW_DATA, **changes})


def test_rows_are_grouped_into_students() -> None:
    """Rows with the same student id become one student with all grades."""
    students, problems = build_students(
        [
            record(2),
            record(3, course_code="CS102", score="80"),
            record(4, student_id="S002", name="Brian", year="2", score="70"),
        ]
    )
    assert not problems
    assert [s.student_id for s in students] == ["S001", "S002"]
    assert students[0].grades == [
        Grade("CS101", "2026-S1", 92.0),
        Grade("CS102", "2026-S1", 80.0),
    ]
    assert (students[1].name, students[1].year) == ("Brian", 2)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"name": ""}, "'name' is empty"),
        ({"year": "two"}, "year 'two' is not a whole number"),
        ({"score": "eighty"}, "score 'eighty' is not a number"),
        ({"score": "120"}, "Score must be between 0 and 100, got 120"),
        ({"score": "nan"}, "Score must be between 0 and 100, got nan"),
    ],
    ids=["empty-field", "bad-year", "text-score", "score-too-high", "nan-score"],
)
def test_bad_rows_are_skipped_and_reported(
    changes: dict[str, str], reason: str
) -> None:
    """A bad row is skipped with its line number; good rows still load."""
    students, problems = build_students([record(2), record(3, **changes)])
    assert [s.student_id for s in students] == ["S001"]
    assert len(students[0].grades) == 1
    assert problems == [RowProblem(3, reason)]


def test_no_records_gives_no_students() -> None:
    """An empty input gives empty results."""
    assert build_students([]) == ([], [])
