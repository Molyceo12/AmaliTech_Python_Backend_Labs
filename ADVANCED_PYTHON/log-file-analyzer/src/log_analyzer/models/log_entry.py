"""One parsed line of a web server access log."""

from dataclasses import dataclass
from datetime import datetime

ERROR_STATUS = 400  # 4xx and 5xx responses are errors


@dataclass(frozen=True, slots=True)
class LogEntry:
    """A single request taken from an access log line.

    Attributes:
        ip: Client IPv4 address, e.g. ``"192.168.1.10"``.
        timestamp: When the request was made (timezone aware).
        method: HTTP method, e.g. ``"GET"``.
        url: Requested path, including any query string.
        protocol: HTTP version, e.g. ``"HTTP/1.1"``.
        status: HTTP status code, e.g. ``200``.
        size: Response size in bytes, or ``None`` when the log shows ``-``.
        referrer: Referring page (combined format only).
        user_agent: Client software (combined format only).
    """

    ip: str
    timestamp: datetime
    method: str
    url: str
    protocol: str
    status: int
    size: int | None = None
    referrer: str | None = None
    user_agent: str | None = None

    @property
    def is_error(self) -> bool:
        """Whether the response was a client or server error (4xx/5xx)."""
        return self.status >= ERROR_STATUS

    @property
    def hour(self) -> int:
        """Hour of the day (0–23) the request was made."""
        return self.timestamp.hour
