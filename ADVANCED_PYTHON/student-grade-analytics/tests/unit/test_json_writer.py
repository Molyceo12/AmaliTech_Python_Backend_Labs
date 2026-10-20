"""Tests for the JSON report writer and the atomic write helper."""

import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from grade_analytics.exceptions import ReportWriteError
from grade_analytics.models import GradeReport
from grade_analytics.utils import atomic_write
from grade_analytics.writers import JsonReportWriter, ReportWriter

REPORT: GradeReport = {
    "total_students": 2,
    "statistics": {
        "count": 2,
        "mean": 81.0,
        "median": 81.0,
        "mode": None,
        "lowest": 70.0,
        "highest": 92.0,
    },
    "grade_distribution": {"A": 1, "B": 0, "C": 1, "D": 0, "F": 0},
    "averages_by_major": {"Computer Science": 81.0},
    "top_performers": [
        {
            "student_id": "S001",
            "name": "Zoë",
            "major": "Computer Science",
            "average": 92.0,
            "percentile": 100.0,
        }
    ],
    "semester_trends": {"2026-S1": [92.0, 70.0]},
}


def test_writer_implements_interface() -> None:
    """JsonReportWriter is a ReportWriter."""
    assert isinstance(JsonReportWriter(), ReportWriter)


def test_writes_readable_indented_json(tmp_path: Path) -> None:
    """The report is saved as indented UTF-8 JSON and reads back the same."""
    path = JsonReportWriter().write(REPORT, tmp_path / "report.json")
    text = path.read_text(encoding="utf-8")
    assert json.loads(text) == REPORT
    assert '\n  "total_students": 2' in text  # indent=2
    assert "Zoë" in text  # ensure_ascii=False keeps names readable
    assert text.endswith("}\n")


def test_creates_missing_folders(tmp_path: Path) -> None:
    """Parent folders are created when they do not exist."""
    target = tmp_path / "output" / "reports" / "report.json"
    assert JsonReportWriter().write(REPORT, str(target)) == target
    assert target.exists()


def test_write_failure_raises_report_write_error(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    """An OS error while saving raises ReportWriteError and leaves no files."""
    mocker.patch(
        "grade_analytics.utils.file_utils.os.replace", side_effect=OSError("disk full")
    )
    with pytest.raises(ReportWriteError, match="disk full"):
        JsonReportWriter().write(REPORT, tmp_path / "report.json")
    assert not list(tmp_path.iterdir())


def test_atomic_write_keeps_old_file_on_failure(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    """If writing fails, the previous file content is untouched."""
    target = tmp_path / "report.json"
    target.write_text("old", encoding="utf-8")
    mocker.patch(
        "grade_analytics.utils.file_utils.os.replace", side_effect=OSError("boom")
    )
    with pytest.raises(OSError), atomic_write(target) as handle:
        handle.write("new")
    assert target.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.iterdir()) == [target]
