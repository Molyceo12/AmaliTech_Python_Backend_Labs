"""CSV reader: reads rows only; turning them into students is a separate step."""

import csv
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO, Union

from grade_analytics.exceptions import (
    DataFileFormatError,
    DataFileNotFoundError,
    DataFilePermissionError,
)
from grade_analytics.readers.base import RawRecord, RecordReader

REQUIRED_HEADERS = (
    "student_id",
    "name",
    "major",
    "year",
    "course_code",
    "semester",
    "score",
)

logger = logging.getLogger(__name__)


@contextmanager
def open_data_file(path: Path) -> Iterator[TextIO]:
    """Open a data file for reading and always close it afterwards.

    ``utf-8-sig`` removes the BOM Excel adds; ``newline=""`` lets the csv
    module handle line endings.

    Args:
        path: File to open.

    Yields:
        The open text file.

    Raises:
        DataFileNotFoundError: If the file does not exist.
        DataFilePermissionError: If there is no permission to read it.
        DataFileFormatError: If it cannot be opened for another reason.
    """
    try:
        handle = path.open(encoding="utf-8-sig", newline="")
    except FileNotFoundError as error:
        raise DataFileNotFoundError(f"Data file not found: {path}") from error
    except PermissionError as error:
        raise DataFilePermissionError(
            f"No permission to read data file: {path}"
        ) from error
    except OSError as error:
        raise DataFileFormatError(f"Cannot open data file {path}: {error}") from error
    with handle:
        yield handle


class CsvRecordReader(RecordReader):
    """Reads grade rows from a CSV file with ``csv.DictReader``."""

    def read(self, path: Union[str, Path]) -> Iterator[RawRecord]:
        """Yield every non-empty data row, one at a time (low memory).

        Header names are trimmed and lowercased, so any order and letter
        case works.

        Args:
            path: CSV file to read.

        Yields:
            One ``RawRecord`` per data row.

        Raises:
            DataFileNotFoundError: If the file does not exist.
            DataFilePermissionError: If there is no permission to read it.
            DataFileFormatError: If the file is empty, not valid text or
                misses required headers.
        """
        csv_path = Path(path)
        logger.debug("Opening %s", csv_path)
        with open_data_file(csv_path) as handle:
            try:
                reader = csv.DictReader(handle)
                if reader.fieldnames is None:
                    raise DataFileFormatError(f"Data file is empty: {csv_path}")
                reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
                logger.debug("Headers: %s", ", ".join(reader.fieldnames))
                missing = [h for h in REQUIRED_HEADERS if h not in reader.fieldnames]
                if missing:
                    raise DataFileFormatError(
                        f"Data file is missing required headers: {', '.join(missing)}"
                    )
                for row in reader:
                    data = {
                        key: (value or "").strip()
                        for key, value in row.items()
                        if isinstance(key, str)
                    }
                    if any(data.values()):  # skip lines with only commas
                        yield RawRecord(reader.line_num, data)
            except (csv.Error, UnicodeDecodeError) as error:
                raise DataFileFormatError(
                    f"Cannot read data file {csv_path}: {error}"
                ) from error
