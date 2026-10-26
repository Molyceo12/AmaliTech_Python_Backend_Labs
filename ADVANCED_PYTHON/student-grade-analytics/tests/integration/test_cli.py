"""End-to-end: sample CSV files through the command line to a JSON report."""

import json
import logging
from pathlib import Path

import pytest

from grade_analytics.cli import EXIT_ERROR, EXIT_OK, EXIT_ROWS_SKIPPED, main
from grade_analytics.console import border, boxed
from grade_analytics.services import AnalyticsService
from tests.helpers import CHART_FILES

DATA = Path(__file__).resolve().parents[2] / "data"


def run(csv_name: str, tmp_path: Path, *extra: str, charts: bool = False) -> int:
    """Run the CLI on a sample file, writing the report into ``tmp_path``.

    Charts are off by default to keep the tests fast.
    """
    output = tmp_path / "report.json"
    args = [str(DATA / csv_name), "--output", str(output), *extra]
    return main(args if charts else [*args, "--no-charts"])


def test_charts_are_written_next_to_the_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """By default the CLI saves the JSON report and five PNG charts."""
    assert run("students.csv", tmp_path, charts=True) == EXIT_OK
    files = {path.name for path in tmp_path.iterdir()}
    assert files == {*CHART_FILES, "report.json"}
    printed = capsys.readouterr().out
    assert "4. Drawing the charts " in printed
    assert "done (5 files)" in printed
    assert "6. Course averages chart saved to " in printed


def test_no_charts_writes_only_the_report(tmp_path: Path) -> None:
    """--no-charts writes the JSON report only."""
    assert run("students.csv", tmp_path) == EXIT_OK
    assert [path.name for path in tmp_path.iterdir()] == ["report.json"]


def test_valid_file_writes_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The sample file gives exit code 0, numbered steps and a full JSON report."""
    assert run("students.csv", tmp_path, "--top", "3") == EXIT_OK
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["total_students"] == 16
    assert report["total_grades"] == 48
    assert len(report["top_performers"]) == 3
    assert len(report["semester_trends"]) == 3
    printed = capsys.readouterr().out
    assert "done (16 students, 48 grades)" in printed
    assert "2. Calculating statistics " in printed
    assert "3. Writing the JSON report " in printed
    assert "Drawing the charts" not in printed  # --no-charts
    assert f"1. JSON report saved to {tmp_path / 'report.json'}" in printed


def test_output_is_drawn_in_bordered_boxes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Steps and summary sit in two boxes: border, title, border, lines, border."""
    run("students.csv", tmp_path)
    lines = capsys.readouterr().out.splitlines()
    assert lines[:3] == [border(), boxed("Student Grade Analytics"), border()]
    assert boxed("Summary") in lines
    assert lines[-1] == border()
    assert lines.count(border()) == 6  # two boxes, three borders each
    assert all(line.startswith("::") and line.endswith("::") for line in lines if line)


def test_invalid_rows_give_exit_code_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Skipped rows are listed and the exit code is 2."""
    assert run("invalid_rows.csv", tmp_path) == EXIT_ROWS_SKIPPED
    printed = capsys.readouterr().out
    assert "4 rows skipped)" in printed
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
    captured = capsys.readouterr()
    assert captured.out.splitlines()[-1] == border()  # the steps box is closed
    error = captured.err
    assert error.startswith("Error:")
    assert message in error
    assert not (tmp_path / "report.json").exists()


@pytest.mark.parametrize("value", ["0", "-2", "abc"])
def test_bad_numbers_are_rejected(tmp_path: Path, value: str) -> None:
    """--top and --window must be whole numbers of at least 1."""
    with pytest.raises(SystemExit) as exit_info:
        run("students.csv", tmp_path, "--window", value)
    assert exit_info.value.code == 2


def test_run_is_logged_to_file(tmp_path: Path) -> None:
    """A normal run writes its start, progress and end to the log file."""
    log_file = tmp_path / "logs" / "run.log"
    assert run("students.csv", tmp_path, "--log-file", str(log_file)) == EXIT_OK
    text = log_file.read_text(encoding="utf-8")
    assert "| INFO     | grade_analytics.cli | Run started: input=" in text
    assert "16 students, 48 grades" in text
    assert "Report written to " in text
    assert "Run finished: exit code 0" in text
    assert "DEBUG" not in text  # default level is INFO


def test_debug_level_and_skipped_rows_are_logged(tmp_path: Path) -> None:
    """--log-level debug adds details; skipped rows are warnings."""
    log_file = tmp_path / "run.log"
    code = run(
        "invalid_rows.csv",
        tmp_path,
        "--log-file",
        str(log_file),
        "--log-level",
        "debug",
        charts=True,
    )
    assert code == EXIT_ROWS_SKIPPED
    text = log_file.read_text(encoding="utf-8")
    assert "| DEBUG    | grade_analytics.readers.csv_reader | Headers: " in text
    assert "Chart saved: " in text
    assert "| WARNING  |" in text
    assert "Skipped line 3: 'name' is empty" in text
    assert "Run finished: exit code 2" in text


def test_file_error_is_logged(tmp_path: Path) -> None:
    """A failed run is logged as an error with its message."""
    log_file = tmp_path / "run.log"
    assert run("missing.csv", tmp_path, "--log-file", str(log_file)) == EXIT_ERROR
    text = log_file.read_text(encoding="utf-8")
    assert "| ERROR    | grade_analytics.cli | Run failed: Data file not found" in text
    assert "Run finished: exit code 1" in text


def test_unexpected_error_is_logged_and_raised(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A bug is logged as critical with its traceback, then re-raised."""

    def broken_run(*_: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(AnalyticsService, "run", broken_run)
    with (
        caplog.at_level(logging.INFO, logger="grade_analytics"),
        pytest.raises(RuntimeError, match="boom"),
    ):
        run("students.csv", tmp_path)
    critical = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical) == 1
    assert critical[0].exc_info is not None


def test_bad_log_level_is_rejected(tmp_path: Path) -> None:
    """--log-level only accepts the known level names."""
    with pytest.raises(SystemExit) as exit_info:
        run("students.csv", tmp_path, "--log-level", "loud")
    assert exit_info.value.code == 2
