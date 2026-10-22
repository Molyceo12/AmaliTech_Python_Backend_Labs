"""Reader interface: where the log lines come from."""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from pathlib import Path


class LogReader(ABC):
    """What any log reader must do; the service depends only on this.

    Other readers (gzip files, a whole folder, standard input) can be added
    by subclassing, without changing the service.
    """

    @abstractmethod
    def read(self, paths: Iterable[str | Path]) -> Iterator[str]:
        """Yield the lines of every source, one at a time, in order.

        Raises:
            LogFileError: If a source cannot be read.
        """
