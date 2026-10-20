"""Custom exceptions: every expected problem is a ``GradeAnalyticsError``."""


class GradeAnalyticsError(Exception):
    """Base class for all errors raised by the grade analytics tool."""


class InvalidGradeError(GradeAnalyticsError):
    """A score is not a number between 0 and 100."""


class DataFileError(GradeAnalyticsError):
    """The input data file cannot be used."""


class DataFileNotFoundError(DataFileError):
    """The input data file does not exist."""


class DataFileFormatError(DataFileError):
    """The input data file is empty, unreadable or has wrong headers."""


class ReportWriteError(GradeAnalyticsError):
    """The report file cannot be written."""
