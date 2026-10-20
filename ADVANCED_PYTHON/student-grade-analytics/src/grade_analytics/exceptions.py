"""Custom exceptions: every expected problem is a ``GradeAnalyticsError``."""


class GradeAnalyticsError(Exception):
    """Base class for all errors raised by the grade analytics tool."""


class InvalidGradeError(GradeAnalyticsError):
    """A score is not a number between 0 and 100."""


class DataFileError(GradeAnalyticsError):
    """The input data file cannot be used."""


class DataFileNotFoundError(DataFileError):
    """The input data file does not exist."""


class DataFilePermissionError(DataFileError):
    """The input data file exists but cannot be opened (no permission)."""


class DataFileFormatError(DataFileError):
    """The input data file is empty, unreadable or has wrong headers."""


class InvalidRowError(DataFileError):
    """One row of the data file has a missing or invalid value."""

    def __init__(self, line_number: int, reason: str) -> None:
        """Store where the row is and what is wrong with it.

        Args:
            line_number: Line of the row in the data file.
            reason: Short description of the problem.
        """
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"Line {line_number}: {reason}")


class ReportWriteError(GradeAnalyticsError):
    """The report file cannot be written."""
