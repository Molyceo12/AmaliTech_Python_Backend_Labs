"""End to end: sample log files through the command line to a JSON report."""

import argparse
import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from log_analyzer.cli import EXIT_ERROR, EXIT_OK, iso_datetime, main, positive_int
from log_analyzer.console import border, boxed
from tests.helpers import DATA

ACCESS = str(DATA / "access.log")
ACCESS_2 = str(DATA / "access_2.log")


def run(tmp_path: Path, *args: str) -> tuple[int, dict[str, object]]:
    """Run the CLI with its report in ``tmp_path``; return the code and report."""
    output = tmp_path / "report.json"
    code = main([*args, "--output", str(output)])
    report = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    return code, report


def test_sample_log_gives_a_report_and_two_boxes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 0, a JSON report, and the steps and summary boxes."""
    code, report = run(tmp_path, ACCESS)
    assert code == EXIT_OK
    assert report["total_lines"] == 1200
    lines = capsys.readouterr().out.splitlines()
    assert lines[:3] == [border(), boxed("Log File Analyzer"), border()]
    assert boxed("Summary") in lines
    assert lines.count(border()) == 6
    assert any("1. Requests analyzed: 1,200" in line for line in lines)


def test_two_files_are_chained(tmp_path: Path) -> None:
    """Both sample files are read, one after the other."""
    _, report = run(tmp_path, ACCESS, ACCESS_2)
    assert report["files"] == [ACCESS, ACCESS_2]
    assert report["total_lines"] == 1500


def test_filter_options(tmp_path: Path) -> None:
    """Status, method, time window and paging options reach the report."""
    _, report = run(
        tmp_path,
        ACCESS,
        "--status",
        "404",
        "--status",
        "500",
        "--method",
        "get",
        "--from",
        "2026-10-20T00:00",
        "--to",
        "2026-10-20T12:00",
        "--top",
        "2",
        "--page",
        "2",
        "--per-page",
        "3",
    )
    filters = report["filters"]
    assert isinstance(filters, dict)
    assert filters["statuses"] == "404, 500"
    assert filters["method"] == "GET"
    page = report["page"]
    assert isinstance(page, dict)
    assert page["number"] == 2
    assert len(page["entries"]) == 3
    assert all(entry["status"] in (404, 500) for entry in page["entries"])


def test_errors_only_and_verbose(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--errors-only`` keeps 4xx/5xx; ``-v`` still prints the boxes."""
    code, report = run(tmp_path, ACCESS, "--errors-only", "-v")
    assert code == EXIT_OK
    summary = report["summary"]
    assert isinstance(summary, dict)
    assert summary["error_rate"] == 100.0
    assert "Summary" in capsys.readouterr().out


def test_missing_file_gives_exit_code_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A clear error on stderr, the steps box closed, no report."""
    code, report = run(tmp_path, "missing.log")
    assert code == EXIT_ERROR
    assert not report
    captured = capsys.readouterr()
    assert captured.err.startswith("Error: Log file not found")
    assert captured.out.splitlines()[-1] == border()


@pytest.mark.parametrize(
    "args",
    [["--from", "yesterday"], ["--top", "0"], ["--page", "x"]],
    ids=["bad time", "top 0", "page not a number"],
)
def test_bad_option_values_exit_with_code_2(tmp_path: Path, args: list[str]) -> None:
    """``argparse`` rejects bad values before anything runs."""
    with pytest.raises(SystemExit) as stop:
        run(tmp_path, ACCESS, *args)
    assert stop.value.code == 2


def test_iso_datetime_assumes_utc_without_a_timezone() -> None:
    """A time without an offset is taken as UTC; an offset is kept."""
    assert iso_datetime("2026-10-20T09:00") == datetime(2026, 10, 20, 9, tzinfo=UTC)
    with_offset = iso_datetime("2026-10-20T09:00+02:00")
    assert with_offset.utcoffset() == timedelta(hours=2)
    assert with_offset.tzinfo == timezone(timedelta(hours=2))


def test_positive_int() -> None:
    """Whole numbers of at least 1 only."""
    assert positive_int("3") == 3
    for bad in ("0", "-1", "two"):
        with pytest.raises(argparse.ArgumentTypeError):
            positive_int(bad)
