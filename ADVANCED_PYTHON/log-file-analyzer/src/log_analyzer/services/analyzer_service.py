"""Analyzer service: read → parse → filter → report → write, for some log files."""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from operator import attrgetter
from pathlib import Path

from log_analyzer.decorators import log_call, timer
from log_analyzer.models import LogEntry, LogReport
from log_analyzer.parsing import parse_line
from log_analyzer.pipeline import (
    errors_by_status,
    paginate,
    requests_per_hour,
    select_all,
    summarize,
    time_window,
    to_records,
)
from log_analyzer.readers import Batches, read_many
from log_analyzer.services.options import AnalyzerOptions
from log_analyzer.writers import write_report

# Called after each finished step with the step name and a short detail.
StepCallback = Callable[[str, str], None]
ReportWriter = Callable[[LogReport, Path], Path]

BATCH_SIZE = 500  # lines parsed per batch
EARLIEST = datetime.min.replace(tzinfo=UTC)
LATEST = datetime.max.replace(tzinfo=UTC)


def _ignore_step(*_: str) -> None:
    """Default step callback: report nothing."""


@dataclass(frozen=True)
class ParsedLines:
    """What reading and parsing the files produced."""

    entries: list[LogEntry]
    total_lines: int

    @property
    def skipped_lines(self) -> int:
        """Lines that did not match any log format."""
        return self.total_lines - len(self.entries)


@dataclass(frozen=True)
class AnalysisResult:
    """What one run produced: the report and where it was written."""

    report: LogReport
    output_path: Path


@dataclass
class AnalyzerService:
    """Runs a full analysis of one or more log files.

    Attributes:
        writer: Saves the report (``write_report`` by default; tests use a mock).
        on_step: Called after each finished step, e.g. to show progress.
        batch_size: How many lines are parsed per batch.
    """

    writer: ReportWriter = write_report
    on_step: StepCallback = _ignore_step
    batch_size: int = BATCH_SIZE

    def read_and_parse(self, paths: Iterable[str | Path]) -> ParsedLines:
        """Stream the lines of every file in batches and keep the valid entries.

        Lines come from a generator (``read_many``) and are parsed batch by
        batch, so only one batch of raw lines is in memory at a time.
        """
        entries: list[LogEntry] = []
        total = 0
        for batch in Batches(read_many(paths), self.batch_size):
            total += len(batch)
            entries.extend(filter(None, map(parse_line, batch)))
        return ParsedLines(entries, total)

    @staticmethod
    def select(entries: list[LogEntry], options: AnalyzerOptions) -> list[LogEntry]:
        """Apply the option filters, then the time window, oldest entry first."""
        matching = select_all(options.predicates(), entries)
        in_order = sorted(matching, key=attrgetter("timestamp"))
        if options.start is None and options.end is None:
            return in_order
        start = options.start or EARLIEST
        end = options.end or LATEST
        return list(time_window(start, end, in_order))

    @staticmethod
    def build_report(
        paths: Sequence[str | Path],
        parsed: ParsedLines,
        selected: list[LogEntry],
        options: AnalyzerOptions,
    ) -> LogReport:
        """Put every section of the report together."""
        page = paginate(selected, options.page, options.per_page)
        return {
            "files": [str(path) for path in paths],
            "total_lines": parsed.total_lines,
            "parsed_lines": len(parsed.entries),
            "skipped_lines": parsed.skipped_lines,
            "filters": options.describe(),
            "summary": summarize(selected, options.top),
            "requests_per_hour": requests_per_hour(selected),
            "errors_by_status": errors_by_status(selected),
            "page": {
                "number": options.page,
                "per_page": options.per_page,
                "entries": list(to_records(page)),
            },
        }

    @timer
    @log_call
    def run(
        self,
        paths: Sequence[str | Path],
        output: str | Path,
        options: AnalyzerOptions | None = None,
    ) -> AnalysisResult:
        """Analyze the log files and write the JSON report.

        ``@timer`` (outer) measures the whole run, including the ``@log_call``
        tracing; read the time with ``last_duration(service.run)``.

        Raises:
            LogFileError: If a log file cannot be read.
            ReportWriteError: If the report cannot be written.
            ValueError: If the page settings are less than 1.
        """
        settings = options or AnalyzerOptions()
        parsed = self.read_and_parse(paths)
        self.on_step(
            f"Reading {len(paths)} file(s)",
            f"{parsed.total_lines:,} lines, {parsed.skipped_lines:,} skipped",
        )

        selected = self.select(parsed.entries, settings)
        self.on_step("Filtering the entries", f"{len(selected):,} entries match")

        report = self.build_report(paths, parsed, selected, settings)
        self.on_step(
            "Building the report",
            f"{len(report['requests_per_hour'])} hour(s), "
            f"{len(report['summary']['requests_per_status'])} status code(s)",
        )

        written = self.writer(report, Path(output))
        self.on_step("Writing the JSON report", "1 file")
        return AnalysisResult(report, written)
