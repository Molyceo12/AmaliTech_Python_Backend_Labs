"""What the user asked to analyze (filled from the command line)."""

from dataclasses import dataclass
from datetime import datetime
from functools import partial

from log_analyzer.pipeline import Predicate, by_method, by_status, only_errors


@dataclass(frozen=True)
class AnalyzerOptions:
    """Filters and report settings for one run.

    Attributes:
        statuses: Keep only these status codes (empty = all).
        errors_only: Keep only 4xx/5xx responses.
        method: Keep only this HTTP method (``None`` = all).
        start: Keep entries from this time on (``None`` = from the start).
        end: Keep entries before this time (``None`` = to the end).
        top: How many IPs and URLs the "top" lists keep.
        page: Which page of entries the report lists (from 1).
        per_page: How many entries one page holds.
    """

    statuses: tuple[int, ...] = ()
    errors_only: bool = False
    method: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    top: int = 5
    page: int = 1
    per_page: int = 20

    def predicates(self) -> list[Predicate]:
        """Return the ``partial`` filters these options ask for."""
        checks: list[Predicate] = []
        if self.statuses:
            checks.append(partial(by_status, frozenset(self.statuses)))
        if self.errors_only:
            checks.append(only_errors)
        if self.method:
            checks.append(partial(by_method, self.method.upper()))
        return checks

    def describe(self) -> dict[str, str]:
        """Return the active filters as text, for the report."""
        shown: dict[str, str] = {}
        if self.statuses:
            shown["statuses"] = ", ".join(map(str, self.statuses))
        if self.errors_only:
            shown["errors_only"] = "yes"
        if self.method:
            shown["method"] = self.method.upper()
        if self.start:
            shown["from"] = self.start.isoformat()
        if self.end:
            shown["to"] = self.end.isoformat()
        return shown
