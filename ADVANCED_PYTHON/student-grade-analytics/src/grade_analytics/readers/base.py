"""Reader interface and the raw record it produces."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Dict, NamedTuple, Union


class RawRecord(NamedTuple):
    """One row from a data file, not checked yet.

    Attributes:
        line_number: Line of the row in the file (for error messages).
        data: Column name → trimmed value.
    """

    line_number: int
    data: Dict[str, str]


class RecordReader(ABC):
    """What any data-file reader must do; the service depends only on this."""

    @abstractmethod
    def read(self, path: Union[str, Path]) -> Iterator[RawRecord]:
        """Yield the data rows of a file, one at a time.

        Args:
            path: Data file to read.

        Raises:
            DataFileNotFoundError: If the file does not exist.
            DataFilePermissionError: If the file cannot be opened.
            DataFileFormatError: If the file is empty, unreadable or misses headers.
        """
