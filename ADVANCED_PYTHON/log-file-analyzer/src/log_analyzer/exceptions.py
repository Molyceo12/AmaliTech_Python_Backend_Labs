"""Custom exceptions: every expected problem is a ``LogAnalyzerError``."""


class LogAnalyzerError(Exception):
    """Base class for all errors raised by the log analyzer."""


class LogFileError(LogAnalyzerError):
    """A log file cannot be used."""


class LogFileNotFoundError(LogFileError):
    """The log file does not exist."""


class LogFilePermissionError(LogFileError):
    """The log file exists but cannot be opened (no permission)."""


class ReportWriteError(LogAnalyzerError):
    """The report file cannot be written."""
