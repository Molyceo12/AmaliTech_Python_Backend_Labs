"""Tests for mean, median, mode, percentile rank and the summary."""

from typing import Optional

import pytest

from grade_analytics.analytics import mean, median, mode, percentile_rank, summarize

SCORES = [70.0, 80.0, 80.0, 90.0, 100.0]


def test_mean() -> None:
    """The mean is the sum divided by the count."""
    assert mean(SCORES) == 84.0


@pytest.mark.parametrize(
    ("scores", "expected"),
    [([3.0, 1.0, 2.0], 2.0), ([4.0, 1.0, 3.0, 2.0], 2.5), ([7.0], 7.0)],
    ids=["odd", "even", "single"],
)
def test_median(scores: list[float], expected: float) -> None:
    """Odd counts take the middle value, even counts average the two middle."""
    assert median(scores) == expected


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        (SCORES, 80.0),
        ([5.0, 5.0, 7.0, 7.0, 1.0], 7.0),
        ([1.0, 2.0, 3.0], None),
        ([42.0], 42.0),
    ],
    ids=["single-mode", "tie-takes-highest", "all-unique", "one-score"],
)
def test_mode(scores: list[float], expected: Optional[float]) -> None:
    """Mode uses Counter; ties pick the highest; all-unique has no mode."""
    assert mode(scores) == expected


@pytest.mark.parametrize("function", [mean, median, mode])
def test_empty_scores_give_none(function: object) -> None:
    """With no scores there is no mean, median or mode."""
    assert callable(function)
    assert function([]) is None


@pytest.mark.parametrize(
    ("score", "expected"), [(100.0, 100.0), (80.0, 60.0), (70.0, 20.0), (50.0, 0.0)]
)
def test_percentile_rank(score: float, expected: float) -> None:
    """Percentile = share of scores at or below the score."""
    assert percentile_rank(score, SCORES) == expected


def test_percentile_rank_needs_scores() -> None:
    """Ranking against nothing is an error."""
    with pytest.raises(ValueError, match="empty"):
        percentile_rank(50.0, [])


def test_summarize() -> None:
    """The summary rounds to 2 decimals and includes count, lowest, highest."""
    assert summarize([70.0, 80.0, 85.5]) == {
        "count": 3,
        "mean": 78.5,
        "median": 80.0,
        "mode": None,
        "lowest": 70.0,
        "highest": 85.5,
    }


def test_summarize_no_scores() -> None:
    """An empty data set gives a zero count and no values."""
    summary = summarize([])
    assert summary["count"] == 0
    assert summary["mean"] is None and summary["highest"] is None
