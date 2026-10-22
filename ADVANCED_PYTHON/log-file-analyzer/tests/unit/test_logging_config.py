"""Tests for where the tool's own log messages go."""

import logging
from pathlib import Path

import pytest

from log_analyzer.logging_config import (
    PACKAGE_LOGGER,
    SHOWN_TO_USER,
    LogSetupError,
    configure_logging,
)

LOGGER = logging.getLogger(f"{PACKAGE_LOGGER}.tests")


def log_every_level() -> None:
    """Write one message per level."""
    LOGGER.debug("debug message")
    LOGGER.info("info message")
    LOGGER.warning("warning message")
    LOGGER.error("error message")


def test_file_gets_every_level_with_a_timestamp(tmp_path: Path) -> None:
    """DEBUG and up go to the file, with time, level and logger name."""
    log_file = configure_logging(tmp_path / "logs" / "run.log")
    log_every_level()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4
    assert lines[0].endswith("DEBUG    log_analyzer.tests: debug message")
    assert " ERROR " in lines[3]
    assert lines[0][:4].isdigit()  # starts with the date


def test_terminal_shows_only_warnings_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Without ``verbose`` the terminal stays clean: WARNING and up only."""
    configure_logging(tmp_path / "run.log")
    log_every_level()
    err = capsys.readouterr().err
    assert "warning message" in err
    assert "error message" in err
    assert "info message" not in err
    assert "debug message" not in err


def test_verbose_shows_everything_in_the_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``verbose`` lowers the terminal level to DEBUG."""
    configure_logging(tmp_path / "run.log", verbose=True)
    log_every_level()
    assert "debug message" in capsys.readouterr().err


def test_messages_shown_to_the_user_are_not_repeated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A record marked as already shown goes to the file only."""
    log_file = configure_logging(tmp_path / "run.log")
    LOGGER.error("printed by the CLI", extra={SHOWN_TO_USER: True})
    assert "printed by the CLI" not in capsys.readouterr().err
    assert "printed by the CLI" in log_file.read_text(encoding="utf-8")


def test_calling_again_does_not_log_twice(tmp_path: Path) -> None:
    """Old handlers are replaced, and the file is appended to."""
    first = configure_logging(tmp_path / "run.log")
    LOGGER.info("first run")
    configure_logging(first)
    LOGGER.info("second run")
    lines = first.read_text(encoding="utf-8").splitlines()
    assert [line.rsplit(": ", 1)[1] for line in lines] == ["first run", "second run"]


def test_unwritable_log_file_raises(tmp_path: Path) -> None:
    """A path whose folder cannot be created gives ``LogSetupError``."""
    blocker = tmp_path / "taken"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises(LogSetupError, match="Cannot write log file"):
        configure_logging(blocker / "run.log")


def test_other_handlers_are_left_alone(tmp_path: Path) -> None:
    """Only the handlers this module added are replaced."""
    package = logging.getLogger(PACKAGE_LOGGER)
    foreign = logging.NullHandler()
    package.addHandler(foreign)
    try:
        configure_logging(tmp_path / "run.log")
        configure_logging(tmp_path / "run.log")
        assert foreign in package.handlers
    finally:
        package.removeHandler(foreign)
