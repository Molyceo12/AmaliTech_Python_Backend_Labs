"""Small builders shared by the tests."""

from grade_analytics.models import Grade, Student

HEADER = "student_id,name,major,year,course_code,semester,score\n"

# One valid CSV row as the reader returns it (column -> value).
ROW_DATA = {
    "student_id": "S001",
    "name": "Alice",
    "major": "Computer Science",
    "year": "1",
    "course_code": "CS101",
    "semester": "2026-S1",
    "score": "92",
}


def make_grade(
    score: float = 85.0, course_code: str = "CS101", semester: str = "2026-S1"
) -> Grade:
    """Build a ``Grade`` with sensible defaults."""
    return Grade(course_code, semester, score)


def make_student(
    student_id: str = "S001",
    name: str = "Alice",
    major: str = "Computer Science",
    year: int = 1,
    scores: tuple[float, ...] = (),
) -> Student:
    """Build a ``Student`` with one CS101 grade per score."""
    return Student(student_id, name, major, year, [make_grade(s) for s in scores])
