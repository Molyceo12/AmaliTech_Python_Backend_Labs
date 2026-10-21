"""Custom exceptions: every expected problem is a ``LogAnalyzerError``."""


class LogAnalyzerError(Exception):
    """Base class for all errors raised by the log analyzer."""


class LogParseError(LogAnalyzerError):
    """A log line does not match any supported log format."""

    def __init__(self, line_number: int, reason: str) -> None:
        """Store where the line is and what is wrong with it.

        Args:
            line_number: Line of the entry in the log file.
            reason: Short description of the problem.
        """
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"Line {line_number}: {reason}")


class LogFileError(LogAnalyzerError):
    """A log file cannot be used."""


class LogFileNotFoundError(LogFileError):
    """The log file does not exist."""


class LogFilePermissionError(LogFileError):
    """The log file exists but cannot be opened (no permission)."""
