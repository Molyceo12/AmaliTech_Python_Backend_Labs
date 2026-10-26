"""JSON implementation of the report writer."""

import json
import logging
from pathlib import Path
from typing import Union

from grade_analytics.exceptions import ReportWriteError
from grade_analytics.models import GradeReport
from grade_analytics.utils import atomic_write
from grade_analytics.writers.base import ReportWriter

logger = logging.getLogger(__name__)


class JsonReportWriter(ReportWriter):
    """Writes reports as indented JSON, atomically."""

    def __init__(self, indent: int = 2) -> None:
        """Create a writer.

        Args:
            indent: Spaces per indentation level in the JSON file.
        """
        self.indent = indent

    def write(self, report: GradeReport, path: Union[str, Path]) -> Path:
        """Write the report to a JSON file, creating its folder if needed.

        Args:
            report: The report to save.
            path: Target ``.json`` file.

        Returns:
            The path the report was written to.

        Raises:
            ReportWriteError: If the folder or file cannot be written.
        """
        target = Path(path)
        try:
            with atomic_write(target) as handle:
                json.dump(report, handle, indent=self.indent, ensure_ascii=False)
                handle.write("\n")
        except OSError as error:
            raise ReportWriteError(f"Cannot write report {target}: {error}") from error
        logger.info("Report written to %s", target)
        return target
