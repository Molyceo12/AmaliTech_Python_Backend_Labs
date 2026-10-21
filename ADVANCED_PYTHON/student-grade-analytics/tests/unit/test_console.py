"""Tests for the bordered terminal output."""

from pathlib import Path
from typing import List, Optional, cast

import pytest

from grade_analytics.console import (
    BOX_WIDTH,
    border,
    box_header,
    boxed,
    format_summary,
    step_printer,
)
from grade_analytics.models import GradeReport, RowProblem
from grade_analytics.services import AnalysisResult

REPORT_PATH = Path("out/report.json")


def make_result(
    charts: Optional[List[Path]] = None, problems: Optional[List[RowProblem]] = None
) -> AnalysisResult:
    """Return a run result; only the paths and problems matter for the summary."""
    return AnalysisResult(
        cast(GradeReport, {}), problems or [], REPORT_PATH, charts or []
    )


def test_border_fills_the_box_width() -> None:
    """A border is one line of colons as wide as the box."""
    assert border() == ":" * BOX_WIDTH


def test_boxed_pads_lines_to_the_box_width() -> None:
    """Short text is padded so the right border lines up."""
    line = boxed("hi")
    assert len(line) == BOX_WIDTH
    assert line.startswith("::  hi ")
    assert line.endswith("  ::")


def test_boxed_long_text_pushes_the_border_out() -> None:
    """Text wider than the box is kept whole, not cut."""
    text = "x" * BOX_WIDTH
    assert boxed(text) == f"::  {text}::"


def test_box_header_is_border_title_border() -> None:
    """A box starts with a border, the title line and another border."""
    assert box_header("Title").splitlines() == [border(), boxed("Title"), border()]


def test_step_printer_numbers_each_step(capsys: pytest.CaptureFixture[str]) -> None:
    """Every step gets the next number, dots up to the column and its detail."""
    show = step_printer()
    show("Reading", "2 students")
    show("Writing", "1 file")
    first, second = capsys.readouterr().out.splitlines()
    assert first.startswith("::  1. Reading ....")
    assert "done (2 students)" in first
    assert second.startswith("::  2. Writing ....")
    assert first.index("done") == second.index("done")  # lined up


def test_summary_lists_every_saved_file() -> None:
    """The report comes first, then one line per chart, in a closed box."""
    chart = Path("out/top_performers.png")
    lines = format_summary(make_result(charts=[chart])).splitlines()
    assert lines[:3] == box_header("Summary").splitlines()
    assert lines[3] == boxed(f"1. JSON report saved to {REPORT_PATH}")
    assert lines[4] == boxed(f"2. Top performers chart saved to {chart}")
    assert lines[-1] == border()


def test_summary_lists_skipped_rows() -> None:
    """Skipped rows are listed inside the summary box."""
    result = make_result(problems=[RowProblem(3, "'name' is empty")])
    lines = format_summary(result).splitlines()
    assert boxed("Skipped rows (1):") in lines
    assert boxed("  Line 3: 'name' is empty") in lines


def test_summary_has_no_skipped_section_without_problems() -> None:
    """A clean run shows only the saved files."""
    assert "Skipped rows" not in format_summary(make_result())
