"""Analyzer service: read → parse → filter → report → write, for some log files."""

import logging
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from operator import attrgetter
from pathlib import Path

from log_analyzer.decorators import log_call, timer
from log_analyzer.models import LogEntry, LogReport
from log_analyzer.parsing import ApacheLogParser, LogParser
from log_analyzer.patterns.validators import find_ip
from log_analyzer.pipeline import (
    errors_by_status,
    paginate,
    referrer_ips,
    requests_per_hour,
    select_all,
    summarize,
    time_window,
    to_records,
)
from log_analyzer.readers import Batches, FileLogReader, LogReader
from log_analyzer.services.options import AnalyzerOptions
from log_analyzer.writers import JsonReportWriter, ReportWriter

# Called after each finished step with the step name and a short detail.
StepCallback = Callable[[str, str], None]

logger = logging.getLogger(__name__)

BATCH_SIZE = 500  # lines parsed per batch
EARLIEST = datetime.min.replace(tzinfo=UTC)
LATEST = datetime.max.replace(tzinfo=UTC)
UNKNOWN_IP = "unknown"  # skipped line with no IPv4 address in it


def _ignore_step(*_: str) -> None:
    """Default step callback: report nothing."""


@dataclass(frozen=True)
class ParsedLines:
    """What reading and parsing the files produced."""

    entries: list[LogEntry]
    total_lines: int
    skipped_by_ip: dict[str, int] = field(default_factory=dict)

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

    The reader, parser and writer are passed in as interfaces (dependency
    inversion), so other sources, formats or test mocks can be used without
    changing this class.

    Attributes:
        reader: Where the lines come from (``FileLogReader`` by default).
        parser: How a line becomes an entry (``ApacheLogParser`` by default).
        writer: Where the report goes (``JsonReportWriter`` by default).
        on_step: Called after each finished step, e.g. to show progress.
        batch_size: How many lines are parsed per batch.
    """

    reader: LogReader = field(default_factory=FileLogReader)
    parser: LogParser = field(default_factory=ApacheLogParser)
    writer: ReportWriter = field(default_factory=JsonReportWriter)
    on_step: StepCallback = _ignore_step
    batch_size: int = BATCH_SIZE

    def read_and_parse(self, paths: Iterable[str | Path]) -> ParsedLines:
        """Stream the lines of every file in batches and keep the valid entries.

        Lines come from the reader's generator and are parsed batch by batch,
        so only one batch of raw lines is in memory at a time. For each
        skipped line, ``re.search`` looks for the client IP so the report can
        show who sent it.
        """
        entries: list[LogEntry] = []
        skipped: Counter[str] = Counter()
        total = 0
        for batch in Batches(self.reader.read(paths), self.batch_size):
            total += len(batch)
            results = list(map(self.parser.parse, batch))
            entries.extend(filter(None, results))
            skipped.update(
                find_ip(line) or UNKNOWN_IP
                for line, entry in zip(batch, results, strict=True)
                if entry is None
            )
        return ParsedLines(entries, total, dict(skipped.most_common()))

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
            "skipped_by_ip": parsed.skipped_by_ip,
            "filters": options.describe(),
            "summary": summarize(selected, options.top),
            "requests_per_hour": requests_per_hour(selected),
            "errors_by_status": errors_by_status(selected),
            "referrer_ips": referrer_ips(selected),
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
        logger.info(
            "Analyzing %s with filters %s",
            ", ".join(map(str, paths)),
            settings.describe(),
        )
        parsed = self.read_and_parse(paths)
        self._step(
            f"Reading {len(paths)} file(s)",
            f"{parsed.total_lines:,} lines, {parsed.skipped_lines:,} skipped",
        )
        if parsed.skipped_lines:
            logger.warning(
                "%s line(s) did not match any log format and were skipped",
                parsed.skipped_lines,
            )

        selected = self.select(parsed.entries, settings)
        self._step("Filtering the entries", f"{len(selected):,} entries match")
        if not selected:
            logger.warning("No entries match the filters; the report is empty")

        report = self.build_report(paths, parsed, selected, settings)
        self._step(
            "Building the report",
            f"{len(report['requests_per_hour'])} hour(s), "
            f"{len(report['summary']['requests_per_status'])} status code(s)",
        )

        written = self.writer.write(report, Path(output))
        self._step("Writing the JSON report", "1 file")
        logger.info("Report written to %s", written)
        return AnalysisResult(report, written)

    def _step(self, step: str, detail: str) -> None:
        """Log a finished step (INFO) and pass it to ``on_step``."""
        logger.info("%s: %s", step, detail)
        self.on_step(step, detail)
