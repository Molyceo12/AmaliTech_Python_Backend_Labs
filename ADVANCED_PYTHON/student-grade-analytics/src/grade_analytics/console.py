"""Terminal output: bordered boxes for the progress steps and the summary.

Only the look of the output lives here; ``cli.py`` decides when to print it.
"""

from itertools import count

from grade_analytics.services import AnalysisResult, StepCallback

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


def box_header(title: str) -> str:
    """Return the top of a box: border, title line, border."""
    return "\n".join([border(), boxed(title), border()])


def step_printer() -> StepCallback:
    """Return a step callback that prints numbered progress lines in the box.

    Each finished step prints e.g.
    ``::  1. Reading data/students.csv ........ done (16 students, 48 grades)  ::``.
    """
    numbers = count(1)

    def show(step: str, detail: str) -> None:
        line = f"{next(numbers)}. {step} ".ljust(STEP_WIDTH, ".")
        print(boxed(f"{line} done ({detail})"), flush=True)

    return show


def format_summary(result: AnalysisResult) -> str:
    """Return the summary box printed after a successful run.

    Args:
        result: Output of ``AnalyticsService.run``.

    Returns:
        One numbered line per saved file, then the skipped rows (if any),
        inside a bordered box.
    """
    saved = [("JSON report", result.output_path)]
    saved += [
        (f"{path.stem.replace('_', ' ').capitalize()} chart", path)
        for path in result.chart_paths
    ]
    lines = [
        f"{number}. {name} saved to {path}"
        for number, (name, path) in enumerate(saved, start=1)
    ]
    if result.problems:
        lines += ["", f"Skipped rows ({len(result.problems)}):"]
        lines += [
            f"  Line {problem.line_number}: {problem.reason}"
            for problem in result.problems
        ]
    body = [boxed(line) for line in lines]
    return "\n".join([box_header("Summary"), *body, border()])
