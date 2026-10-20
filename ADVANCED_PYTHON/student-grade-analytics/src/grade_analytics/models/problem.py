"""A data-file row that was skipped."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RowProblem:
    """A row that could not be used, and why.

    Attributes:
        line_number: Line of the row in the data file.
        reason: What is wrong with the row.
    """

    line_number: int
    reason: str
