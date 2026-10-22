"""JSON implementation of the report writer."""

import json
from pathlib import Path

from log_analyzer.exceptions import ReportWriteError
from log_analyzer.models import LogReport
from log_analyzer.writers.base import ReportWriter


class JsonReportWriter(ReportWriter):
    """Writes the report as indented JSON."""

    def write(self, report: LogReport, path: str | Path) -> Path:
        """Write the report as indented JSON, creating its folder if needed.

        Returns:
            The path the report was written to.

        Raises:
            ReportWriteError: If the folder or the file cannot be written.
        """
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8") as handle:
                json.dump(report, handle, indent=2)
                handle.write("\n")
        except OSError as error:
            raise ReportWriteError(f"Cannot write report {target}: {error}") from error
        return target
