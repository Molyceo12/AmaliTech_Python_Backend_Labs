"""Tests for the text bar chart."""

from grade_analytics.utils import bar_chart


def test_bars_scale_to_the_largest_count() -> None:
    """The largest count gets the full width; others scale down."""
    assert bar_chart({"A": 4, "B": 2}, width=8) == "A | ######## 4\nB | #### 2"


def test_zero_count_has_no_bar() -> None:
    """A zero count shows only the number."""
    assert bar_chart({"A": 3, "F": 0}, width=3).splitlines()[1] == "F | 0"


def test_labels_are_aligned() -> None:
    """Shorter labels are padded so the bars line up."""
    lines = bar_chart({"Physics": 1, "CS": 1}, width=2).splitlines()
    assert lines == ["Physics | ## 1", "CS      | ## 1"]


def test_all_zero_counts() -> None:
    """All-zero counts draw no bars and do not divide by zero."""
    assert bar_chart({"A": 0}) == "A | 0"


def test_empty_chart() -> None:
    """No labels gives an empty chart."""
    assert bar_chart({}) == ""
