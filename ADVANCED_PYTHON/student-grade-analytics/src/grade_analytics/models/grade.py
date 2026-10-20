"""Grade model and the lightweight ``ScoreRecord`` row."""

from collections import namedtuple
from dataclasses import dataclass

from grade_analytics.exceptions import InvalidGradeError

MIN_SCORE = 0.0
MAX_SCORE = 100.0

# (minimum score, letter), checked from the highest band down.
LETTER_BANDS: tuple[tuple[float, str], ...] = (
    (90.0, "A"),
    (80.0, "B"),
    (70.0, "C"),
    (60.0, "D"),
    (MIN_SCORE, "F"),
)

# One raw score row before it becomes a Grade: small and immutable like a tuple.
ScoreRecord = namedtuple(
    "ScoreRecord", ["student_id", "course_code", "semester", "score"]
)


def letter_for(score: float) -> str:
    """Return the letter grade (A–F) for a score.

    Args:
        score: Score between 0 and 100.

    Returns:
        The letter of the first band whose minimum the score reaches.
    """
    for minimum, letter in LETTER_BANDS:
        if score >= minimum:
            return letter
    return "F"


@dataclass(frozen=True, slots=True)
class Grade:
    """One score a student got in one course and semester.

    Attributes:
        course_code: Course identifier, e.g. ``"CS101"``.
        semester: Semester label, e.g. ``"2026-S1"``.
        score: Score between 0 and 100.
    """

    course_code: str
    semester: str
    score: float

    def __post_init__(self) -> None:
        """Reject scores outside 0–100.

        Raises:
            InvalidGradeError: If the score is out of range.
        """
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise InvalidGradeError(
                f"Score must be between {MIN_SCORE:g} and {MAX_SCORE:g}, "
                f"got {self.score:g}"
            )

    @property
    def letter(self) -> str:
        """Letter grade (A–F) for this score."""
        return letter_for(self.score)
