"""Tests for the analyzer service, with small temp log files."""

from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from log_analyzer.decorators import last_duration
from log_analyzer.exceptions import LogFileNotFoundError, ReportWriteError
from log_analyzer.services import AnalyzerOptions, AnalyzerService
from tests.conftest import WriteLog
from tests.helpers import COMBINED_LINE, COMMON_LINE, TIMESTAMP

# Common line at 09:05 with status 302; make a 404 and a 500 variant.
NOT_FOUND = COMMON_LINE.replace(" 302 ", " 404 ")
SERVER_ERROR = COMMON_LINE.replace(" 302 ", " 500 ").replace("09:05", "10:30")


@pytest.fixture(name="writer")
def fixture_writer() -> MagicMock:
    """Return a mock writer that returns the path it is given."""
    return MagicMock(side_effect=lambda report, path: path)


@pytest.fixture(name="log_file")
def fixture_log_file(write_log: WriteLog) -> Path:
    """Return a log with 4 good lines (combined, 302, 404, 500) and 1 bad line."""
    return write_log([COMBINED_LINE, COMMON_LINE, "garbage", NOT_FOUND, SERVER_ERROR])


def test_run_builds_every_section(
    log_file: Path, writer: MagicMock, tmp_path: Path
) -> None:
    """The report has totals, sections and one page of records."""
    output = tmp_path / "report.json"
    result = AnalyzerService(writer).run([log_file], output)
    report = result.report
    assert report["files"] == [str(log_file)]
    assert report["total_lines"] == 5
    assert report["parsed_lines"] == 4
    assert report["skipped_lines"] == 1
    assert report["summary"]["total_requests"] == 4
    assert report["errors_by_status"] == {"404": 1, "500": 1}
    assert report["requests_per_hour"] == {"09": 2, "10": 1, "13": 1}
    assert report["page"]["number"] == 1
    assert [entry["status"] for entry in report["page"]["entries"]] == [
        302,
        404,
        500,
        200,
    ]  # oldest first
    writer.assert_called_once_with(report, output)
    assert result.output_path == output


def test_run_applies_the_filters(log_file: Path, writer: MagicMock) -> None:
    """Only matching entries are counted; the filters are listed."""
    options = AnalyzerOptions(errors_only=True, top=1)
    report = AnalyzerService(writer).run([log_file], "out.json", options).report
    assert report["summary"]["total_requests"] == 2
    assert report["filters"] == {"errors_only": "yes"}
    assert len(report["summary"]["top_ips"]) == 1


@pytest.mark.parametrize(
    ("start_hours", "end_hours", "expected"),
    # Entries at 09:05, 09:05, 10:30 and 13:55; TIMESTAMP is 13:55.
    [(None, -4, 2), (-4, None, 2), (-4.5, 1, 2)],
    ids=["only end", "only start", "both"],
)
def test_run_applies_the_time_window(
    log_file: Path,
    writer: MagicMock,
    start_hours: float | None,
    end_hours: float | None,
    expected: int,
) -> None:
    """``--from`` and ``--to`` can be used alone or together."""
    hour = timedelta(hours=1)
    options = AnalyzerOptions(
        start=None if start_hours is None else TIMESTAMP + start_hours * hour,
        end=None if end_hours is None else TIMESTAMP + end_hours * hour,
    )
    report = AnalyzerService(writer).run([log_file], "out.json", options).report
    assert report["summary"]["total_requests"] == expected


def test_run_reads_several_files_in_batches(
    write_log: WriteLog, writer: MagicMock
) -> None:
    """Files are chained and parsed in batches smaller than the input."""
    first = write_log([COMBINED_LINE] * 3, "a.log")
    second = write_log([COMMON_LINE] * 2, "b.log")
    report = AnalyzerService(writer, batch_size=2).run([first, second], "x").report
    assert report["total_lines"] == 5
    assert report["summary"]["total_requests"] == 5


def test_run_reports_each_step(log_file: Path, writer: MagicMock) -> None:
    """``on_step`` is called after every step, in order."""
    on_step = MagicMock()
    AnalyzerService(writer, on_step).run([log_file], "out.json")
    assert [call.args for call in on_step.call_args_list] == [
        ("Reading 1 file(s)", "5 lines, 1 skipped"),
        ("Filtering the entries", "4 entries match"),
        ("Building the report", "3 hour(s), 4 status code(s)"),
        ("Writing the JSON report", "1 file"),
    ]


def test_run_is_timed(log_file: Path, writer: MagicMock) -> None:
    """``@timer`` on ``run`` records how long the last run took."""
    service = AnalyzerService(writer)
    service.run([log_file], "out.json")
    assert last_duration(service.run) > 0


def test_missing_file_stops_before_writing(writer: MagicMock) -> None:
    """A file error propagates and nothing is written."""
    with pytest.raises(LogFileNotFoundError):
        AnalyzerService(writer).run(["missing.log"], "out.json")
    writer.assert_not_called()


def test_bad_page_settings_are_rejected(log_file: Path, writer: MagicMock) -> None:
    """Page numbers start at 1."""
    with pytest.raises(ValueError, match="at least 1"):
        AnalyzerService(writer).run([log_file], "out.json", AnalyzerOptions(page=0))


def test_real_writer_errors_become_report_write_errors(
    log_file: Path, tmp_path: Path
) -> None:
    """A folder that cannot be created gives ``ReportWriteError``."""
    blocker = tmp_path / "taken"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises(ReportWriteError, match="Cannot write report"):
        AnalyzerService().run([log_file], blocker / "report.json")
