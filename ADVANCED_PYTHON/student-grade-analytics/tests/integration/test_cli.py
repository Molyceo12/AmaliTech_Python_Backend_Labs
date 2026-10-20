"""End-to-end: sample CSV files through the command line to a JSON report."""

import json
from pathlib import Path

import pytest

from grade_analytics.cli import EXIT_ERROR, EXIT_OK, EXIT_ROWS_SKIPPED, main

DATA = Path(__file__).resolve().parents[2] / "data"


def run(csv_name: str, tmp_path: Path, *extra: str) -> int:
    """Run the CLI on a sample file, writing the report into ``tmp_path``."""
    output = tmp_path / "report.json"
    return main([str(DATA / csv_name), "--output", str(output), *extra])


def test_valid_file_writes_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The sample file gives exit code 0, a summary and a full JSON report."""
    assert run("students.csv", tmp_path, "--top", "3") == EXIT_OK
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["total_students"] == 16
    assert report["total_grades"] == 48
    assert len(report["top_performers"]) == 3
    assert len(report["semester_trends"]) == 3
    printed = capsys.readouterr().out
    assert "Students: 16   Grades: 48" in printed
    assert "Grade distribution:" in printed
    assert "1. Maurice Irimaso (S016)" in printed


def test_invalid_rows_give_exit_code_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Skipped rows are listed and the exit code is 2."""
    assert run("invalid_rows.csv", tmp_path) == EXIT_ROWS_SKIPPED
    printed = capsys.readouterr().out
    assert "Skipped rows (4):" in printed
    assert "Line 3: 'name' is empty" in printed


@pytest.mark.parametrize(
    ("csv_name", "message"),
    [
        ("missing.csv", "not found"),
        ("empty.csv", "empty"),
        ("bad_headers.csv", "missing required headers: score"),
    ],
)
def test_file_errors_give_exit_code_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], csv_name: str, message: str
) -> None:
    """File problems print a clear error (no traceback) and exit with 1."""
    assert run(csv_name, tmp_path) == EXIT_ERROR
    error = capsys.readouterr().err
    assert error.startswith("Error:")
    assert message in error
    assert not (tmp_path / "report.json").exists()


@pytest.mark.parametrize("value", ["0", "-2", "abc"])
def test_bad_numbers_are_rejected(tmp_path: Path, value: str) -> None:
    """--top and --window must be whole numbers of at least 1."""
    with pytest.raises(SystemExit) as exit_info:
        run("students.csv", tmp_path, "--window", value)
    assert exit_info.value.code == 2
