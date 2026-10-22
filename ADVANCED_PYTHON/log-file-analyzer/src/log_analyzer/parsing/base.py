"""Parser interface: how one log line becomes a ``LogEntry``."""

from abc import ABC, abstractmethod

from log_analyzer.models import LogEntry


class LogParser(ABC):
    """What any log parser must do; the service depends only on this.

    Other log layouts (a custom Nginx format, JSON lines) can be added by
    subclassing, without changing the service.
    """

    @abstractmethod
    def parse(self, line: str) -> LogEntry | None:
        """Turn one raw line into an entry, or ``None`` if it is not valid."""
