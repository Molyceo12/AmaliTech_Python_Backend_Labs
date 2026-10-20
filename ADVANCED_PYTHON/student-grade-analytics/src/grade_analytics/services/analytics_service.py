"""Analytics service: read → analyse → write, for one data file."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

from grade_analytics.analytics import build_report
from grade_analytics.models import GradeReport, RowProblem
from grade_analytics.readers import RecordReader, build_students
from grade_analytics.writers import ReportWriter


@dataclass(frozen=True)
class AnalysisResult:
    """What one run produced.

    Attributes:
        report: The report that was written.
        problems: Rows that were skipped, and why.
        output_path: Where the report was written.
    """

    report: GradeReport
    problems: List[RowProblem]
    output_path: Path


@dataclass
class AnalyticsService:
    """Coordinates the reader, the analysis and the writer.

    The reader and writer are passed in as interfaces (dependency
    inversion), so other formats or test mocks can be used without
    changing this class.

    Attributes:
        reader: Source of raw records.
        writer: Destination of the report.
        top_n: How many top performers the report lists.
        window: How many semesters the rolling average covers.
    """

    reader: RecordReader
    writer: ReportWriter
    top_n: int = 5
    window: int = 3

    def run(
        self, input_path: Union[str, Path], output_path: Union[str, Path]
    ) -> AnalysisResult:
        """Analyse one data file and write its report.

        Args:
            input_path: Data file to read.
            output_path: Where to write the report.

        Returns:
            The report, the skipped rows and the written path.

        Raises:
            DataFileError: If the data file cannot be read.
            ReportWriteError: If the report cannot be written.
        """
        data = build_students(self.reader.read(input_path))
        report = build_report(data, top_n=self.top_n, window=self.window)
        written = self.writer.write(report, output_path)
        return AnalysisResult(report, data.problems, written)
