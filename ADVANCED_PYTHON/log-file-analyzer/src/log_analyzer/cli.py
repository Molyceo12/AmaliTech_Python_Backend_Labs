"""Command-line interface: ``log-analyzer data/access.log [more files] [options]``."""

import argparse
import logging
import sys
from collections.abc import Sequence
from datetime import UTC, datetime

from log_analyzer.console import border, box_header, format_summary, step_printer
from log_analyzer.decorators import last_duration
from log_analyzer.exceptions import LogAnalyzerError
from log_analyzer.services import AnalyzerOptions, AnalyzerService

DEFAULT_OUTPUT = "output/report.json"
EXIT_OK = 0
EXIT_ERROR = 1


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
        "-v", "--verbose", action="store_true", help="show timing and call tracing"
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
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    service = AnalyzerService(on_step=step_printer())
    print(box_header("Log File Analyzer"))
    try:
        result = service.run(args.paths, args.output, options_from(args))
    except LogAnalyzerError as error:
        print(border())
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(border())
    print()
    print(format_summary(result, last_duration(service.run)))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
