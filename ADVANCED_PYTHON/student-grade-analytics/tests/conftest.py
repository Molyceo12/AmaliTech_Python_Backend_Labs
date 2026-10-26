"""Shared pytest fixtures: sample students, grades and temporary CSV files."""

import logging
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from grade_analytics import cli
from grade_analytics.logging_config import PACKAGE_LOGGER
from grade_analytics.models import Grade, Student
from tests.helpers import make_grade, make_student


@pytest.fixture(autouse=True)
def isolated_logging(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> Iterator[None]:
    """Keep test logs out of the real ``logs/`` folder and close them afterwards."""
    log_dir = tmp_path_factory.mktemp("logs")
    monkeypatch.setattr(cli, "DEFAULT_LOG_FILE", str(log_dir / "app.log"))
    yield
    logger = logging.getLogger(PACKAGE_LOGGER)
    for handler in logger.handlers[:]:
        if not isinstance(handler, logging.NullHandler):
            logger.removeHandler(handler)
            handler.close()
    logger.setLevel(logging.NOTSET)


@pytest.fixture(name="write_csv")
def fixture_write_csv(tmp_path: Path) -> Callable[..., Path]:
    """Return a function that writes CSV text to a temp file and gives its path."""

    def write(content: str, name: str = "students.csv") -> Path:
        path = tmp_path / name
        path.write_text(content, encoding="utf-8")
        return path

    return write


@pytest.fixture(name="sample_grades")
def fixture_sample_grades() -> list[Grade]:
    """Return grades covering every letter band (A, A, B, C, D, F)."""
    return [make_grade(score) for score in (95, 90, 85, 72, 61, 40)]


@pytest.fixture(name="sample_students")
def fixture_sample_students() -> list[Student]:
    """Return four students across two majors and two years."""
    return [
        make_student("S001", "Alice", "Computer Science", 1, (90, 80)),
        make_student("S002", "Brian", "Mathematics", 2, (70,)),
        make_student("S003", "Chantal", "Computer Science", 2, (60, 100)),
        make_student("S004", "David", "Mathematics", 1),
    ]
