"""Student model."""

from dataclasses import dataclass, field
from typing import Optional

from grade_analytics.models.grade import Grade


@dataclass(slots=True)
class Student:
    """A student and the grades they received.

    Attributes:
        student_id: Unique student identifier, e.g. ``"S001"``.
        name: Full name.
        major: Field of study, e.g. ``"Computer Science"``.
        year: Year of study (1, 2, 3, ...).
        grades: Grades received; empty by default.
    """

    student_id: str
    name: str
    major: str
    year: int
    grades: list[Grade] = field(default_factory=list)

    @property
    def average(self) -> Optional[float]:
        """Mean score across all grades, or ``None`` if there are no grades."""
        if not self.grades:
            return None
        return sum(grade.score for grade in self.grades) / len(self.grades)
