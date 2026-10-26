"""PNG charts drawn with matplotlib's object-oriented API (no GUI, no pyplot)."""

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import List, Optional, Union

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from grade_analytics.exceptions import ReportWriteError
from grade_analytics.models import GradeReport
from grade_analytics.visualization.base import ReportVisualizer

DPI = 100
BAR_COLOR = "#4C72B0"
LINE_COLOR = "#DD8452"

logger = logging.getLogger(__name__)


class MatplotlibVisualizer(ReportVisualizer):
    """Saves the report's charts as PNG files."""

    def render(self, report: GradeReport, output_dir: Union[str, Path]) -> List[Path]:
        """Draw every chart that has data and save it as a PNG.

        Files: ``grade_distribution.png``, ``summary_statistics.png``,
        ``top_performers.png``, ``semester_trends.png``, ``course_averages.png``.

        Args:
            report: The report to draw.
            output_dir: Folder for the PNG files (created if missing).

        Returns:
            The PNG files written, in the order above.

        Raises:
            ReportWriteError: If the folder or a file cannot be written.
        """
        folder = Path(output_dir)
        charts = [
            ("grade_distribution.png", self._grade_distribution(report)),
            ("summary_statistics.png", self._summary_statistics(report)),
            ("top_performers.png", self._top_performers(report)),
            ("semester_trends.png", self._semester_trends(report)),
            ("course_averages.png", self._course_averages(report)),
        ]
        written: List[Path] = []
        try:
            folder.mkdir(parents=True, exist_ok=True)
            for name, figure in charts:
                if figure is not None:
                    path = folder / name
                    figure.savefig(path, dpi=DPI)
                    written.append(path)
                    logger.debug("Chart saved: %s", path)
        except OSError as error:
            raise ReportWriteError(f"Cannot save chart in {folder}: {error}") from error
        return written

    @staticmethod
    def _bar_figure(
        labels: Sequence[str], values: Sequence[float], title: str, ylabel: str
    ) -> Figure:
        """Vertical bar chart with each value written above its bar."""
        figure = Figure(figsize=(8, 5))
        axes: Axes = figure.add_subplot()
        bars = axes.bar(labels, values, color=BAR_COLOR)
        axes.bar_label(bars, fmt="%g")
        axes.set_title(title)
        axes.set_ylabel(ylabel)
        axes.grid(axis="y", alpha=0.3)
        figure.tight_layout()
        return figure

    def _grade_distribution(self, report: GradeReport) -> Optional[Figure]:
        """Number of grades per letter band (A–F)."""
        counts = report["grade_distribution"]
        if not any(counts.values()):
            return None
        return self._bar_figure(
            list(counts), list(counts.values()), "Grade distribution", "Grades"
        )

    def _summary_statistics(self, report: GradeReport) -> Optional[Figure]:
        """Mean, median, mode, lowest and highest score."""
        stats = report["statistics"]
        values = {
            name.capitalize(): value
            for name, value in stats.items()
            if name != "count" and isinstance(value, (int, float))
        }
        if not values:
            return None
        return self._bar_figure(
            list(values), list(values.values()), "Summary statistics", "Score"
        )

    @staticmethod
    def _top_performers(report: GradeReport) -> Optional[Figure]:
        """Horizontal bars of the top performers' averages, best on top."""
        top = report["top_performers"]
        if not top:
            return None
        figure = Figure(figsize=(8, 5))
        axes: Axes = figure.add_subplot()
        names = [f"{entry['rank']}. {entry['name']}" for entry in top]
        bars = axes.barh(names, [entry["average"] for entry in top], color=BAR_COLOR)
        axes.bar_label(bars, fmt="%.2f", padding=3)
        axes.invert_yaxis()
        axes.set_xlim(0, 105)
        axes.set_title("Top performers")
        axes.set_xlabel("Average score")
        figure.tight_layout()
        return figure

    @staticmethod
    def _semester_trends(report: GradeReport) -> Optional[Figure]:
        """Semester averages and their rolling average over time."""
        trends = report["semester_trends"]
        if not trends:
            return None
        figure = Figure(figsize=(8, 5))
        axes: Axes = figure.add_subplot()
        semesters = [trend["semester"] for trend in trends]
        axes.plot(
            semesters,
            [trend["average"] for trend in trends],
            marker="o",
            color=BAR_COLOR,
            label="Semester average",
        )
        axes.plot(
            semesters,
            [trend["rolling_average"] for trend in trends],
            marker="s",
            linestyle="--",
            color=LINE_COLOR,
            label="Rolling average",
        )
        axes.set_title("Semester trends")
        axes.set_ylabel("Average score")
        axes.legend()
        axes.grid(alpha=0.3)
        figure.tight_layout()
        return figure

    def _course_averages(self, report: GradeReport) -> Optional[Figure]:
        """Average score per course."""
        courses = report["averages_by_course"]
        if not courses:
            return None
        return self._bar_figure(
            [course["code"] for course in courses],
            [course["average"] for course in courses],
            "Course averages",
            "Average score",
        )
