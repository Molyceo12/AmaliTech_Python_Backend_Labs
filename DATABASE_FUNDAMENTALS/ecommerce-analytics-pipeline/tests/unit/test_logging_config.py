"""Tests for where the pipeline's log messages go."""

import logging
from pathlib import Path

import pytest

from ecommerce_pipeline.exceptions import LogSetupError
from ecommerce_pipeline.logging_config import PACKAGE_LOGGER, configure_logging

LOGGER = logging.getLogger(f"{PACKAGE_LOGGER}.tests")


def test_file_gets_every_level_with_a_timestamp(tmp_path: Path) -> None:
    """DEBUG and up go to the file, with time, level and logger name."""
    log_file = configure_logging(tmp_path / "logs" / "run.log")
    LOGGER.debug("debug message")
    LOGGER.error("error message")
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("DEBUG    ecommerce_pipeline.tests: debug message")
    assert " ERROR " in lines[1]
    assert lines[0][:4].isdigit()


def test_terminal_shows_only_warnings_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Without ``verbose`` the terminal shows WARNING and up only."""
    configure_logging(tmp_path / "run.log")
    LOGGER.info("info message")
    LOGGER.warning("warning message")
    err = capsys.readouterr().err
    assert "warning message" in err
    assert "info message" not in err


def test_verbose_shows_everything_in_the_terminal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``verbose`` lowers the terminal level to DEBUG."""
    configure_logging(tmp_path / "run.log", verbose=True)
    LOGGER.debug("debug message")
    assert "debug message" in capsys.readouterr().err


def test_calling_again_does_not_log_twice(tmp_path: Path) -> None:
    """Old handlers are replaced, and the file is appended to."""
    log_file = configure_logging(tmp_path / "run.log")
    LOGGER.info("first run")
    configure_logging(log_file)
    LOGGER.info("second run")
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert [line.rsplit(": ", 1)[1] for line in lines] == ["first run", "second run"]


def test_unwritable_log_file_raises(tmp_path: Path) -> None:
    """A path whose folder cannot be created gives ``LogSetupError``."""
    blocker = tmp_path / "taken"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises(LogSetupError, match="Cannot write log file"):
        configure_logging(blocker / "run.log")
