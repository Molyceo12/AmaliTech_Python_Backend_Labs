"""Command-line interface: ``python -m grade_analytics.cli data/students.csv``."""

import argparse
import sys
from collections.abc import Sequence
from typing import Optional

from grade_analytics.console import border, box_header, format_summary, step_printer
from grade_analytics.exceptions import GradeAnalyticsError
from grade_analytics.readers import CsvRecordReader
from grade_analytics.services import AnalyticsService
from grade_analytics.visualization import MatplotlibVisualizer
from grade_analytics.writers import JsonReportWriter

DEFAULT_OUTPUT = "output/report.json"
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_ROWS_SKIPPED = 2


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


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="grade-analytics",
        description="Analyse student grades from a CSV file and write a JSON report.",
    )
    parser.add_argument("input_file", help="CSV file with one row per grade")
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT, help="JSON report to write"
    )
    parser.add_argument(
        "--top", type=positive_int, default=5, help="number of top performers"
    )
    parser.add_argument(
        "--window",
        type=positive_int,
        default=3,
        help="semesters in the rolling average",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="only write the JSON report, no PNG charts",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the analysis and return the exit code.

    Exit codes: 0 = success, 1 = the analysis failed, 2 = some rows skipped.
    Only this function picks the concrete reader, writer and visualizer.
    """
    args = build_parser().parse_args(argv)
    service = AnalyticsService(
        CsvRecordReader(),
        JsonReportWriter(),
        visualizer=None if args.no_charts else MatplotlibVisualizer(),
        top_n=args.top,
        window=args.window,
        on_step=step_printer(),
    )
    print(box_header("Student Grade Analytics"))
    try:
        result = service.run(args.input_file, args.output)
    except GradeAnalyticsError as error:
        print(border())
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_ERROR
    print(border())
    print()
    print(format_summary(result))
    return EXIT_ROWS_SKIPPED if result.problems else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
