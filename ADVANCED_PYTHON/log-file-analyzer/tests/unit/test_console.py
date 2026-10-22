"""Tests for the bordered terminal output."""

from pathlib import Path

import pytest

from log_analyzer.console import (
    BOX_WIDTH,
    border,
    box_header,
    boxed,
    centered,
    format_summary,
    step_printer,
)
from log_analyzer.models import LogReport
from log_analyzer.pipeline import summarize
from log_analyzer.services import AnalysisResult
from tests.helpers import SAMPLE_ENTRIES

REPORT_PATH = Path("out/report.json")


def make_report(per_hour: dict[str, int], with_entries: bool = True) -> LogReport:
    """Return a report with only the fields the summary box uses."""
    return {
        "files": ["a.log"],
        "total_lines": 7,
        "parsed_lines": 5,
        "skipped_lines": 2,
        "filters": {},
        "summary": summarize(SAMPLE_ENTRIES if with_entries else [], top=2),
        "requests_per_hour": per_hour,
        "errors_by_status": {},
        "page": {"number": 1, "per_page": 20, "entries": []},
    }


def test_border_and_boxed_line_up() -> None:
    """Borders and padded lines have the same width."""
    assert border() == ":" * BOX_WIDTH
    assert len(boxed("hi")) == BOX_WIDTH
    assert boxed("hi").startswith("::  hi ")
    assert boxed("hi").endswith("  ::")


def test_long_text_pushes_the_border_out() -> None:
    """Nothing is cut off."""
    text = "x" * BOX_WIDTH
    assert boxed(text) == f"::  {text}::"


def test_box_header_centers_the_title() -> None:
    """Border, centered title, border."""
    assert box_header("T").splitlines() == [border(), centered("T"), border()]


def test_centered_puts_text_in_the_middle() -> None:
    """Same width as the box, equal space on both sides of the text."""
    line = centered("Summary")
    assert len(line) == BOX_WIDTH
    left, right = line[2:-2].split("Summary")
    assert abs(len(left) - len(right)) <= 1


def test_step_printer_numbers_and_aligns_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each step gets the next number; the ``done`` words line up."""
    show = step_printer()
    show("Reading", "2 files")
    show("Writing the report", "1 file")
    first, second = capsys.readouterr().out.splitlines()
    assert first.startswith("::  1. Reading ....")
    assert second.startswith("::  2. Writing the report ....")
    assert first.index("done") == second.index("done")
    assert "done (2 files)" in first


def test_summary_box_lines() -> None:
    """Totals, errors, busiest hour, report path, time and top IPs."""
    result = AnalysisResult(make_report({"09": 3, "13": 7}), REPORT_PATH)
    lines = format_summary(result, 0.1234).splitlines()
    assert lines[:3] == box_header("Summary").splitlines()
    assert boxed("1. Requests analyzed: 5 (2 lines skipped)") in lines
    assert boxed("2. Errors: 2 (40.0 %)") in lines
    assert boxed("3. Busiest hour: 13:00 (7 requests)") in lines
    assert boxed(f"4. Report saved to {REPORT_PATH}") in lines
    assert boxed("5. Run time: 0.123 s") in lines
    assert boxed("6. Top IPs:") in lines
    assert boxed("     10.0.0.1 (3 requests)") in lines
    assert lines[-1] == border()


def test_summary_box_shows_the_log_file() -> None:
    """When a log file was written, its path is the last line."""
    result = AnalysisResult(make_report({"09": 1}), REPORT_PATH)
    lines = format_summary(result, 0.0, Path("output/run.log")).splitlines()
    assert lines[-2] == boxed(f"7. Log saved to {Path('output/run.log')}")


def test_summary_box_without_requests() -> None:
    """An empty report shows dashes instead of failing."""
    result = AnalysisResult(make_report({}, with_entries=False), REPORT_PATH)
    lines = format_summary(result, 0.0).splitlines()
    assert boxed("3. Busiest hour: -") in lines
    assert boxed("6. Top IPs: -") in lines
