"""Rolling average with ``deque``."""

from collections import deque


class RollingAverage:
    """Average of the most recent scores, e.g. the last 3 semesters.

    A ``deque`` with ``maxlen`` drops the oldest score automatically, so
    adding a score is O(1) and memory stays fixed at ``window`` items.
    """

    def __init__(self, window: int) -> None:
        """Create an empty rolling average.

        Args:
            window: How many recent scores to average.

        Raises:
            ValueError: If ``window`` is less than 1.
        """
        if window < 1:
            raise ValueError("window must be at least 1")
        self._scores: deque[float] = deque(maxlen=window)

    def add(self, score: float) -> float:
        """Add a score and return the new rolling average.

        Args:
            score: The newest score.

        Returns:
            Average of the last ``window`` scores (fewer at the start).
        """
        self._scores.append(score)
        return self.value

    @property
    def value(self) -> float:
        """Current rolling average (0.0 before any score is added)."""
        if not self._scores:
            return 0.0
        return sum(self._scores) / len(self._scores)
