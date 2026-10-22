"""Tests for the JSON report writer."""

import json
from pathlib import Path
from typing import cast

from log_analyzer.models import LogReport
from log_analyzer.writers import JsonReportWriter

REPORT = cast(LogReport, {"files": ["a.log"], "total_lines": 3})


def test_writes_indented_json_and_creates_the_folder(tmp_path: Path) -> None:
    """The folder is created; the file is valid, indented JSON."""
    target = tmp_path / "nested" / "report.json"
    assert JsonReportWriter().write(REPORT, target) == target
    text = target.read_text(encoding="utf-8")
    assert json.loads(text) == REPORT
    assert '\n  "files"' in text
    assert text.endswith("\n")


def test_accepts_a_string_path(tmp_path: Path) -> None:
    """``str`` paths work like ``Path`` objects."""
    target = JsonReportWriter().write(REPORT, str(tmp_path / "report.json"))
    assert target.exists()
