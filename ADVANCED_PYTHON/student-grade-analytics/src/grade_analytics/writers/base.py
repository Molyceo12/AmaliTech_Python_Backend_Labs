"""Report writer interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from grade_analytics.models import GradeReport


class ReportWriter(ABC):
    """What any report writer must do; the service depends only on this."""

    @abstractmethod
    def write(self, report: GradeReport, path: Union[str, Path]) -> Path:
        """Save a report.

        Args:
            report: The report to save.
            path: Where to save it.

        Returns:
            The path the report was written to.

        Raises:
            ReportWriteError: If the report cannot be written.
        """
