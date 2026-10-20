"""Turning raw rows into ``Student`` objects with their grades."""

from collections.abc import Iterable
from typing import Dict, List, Tuple

from grade_analytics.exceptions import InvalidGradeError, InvalidRowError
from grade_analytics.models import Grade, RowProblem, Student
from grade_analytics.readers.base import RawRecord
from grade_analytics.readers.csv_reader import REQUIRED_HEADERS


def parse_record(record: RawRecord) -> Tuple[Student, Grade]:
    """Check one row and turn it into a student (without grades) and a grade.

    Args:
        record: Raw row from the reader.

    Returns:
        The student described by the row and the grade it holds.

    Raises:
        InvalidRowError: If a field is empty, the year is not a whole number,
            or the score is not a number between 0 and 100.
    """
    data = record.data
    for field in REQUIRED_HEADERS:
        if not data.get(field):
            raise InvalidRowError(record.line_number, f"'{field}' is empty")
    try:
        year = int(data["year"])
    except ValueError:
        reason = f"year '{data['year']}' is not a whole number"
        raise InvalidRowError(record.line_number, reason) from None
    try:
        score = float(data["score"])
    except ValueError:
        reason = f"score '{data['score']}' is not a number"
        raise InvalidRowError(record.line_number, reason) from None
    try:
        grade = Grade(data["course_code"], data["semester"], score)
    except InvalidGradeError as error:
        raise InvalidRowError(record.line_number, str(error)) from error
    student = Student(data["student_id"], data["name"], data["major"], year)
    return student, grade


def build_students(
    records: Iterable[RawRecord],
) -> Tuple[List[Student], List[RowProblem]]:
    """Group rows by student id into students with all their grades.

    Bad rows are skipped and reported instead of stopping the whole run.

    Args:
        records: Raw rows, e.g. from ``CsvRecordReader.read()``.

    Returns:
        The students (in first-seen order) and the problems for skipped rows.
    """
    students: Dict[str, Student] = {}
    problems: List[RowProblem] = []
    for record in records:
        try:
            student, grade = parse_record(record)
        except InvalidRowError as error:
            problems.append(RowProblem(error.line_number, error.reason))
            continue
        students.setdefault(student.student_id, student).grades.append(grade)
    return list(students.values()), problems
