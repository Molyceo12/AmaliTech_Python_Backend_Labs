"""Tests for the CSV record reader."""

import inspect
from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from grade_analytics.exceptions import (
    DataFileFormatError,
    DataFileNotFoundError,
    DataFilePermissionError,
)
from grade_analytics.readers import CsvRecordReader, RawRecord, RecordReader
from tests.helpers import HEADER, ROW_DATA

ALICE_ROW = "S001,Alice,Computer Science,1,CS101,2026-S1,92\n"


def test_reader_implements_interface() -> None:
    """CsvRecordReader is a RecordReader."""
    assert isinstance(CsvRecordReader(), RecordReader)


def test_reads_rows_with_line_numbers(write_csv: Callable[..., Path]) -> None:
    """Each data row becomes a RawRecord with its line number."""
    path = write_csv(HEADER + ALICE_ROW + "S002,Brian,Maths,2,MA101,2026-S1,70\n")
    records = list(CsvRecordReader().read(path))
    assert records[0] == RawRecord(2, ROW_DATA)
    assert [r.line_number for r in records] == [2, 3]


def test_read_is_a_generator(write_csv: Callable[..., Path]) -> None:
    """Rows are yielded one at a time instead of being loaded into a list."""
    assert inspect.isgenerator(CsvRecordReader().read(write_csv(HEADER)))


@pytest.mark.parametrize(
    "content",
    [
        " Score ,SEMESTER,course_code,year,major,name,Student_ID\n"
        "92,2026-S1,CS101,1,Computer Science,Alice,S001\n",
        "﻿" + HEADER + ALICE_ROW,
        HEADER + " S001 , Alice , Computer Science , 1 , CS101 , 2026-S1 , 92 \n",
    ],
    ids=["any-order-and-case", "excel-bom", "spaces-trimmed"],
)
def test_reads_flexible_files(write_csv: Callable[..., Path], content: str) -> None:
    """Header order, letter case, a BOM and extra spaces do not matter."""
    records = list(CsvRecordReader().read(write_csv(content)))
    assert records[0].data == ROW_DATA


def test_skips_blank_lines(write_csv: Callable[..., Path]) -> None:
    """Empty lines and lines with only commas are ignored."""
    path = write_csv(HEADER + "\n,,,,,,\n" + ALICE_ROW)
    assert [r.line_number for r in CsvRecordReader().read(path)] == [4]


def test_short_row_gets_empty_values(write_csv: Callable[..., Path]) -> None:
    """Missing trailing values become empty strings (the builder rejects them)."""
    records = list(CsvRecordReader().read(write_csv(HEADER + "S001,Alice\n")))
    assert records[0].data["score"] == ""


def test_missing_file(tmp_path: Path) -> None:
    """A path that does not exist raises DataFileNotFoundError."""
    with pytest.raises(DataFileNotFoundError, match="not found"):
        list(CsvRecordReader().read(tmp_path / "missing.csv"))


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("", "empty"),
        ("student_id,name,major,year,course_code,semester\n", "headers: score"),
    ],
    ids=["empty-file", "missing-header"],
)
def test_bad_file_format(
    write_csv: Callable[..., Path], content: str, message: str
) -> None:
    """Empty files and missing headers raise DataFileFormatError."""
    with pytest.raises(DataFileFormatError, match=message):
        list(CsvRecordReader().read(write_csv(content)))


def test_file_that_is_not_utf8(tmp_path: Path) -> None:
    """Bytes that are not valid UTF-8 raise DataFileFormatError."""
    path = tmp_path / "latin1.csv"
    path.write_bytes(HEADER.encode() + "S001,Zoë,CS,1,CS101,S1,90\n".encode("latin-1"))
    with pytest.raises(DataFileFormatError, match="Cannot read"):
        list(CsvRecordReader().read(path))


def test_permission_error(
    write_csv: Callable[..., Path], mocker: MockerFixture
) -> None:
    """No permission to open the file raises DataFilePermissionError."""
    path = write_csv(HEADER)
    mocker.patch.object(Path, "open", side_effect=PermissionError("denied"))
    with pytest.raises(DataFilePermissionError, match="No permission"):
        list(CsvRecordReader().read(path))


def test_other_open_error_is_a_format_error(
    write_csv: Callable[..., Path], mocker: MockerFixture
) -> None:
    """Any other OS error while opening raises DataFileFormatError."""
    path = write_csv(HEADER)
    mocker.patch.object(Path, "open", side_effect=OSError("device busy"))
    with pytest.raises(DataFileFormatError, match="device busy"):
        list(CsvRecordReader().read(path))
