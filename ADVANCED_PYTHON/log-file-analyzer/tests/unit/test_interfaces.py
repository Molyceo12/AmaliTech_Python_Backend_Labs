"""Tests for the three abstract base classes and their concrete classes."""

from collections.abc import Iterable, Iterator
from pathlib import Path

import pytest

from log_analyzer.models import LogEntry, LogReport
from log_analyzer.parsing import ApacheLogParser, LogParser, parse_line
from log_analyzer.readers import FileLogReader, LogReader
from log_analyzer.services import AnalyzerService
from log_analyzer.writers import JsonReportWriter, ReportWriter
from tests.helpers import COMBINED_LINE, COMMON_LINE, make_entry


@pytest.mark.parametrize("base", [LogReader, LogParser, ReportWriter])
def test_base_classes_cannot_be_created(base: type) -> None:
    """An abstract class has no implementation of its method."""
    with pytest.raises(TypeError, match="abstract"):
        base()


@pytest.mark.parametrize(
    ("concrete", "base"),
    [
        (FileLogReader, LogReader),
        (ApacheLogParser, LogParser),
        (JsonReportWriter, ReportWriter),
    ],
)
def test_concrete_classes_inherit_their_base(concrete: type, base: type) -> None:
    """Each concrete class is a subclass of its interface."""
    assert issubclass(concrete, base)
    assert isinstance(concrete(), base)


def test_service_uses_the_concrete_classes_by_default() -> None:
    """With no arguments the service reads files, parses Apache logs, writes JSON."""
    service = AnalyzerService()
    assert isinstance(service.reader, FileLogReader)
    assert isinstance(service.parser, ApacheLogParser)
    assert isinstance(service.writer, JsonReportWriter)


def test_apache_parser_matches_parse_line() -> None:
    """``ApacheLogParser.parse`` gives exactly what ``parse_line`` gives."""
    parser = ApacheLogParser()
    for line in (COMBINED_LINE, COMMON_LINE, "garbage"):
        assert parser.parse(line) == parse_line(line)


class ListReader(LogReader):
    """A reader that takes its lines from memory instead of files."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def read(self, paths: Iterable[str | Path]) -> Iterator[str]:
        return iter(self.lines)


class AlwaysOkParser(LogParser):
    """A parser that turns every line into the same 200 entry."""

    def parse(self, line: str) -> LogEntry | None:
        return make_entry(200)


class MemoryWriter(ReportWriter):
    """A writer that keeps the report in memory instead of on disk."""

    def __init__(self) -> None:
        self.saved: list[LogReport] = []

    def write(self, report: LogReport, path: str | Path) -> Path:
        self.saved.append(report)
        return Path(path)


def test_new_subclasses_plug_in_without_changing_the_service() -> None:
    """Open/closed: other reader, parser and writer classes just work."""
    writer = MemoryWriter()
    service = AnalyzerService(
        reader=ListReader(["a", "b", "c"]),
        parser=AlwaysOkParser(),
        writer=writer,
    )
    result = service.run(["ignored.log"], "memory.json")
    assert result.report["total_lines"] == 3
    assert result.report["summary"]["total_requests"] == 3
    assert writer.saved == [result.report]
    assert result.output_path == Path("memory.json")
