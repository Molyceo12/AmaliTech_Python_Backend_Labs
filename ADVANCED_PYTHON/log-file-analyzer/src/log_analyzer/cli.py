"""Command-line interface: ``log-analyzer data/access.log [more files] [options]``."""

import argparse
import logging
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from log_analyzer.console import border, box_header, format_summary, step_printer
from log_analyzer.decorators import last_duration
from log_analyzer.exceptions import LogAnalyzerError
from log_analyzer.logging_config import (
    DEFAULT_LOG_FILE,
    PACKAGE_LOGGER,
    SHOWN_TO_USER,
    configure_logging,
)
from log_analyzer.parsing import ApacheLogParser
from log_analyzer.readers import FileLogReader
from log_analyzer.services import AnalyzerOptions, AnalyzerService
from log_analyzer.writers import JsonReportWriter

DEFAULT_OUTPUT = "output/report.json"
EXIT_OK = 0
EXIT_ERROR = 1

# Named explicitly: under "python -m log_analyzer.cli" __name__ is "__main__".
logger = logging.getLogger(f"{PACKAGE_LOGGER}.cli")


def positive_int(value: str) -> int:
    """``argparse`` type: a whole number of at least 1.

    Raises:
        argparse.ArgumentTypeError: If the value is not a positive integer.
    """
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number") from None
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {number}")
    return number


def iso_datetime(value: str) -> datetime:
    """``argparse`` type: an ISO 8601 time; no timezone means UTC.

    Example: ``2026-10-20T09:00`` or ``2026-10-20T09:00+02:00``.

    Raises:
        argparse.ArgumentTypeError: If the value is not an ISO 8601 time.
    """
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{value}' is not an ISO time like 2026-10-20T09:00"
        ) from None
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze Apache/Nginx access logs and write a JSON report.",
    )
    parser.add_argument("paths", nargs="+", help="log files, read in this order")
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT, help="JSON report to write"
    )
    parser.add_argument(
        "--status",
        type=int,
        action="append",
        default=[],
        metavar="CODE",
        help="keep only this status code (repeat for more)",
    )
    parser.add_argument(
        "--errors-only", action="store_true", help="keep only 4xx/5xx responses"
    )
    parser.add_argument("--method", help="keep only this HTTP method, e.g. GET")
    parser.add_argument(
        "--from", dest="start", type=iso_datetime, help="keep entries from this time"
    )
    parser.add_argument(
        "--to", dest="end", type=iso_datetime, help="keep entries before this time"
    )
    parser.add_argument(
        "--top", type=positive_int, default=5, help="top IPs and URLs to list"
    )
    parser.add_argument(
        "--page", type=positive_int, default=1, help="page of entries in the report"
    )
    parser.add_argument(
        "--per-page", type=positive_int, default=20, help="entries per page"
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help="where the tool writes its own log (every level)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="also show every log message in the terminal",
    )
    return parser


def options_from(args: argparse.Namespace) -> AnalyzerOptions:
    """Turn the parsed arguments into analyzer options."""
    return AnalyzerOptions(
        statuses=tuple(args.status),
        errors_only=args.errors_only,
        method=args.method,
        start=args.start,
        end=args.end,
        top=args.top,
        page=args.page,
        per_page=args.per_page,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the analysis and return the exit code (0 = success, 1 = error)."""
    args = build_parser().parse_args(argv)
    try:
        log_file = configure_logging(args.log_file, args.verbose)
    except LogAnalyzerError as error:
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_ERROR
    # The only place that picks the concrete reader, parser and writer.
    service = AnalyzerService(
        reader=FileLogReader(),
        parser=ApacheLogParser(),
        writer=JsonReportWriter(),
        on_step=step_printer(),
    )
    print(box_header("Log File Analyzer"))
    try:
        result = service.run(args.paths, args.output, options_from(args))
    except LogAnalyzerError as error:
        logger.error("Analysis failed: %s", error, extra={SHOWN_TO_USER: True})
        print(border())
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(border())
    print()
    print(format_summary(result, last_duration(service.run), log_file))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
