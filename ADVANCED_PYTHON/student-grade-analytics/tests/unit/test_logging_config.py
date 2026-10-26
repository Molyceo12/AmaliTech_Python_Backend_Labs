"""Logging setup: file creation, levels, no duplicates, fallback."""

import logging
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from grade_analytics.logging_config import PACKAGE_LOGGER, setup_logging

logger = logging.getLogger(f"{PACKAGE_LOGGER}.tests")


def test_creates_folder_and_file(tmp_path: Path) -> None:
    """The log folder is created and records are written to the file."""
    log_file = tmp_path / "logs" / "app.log"
    assert setup_logging(log_file) == log_file
    logger.info("hello")
    text = log_file.read_text(encoding="utf-8")
    assert "| INFO     | grade_analytics.tests | hello" in text


def test_level_filters_records(tmp_path: Path) -> None:
    """Records below the chosen level are not written."""
    log_file = tmp_path / "app.log"
    setup_logging(log_file, "WARNING")
    logger.info("hidden")
    logger.warning("shown")
    text = log_file.read_text(encoding="utf-8")
    assert "hidden" not in text
    assert "shown" in text


def test_second_call_replaces_the_handler(tmp_path: Path) -> None:
    """Calling it twice keeps one file handler, so no line is written twice."""
    log_file = tmp_path / "app.log"
    setup_logging(log_file)
    setup_logging(log_file)
    handlers = logging.getLogger(PACKAGE_LOGGER).handlers
    assert sum(not isinstance(h, logging.NullHandler) for h in handlers) == 1
    logger.info("once")
    assert log_file.read_text(encoding="utf-8").count("once") == 1


def test_unwritable_log_file_only_warns(
    tmp_path: Path, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """If the file cannot be opened, a warning is printed and nothing fails."""
    mocker.patch(
        "grade_analytics.logging_config.RotatingFileHandler",
        side_effect=PermissionError("denied"),
    )
    assert setup_logging(tmp_path / "app.log") is None
    assert "Warning: cannot write log file" in capsys.readouterr().err
