"""Tests for the generator-based log reader."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from log_analyzer.exceptions import (
    LogFileError,
    LogFileNotFoundError,
    LogFilePermissionError,
)
from log_analyzer.readers import read_lines, read_many
from tests.conftest import WriteLog


def test_read_lines_yields_each_line_without_line_break(write_log: WriteLog) -> None:
    """Lines come back one by one, without ``\\n``."""
    path = write_log(["first", "second"])
    assert list(read_lines(path)) == ["first", "second"]


def test_read_lines_removes_windows_line_endings(tmp_path: Path) -> None:
    """``\\r\\n`` endings are removed too."""
    path = tmp_path / "crlf.log"
    path.write_bytes(b"a\r\nb\r\n")
    assert list(read_lines(path)) == ["a", "b"]


def test_read_lines_is_lazy(write_log: WriteLog) -> None:
    """The generator gives one line per ``next()``."""
    lines = read_lines(write_log(["one", "two", "three"]))
    assert next(lines) == "one"
    assert next(lines) == "two"


def test_missing_file_fails_on_first_next() -> None:
    """Creating the generator does nothing; reading it raises the error."""
    lines = read_lines("missing.log")
    with pytest.raises(LogFileNotFoundError, match="Log file not found"):
        next(lines)


def test_no_permission_raises_permission_error(
    write_log: WriteLog, mocker: MockerFixture
) -> None:
    """A ``PermissionError`` becomes ``LogFilePermissionError``."""
    path = write_log(["x"])
    mocker.patch.object(Path, "open", side_effect=PermissionError("denied"))
    with pytest.raises(LogFilePermissionError, match="No permission"):
        next(read_lines(path))


def test_other_os_errors_become_log_file_error(
    write_log: WriteLog, mocker: MockerFixture
) -> None:
    """Any other ``OSError`` becomes ``LogFileError``."""
    path = write_log(["x"])
    mocker.patch.object(Path, "open", side_effect=OSError("disk failure"))
    with pytest.raises(LogFileError, match="Cannot open log file"):
        next(read_lines(path))


def test_folder_is_not_a_log_file(tmp_path: Path) -> None:
    """Reading a folder raises a ``LogFileError`` (its exact kind depends on the OS)."""
    with pytest.raises(LogFileError):
        next(read_lines(tmp_path))


def test_undecodable_bytes_are_replaced(tmp_path: Path) -> None:
    """Bad bytes do not stop the run."""
    path = tmp_path / "bad.log"
    path.write_bytes(b"ok\n\xff\xfe bad\n")
    assert list(read_lines(path))[1].endswith(" bad")


def test_read_many_chains_files_in_order(write_log: WriteLog) -> None:
    """Lines of the first file come before the lines of the second."""
    first = write_log(["a1", "a2"], "a.log")
    second = write_log(["b1"], "b.log")
    assert list(read_many([first, second])) == ["a1", "a2", "b1"]


def test_read_many_opens_the_next_file_only_when_needed(write_log: WriteLog) -> None:
    """A missing second file is not touched until its lines are needed."""
    lines = read_many([write_log(["a1"]), "missing.log"])
    assert next(lines) == "a1"
    with pytest.raises(LogFileNotFoundError):
        next(lines)
