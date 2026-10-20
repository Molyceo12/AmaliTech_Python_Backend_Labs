"""Course model."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Course:
    """A course students can take.

    Attributes:
        code: Course identifier, e.g. ``"CS101"``.
        title: Course name.
        credits: Credit value of the course.
    """

    code: str
    title: str
    credits: int
