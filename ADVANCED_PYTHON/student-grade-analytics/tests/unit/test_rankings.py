"""Tests for ranking students and picking top performers."""

import pytest

from grade_analytics.analytics import RankedStudent, rank_students, top_performers
from tests.helpers import make_student


@pytest.fixture(name="ranked")
def fixture_ranked() -> list[RankedStudent]:
    """Rank five students: averages 90, 80, 80, 70 and one with no grades."""
    return rank_students(
        [
            make_student("B", scores=(80,)),
            make_student("A", scores=(90,)),
            make_student("E"),
            make_student("C", scores=(80,)),
            make_student("D", scores=(70,)),
        ]
    )


def test_ranked_best_first_with_shared_ranks(ranked: list[RankedStudent]) -> None:
    """Ties share a rank and the next rank skips ahead (1, 2, 2, 4)."""
    assert [(r.rank, r.student.student_id) for r in ranked] == [
        (1, "A"),
        (2, "B"),
        (2, "C"),
        (4, "D"),
    ]


def test_students_without_grades_are_left_out(ranked: list[RankedStudent]) -> None:
    """A student with no grades has no average, so is not ranked."""
    assert "E" not in [r.student.student_id for r in ranked]


def test_percentiles(ranked: list[RankedStudent]) -> None:
    """Each average gets its percentile among all averages."""
    assert [r.percentile for r in ranked] == [100.0, 75.0, 75.0, 25.0]


@pytest.mark.parametrize(
    ("n", "expected"),
    [(1, ["A"]), (2, ["A", "B", "C"]), (10, ["A", "B", "C", "D"])],
    ids=["top-1", "tie-at-cutoff", "more-than-available"],
)
def test_top_performers(
    ranked: list[RankedStudent], n: int, expected: list[str]
) -> None:
    """Top n includes everyone tied with the n-th place."""
    assert [r.student.student_id for r in top_performers(ranked, n)] == expected


def test_top_performers_needs_positive_n(ranked: list[RankedStudent]) -> None:
    """n must be at least 1."""
    with pytest.raises(ValueError, match="at least 1"):
        top_performers(ranked, 0)
