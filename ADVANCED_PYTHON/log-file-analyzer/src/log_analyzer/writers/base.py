"""Writer interface: where the report goes."""

from abc import ABC, abstractmethod
from pathlib import Path

from log_analyzer.models import LogReport


class ReportWriter(ABC):
    """What any report writer must do; the service depends only on this.

    Other formats (CSV, Markdown, HTML) can be added by subclassing, without
    changing the service.
    """

    @abstractmethod
    def write(self, report: LogReport, path: str | Path) -> Path:
        """Save the report and return the path it was written to.

        Raises:
            ReportWriteError: If the report cannot be written.
        """
