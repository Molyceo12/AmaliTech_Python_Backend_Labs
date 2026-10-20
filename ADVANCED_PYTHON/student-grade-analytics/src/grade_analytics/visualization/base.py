"""Visualizer interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from grade_analytics.models import GradeReport


class ReportVisualizer(ABC):
    """What any chart generator must do; the service depends only on this."""

    @abstractmethod
    def render(self, report: GradeReport, output_dir: Union[str, Path]) -> List[Path]:
        """Draw charts for a report and save them in a folder.

        Args:
            report: The report to draw.
            output_dir: Folder for the chart files (created if missing).

        Returns:
            The chart files that were written (charts without data are skipped).

        Raises:
            ReportWriteError: If a chart cannot be saved.
        """
