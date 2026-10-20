"""Collection-based aggregators: Counter, defaultdict, OrderedDict, deque."""

from grade_analytics.aggregators.distribution import LETTERS, grade_distribution
from grade_analytics.aggregators.grouping import (
    group_by_major,
    group_by_year,
    scores_by_semester,
)
from grade_analytics.aggregators.ordering import ordered_sections
from grade_analytics.aggregators.rolling import RollingAverage

__all__ = [
    "LETTERS",
    "RollingAverage",
    "grade_distribution",
    "group_by_major",
    "group_by_year",
    "ordered_sections",
    "scores_by_semester",
]
