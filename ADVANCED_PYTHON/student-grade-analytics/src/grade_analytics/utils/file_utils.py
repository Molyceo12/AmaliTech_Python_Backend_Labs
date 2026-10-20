"""File helpers shared across the tool."""

import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO


@contextmanager
def atomic_write(path: Path) -> Iterator[TextIO]:
    """Write to a temp file that replaces ``path`` only if writing succeeds.

    A failed write never leaves a half-written file: the old file (if any)
    stays as it was and the temp file is removed.

    Args:
        path: Final file to write.

    Yields:
        An open text file to write into.

    Raises:
        OSError: If the folder or the file cannot be written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as handle:
            yield handle
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)  # already gone after a successful replace
