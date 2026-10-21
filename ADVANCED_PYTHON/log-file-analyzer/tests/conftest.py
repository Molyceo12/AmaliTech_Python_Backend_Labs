"""Shared pytest fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.helpers import DATA

WriteLog = Callable[..., Path]


@pytest.fixture(name="access_lines")
def fixture_access_lines() -> list[str]:
    """Return every line of the large sample log ``data/access.log``."""
    return (DATA / "access.log").read_text(encoding="utf-8").splitlines()


@pytest.fixture(name="write_log")
def fixture_write_log(tmp_path: Path) -> WriteLog:
    """Return a function that writes lines to a temp log file and gives its path."""

    def write(lines: list[str], name: str = "access.log") -> Path:
        path = tmp_path / name
        path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        return path

    return write
