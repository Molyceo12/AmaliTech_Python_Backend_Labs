"""Analytics service: read → analyse → write (→ charts), for one data file."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from grade_analytics.analytics import build_report
from grade_analytics.models import GradeReport, RowProblem
from grade_analytics.readers import RecordReader, build_students
from grade_analytics.visualization import ReportVisualizer
from grade_analytics.writers import ReportWriter

# Called after each finished step with the step name and a short detail.
StepCallback = Callable[[str, str], None]


def _ignore_step(*_: str) -> None:
    """Default step callback: report nothing."""


@dataclass(frozen=True)
class AnalysisResult:
    """What one run produced.

    Attributes:
        report: The report that was written.
        problems: Rows that were skipped, and why.
        output_path: Where the report was written.
        chart_paths: Chart files written next to the report (may be empty).
    """

    report: GradeReport
    problems: List[RowProblem]
    output_path: Path
    chart_paths: List[Path] = field(default_factory=list)


@dataclass
class AnalyticsService:
    """Coordinates the reader, the analysis, the writer and the charts.

    The reader, writer and visualizer are passed in as interfaces
    (dependency inversion), so other formats or test mocks can be used
    without changing this class.

    Attributes:
        reader: Source of raw records.
        writer: Destination of the report.
        visualizer: Chart generator; ``None`` to skip charts.
        top_n: How many top performers the report lists.
        window: How many semesters the rolling average covers.
        on_step: Called after each finished step, e.g. to show progress.
    """

    reader: RecordReader
    writer: ReportWriter
    visualizer: Optional[ReportVisualizer] = None
    top_n: int = 5
    window: int = 3
    on_step: StepCallback = _ignore_step

    def run(
        self, input_path: Union[str, Path], output_path: Union[str, Path]
    ) -> AnalysisResult:
        """Analyse one data file, write its report and its charts.

        Charts are saved in the same folder as the report.

        Args:
            input_path: Data file to read.
            output_path: Where to write the report.

        Returns:
            The report, the skipped rows, the report path and the chart files.

        Raises:
            DataFileError: If the data file cannot be read.
            ReportWriteError: If the report or a chart cannot be written.
        """
        data = build_students(self.reader.read(input_path))
        grades = sum(len(student.grades) for student in data.students)
        detail = f"{len(data.students)} students, {grades} grades"
        if data.problems:
            detail += f", {len(data.problems)} rows skipped"
        self.on_step(f"Reading {input_path}", detail)

        report = build_report(data, top_n=self.top_n, window=self.window)
        self.on_step("Calculating statistics", "report built")

        written = self.writer.write(report, output_path)
        self.on_step("Writing the JSON report", "1 file")

        charts: List[Path] = []
        if self.visualizer is not None:
            charts = self.visualizer.render(report, written.parent)
            self.on_step("Drawing the charts", f"{len(charts)} files")
        return AnalysisResult(report, data.problems, written, charts)
