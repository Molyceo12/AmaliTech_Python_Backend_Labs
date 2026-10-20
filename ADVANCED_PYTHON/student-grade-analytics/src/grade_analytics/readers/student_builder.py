"""Turning raw rows into students, grades and courses."""

from collections.abc import Iterable
from typing import Dict, List, NamedTuple, Union

from grade_analytics.exceptions import InvalidGradeError, InvalidRowError
from grade_analytics.models import Course, Grade, LoadedData, RowProblem, Student
from grade_analytics.readers.base import RawRecord
from grade_analytics.readers.csv_reader import REQUIRED_HEADERS

DEFAULT_CREDITS = 1


class ParsedRow(NamedTuple):
    """The three things one valid row describes."""

    student: Student
    grade: Grade
    course: Course


def _number(
    record: RawRecord, field: str, kind: Union[type[int], type[float]]
) -> float:
    """Convert a field to a number or raise ``InvalidRowError``."""
    value = record.data[field]
    try:
        return kind(value)
    except ValueError:
        word = "a whole number" if kind is int else "a number"
        reason = f"{field} '{value}' is not {word}"
        raise InvalidRowError(record.line_number, reason) from None


def parse_record(record: RawRecord) -> ParsedRow:
    """Check one row and turn it into a student, a grade and a course.

    ``course_title`` and ``credits`` are optional columns: the title falls
    back to the course code and credits to ``DEFAULT_CREDITS``.

    Args:
        record: Raw row from the reader.

    Returns:
        The student (without grades), the grade and the course of the row.

    Raises:
        InvalidRowError: If a required field is empty, the year or credits
            are not whole numbers, or the score is not a number in 0–100.
    """
    data = record.data
    for field in REQUIRED_HEADERS:
        if not data.get(field):
            raise InvalidRowError(record.line_number, f"'{field}' is empty")
    year = int(_number(record, "year", int))
    score = _number(record, "score", float)
    credit_value = DEFAULT_CREDITS
    if data.get("credits"):
        credit_value = int(_number(record, "credits", int))
    try:
        grade = Grade(data["course_code"], data["semester"], score)
    except InvalidGradeError as error:
        raise InvalidRowError(record.line_number, str(error)) from error
    student = Student(data["student_id"], data["name"], data["major"], year)
    title = data.get("course_title") or data["course_code"]
    return ParsedRow(student, grade, Course(data["course_code"], title, credit_value))


def build_students(records: Iterable[RawRecord]) -> LoadedData:
    """Group rows by student id and collect the course catalog.

    Bad rows are skipped and reported instead of stopping the whole run.
    The first row seen for a student or course decides its details.

    Args:
        records: Raw rows, e.g. from ``CsvRecordReader.read()``.

    Returns:
        Students with all their grades, the courses and the skipped rows.
    """
    students: Dict[str, Student] = {}
    courses: Dict[str, Course] = {}
    problems: List[RowProblem] = []
    for record in records:
        try:
            row = parse_record(record)
        except InvalidRowError as error:
            problems.append(RowProblem(error.line_number, error.reason))
            continue
        students.setdefault(row.student.student_id, row.student).grades.append(
            row.grade
        )
        courses.setdefault(row.course.code, row.course)
    return LoadedData(list(students.values()), courses, problems)
