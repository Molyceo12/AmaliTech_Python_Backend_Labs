"""Analytics service: read → analyse → write (→ charts), for one data file."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from grade_analytics.analytics import build_report
from grade_analytics.models import GradeReport, RowProblem
from grade_analytics.readers import RecordReader, build_students
from grade_analytics.visualization import ReportVisualizer
from grade_analytics.writers import ReportWriter


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
    """

    reader: RecordReader
    writer: ReportWriter
    visualizer: Optional[ReportVisualizer] = None
    top_n: int = 5
    window: int = 3

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
        report = build_report(data, top_n=self.top_n, window=self.window)
        written = self.writer.write(report, output_path)
        charts: List[Path] = []
        if self.visualizer is not None:
            charts = self.visualizer.render(report, written.parent)
        return AnalysisResult(report, data.problems, written, charts)
