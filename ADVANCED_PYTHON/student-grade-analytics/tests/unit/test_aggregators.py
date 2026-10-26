"""Tests for the Counter, defaultdict, OrderedDict and deque aggregators."""

from collections import Counter, OrderedDict

import pytest

from grade_analytics.aggregators import (
    LETTERS,
    RollingAverage,
    grade_distribution,
    group_by_major,
    group_by_year,
    ordered_sections,
)
from grade_analytics.models import Grade, Student


def test_grade_distribution_counts_each_letter(sample_grades: list[Grade]) -> None:
    """Counter holds how many grades fall in each band."""
    distribution = grade_distribution(sample_grades)
    assert isinstance(distribution, Counter)
    assert distribution == Counter({"A": 2, "B": 1, "C": 1, "D": 1, "F": 1})
    assert distribution.most_common(1) == [("A", 2)]


def test_grade_distribution_keeps_empty_bands() -> None:
    """Every letter is present, even with no grades."""
    distribution = grade_distribution([])
    assert list(distribution) == list(LETTERS)
    assert sum(distribution.values()) == 0


def test_group_by_major(sample_students: list[Student]) -> None:
    """defaultdict groups students by major, keeping input order."""
    groups = group_by_major(sample_students)
    ids = {major: [s.student_id for s in group] for major, group in groups.items()}
    assert ids == {
        "Computer Science": ["S001", "S003"],
        "Mathematics": ["S002", "S004"],
    }


def test_group_by_year(sample_students: list[Student]) -> None:
    """defaultdict groups students by year."""
    groups = group_by_year(sample_students)
    assert {year: [s.student_id for s in group] for year, group in groups.items()} == {
        1: ["S001", "S004"],
        2: ["S002", "S003"],
    }


def test_grouping_empty_input_gives_empty_dict() -> None:
    """No students means no groups (and a plain dict is returned)."""
    assert not group_by_major([])
    assert isinstance(group_by_year([]), dict)


def test_ordered_sections_keep_insertion_order() -> None:
    """OrderedDict keeps sections in the order they were added."""
    sections = ordered_sections([("total", 4), ("average", 80.0), ("top", [])])
    assert isinstance(sections, OrderedDict)
    assert list(sections) == ["total", "average", "top"]


def test_ordered_sections_reject_duplicates() -> None:
    """A section name can only appear once."""
    with pytest.raises(ValueError, match="Duplicate report section: total"):
        ordered_sections([("total", 1), ("total", 2)])


def test_rolling_average_uses_last_window_scores() -> None:
    """deque(maxlen=3) drops the oldest score once the window is full."""
    rolling = RollingAverage(window=3)
    assert [rolling.add(s) for s in (70, 80, 90, 100)] == [70, 75, 80, 90]


def test_rolling_average_starts_at_zero() -> None:
    """Before any score is added, the average is 0.0."""
    assert RollingAverage(window=2).value == 0.0


@pytest.mark.parametrize("window", [0, -3])
def test_rolling_average_rejects_bad_window(window: int) -> None:
    """The window must be at least 1."""
    with pytest.raises(ValueError, match="at least 1"):
        RollingAverage(window)
