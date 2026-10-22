"""Terminal output: bordered boxes for the progress steps and the summary.

Only the look of the output lives here; ``cli.py`` decides when to print it.
"""

from itertools import count
from pathlib import Path

from log_analyzer.models import LogReport
from log_analyzer.services import AnalysisResult, StepCallback

BOX_WIDTH = 98  # full width of the bordered boxes
STEP_WIDTH = 45  # step text is padded with dots up to this column
BORDER = ":"
SIDE = "::"


def border() -> str:
    """Return a full-width border line of colons."""
    return BORDER * BOX_WIDTH


def boxed(text: str = "") -> str:
    """Return ``text`` between ``::`` side borders, padded to the box width.

    Text longer than the box pushes the right border out instead of being cut.
    """
    return f"{SIDE}  {text}".ljust(BOX_WIDTH - len(SIDE)) + SIDE


def centered(text: str) -> str:
    """Return ``text`` in the middle of the box, between ``::`` side borders."""
    inner = BOX_WIDTH - 2 * len(SIDE)
    return f"{SIDE}{text.center(inner)}{SIDE}"


def box_header(title: str) -> str:
    """Return the top of a box: border, centered title line, border."""
    return "\n".join([border(), centered(title), border()])


def step_printer() -> StepCallback:
    """Return a step callback that prints numbered progress lines in the box.

    Each finished step prints e.g.
    ``::  1. Reading 2 file(s) ........ done (1,500 lines, 0 skipped)  ::``.
    """
    numbers = count(1)

    def show(step: str, detail: str) -> None:
        line = f"{next(numbers)}. {step} ".ljust(STEP_WIDTH, ".")
        print(boxed(f"{line} done ({detail})"), flush=True)

    return show


def _busiest_hour(report: LogReport) -> str:
    """Return e.g. ``"02:00 (57 requests)"``, or ``"-"`` with no requests."""
    per_hour = report["requests_per_hour"]
    if not per_hour:
        return "-"
    hour = max(per_hour, key=lambda name: (per_hour[name], name))
    return f"{hour}:00 ({per_hour[hour]:,} requests)"


def format_summary(
    result: AnalysisResult, seconds: float, log_file: Path | None = None
) -> str:
    """Return the summary box printed after a successful run.

    Args:
        result: Output of ``AnalyzerService.run``.
        seconds: How long the run took (from ``@timer``).
        log_file: Where the tool's own log was written, if it was.
    """
    report = result.report
    summary = report["summary"]
    top_ips = [
        f"     {item['name']} ({item['count']:,} requests)"
        for item in summary["top_ips"]
    ]
    lines = [
        f"1. Requests analyzed: {summary['total_requests']:,} "
        f"({report['skipped_lines']:,} lines skipped)",
        f"2. Errors: {summary['error_count']:,} ({summary['error_rate']} %)",
        f"3. Busiest hour: {_busiest_hour(report)}",
        f"4. Report saved to {result.output_path}",
        f"5. Run time: {seconds:.3f} s",
        f"6. Top IPs:{'' if top_ips else ' -'}",
        *top_ips,
    ]
    if log_file is not None:
        lines.append(f"7. Log saved to {log_file}")
    body = [boxed(line) for line in lines]
    return "\n".join([box_header("Summary"), *body, border()])
