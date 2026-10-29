"""Tests for the ``ecommerce`` command line."""

import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline import cli
from ecommerce_pipeline.exceptions import DatabaseConnectionError


@pytest.fixture(autouse=True)
def no_log_file(mocker: MockerFixture) -> None:
    """Keep the tests from writing ``output/ecommerce.log``."""
    mocker.patch("ecommerce_pipeline.cli.configure_logging")


def test_setup_creates_tables_and_closes_the_pool(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """``setup`` creates the tables, closes the pool and exits with 0."""
    mocker.patch("ecommerce_pipeline.cli.load_settings")
    pool = mocker.patch("ecommerce_pipeline.cli.create_pool").return_value
    create_tables = mocker.patch("ecommerce_pipeline.cli.create_tables")
    assert cli.main(["setup"]) == 0
    create_tables.assert_called_once_with(pool)
    pool.closeall.assert_called_once()
    assert "Tables created." in capsys.readouterr().out


def test_expected_error_prints_a_message_and_exits_with_1(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """An ``EcommerceError`` is shown as one line, not a traceback."""
    mocker.patch("ecommerce_pipeline.cli.load_settings")
    mocker.patch(
        "ecommerce_pipeline.cli.create_pool",
        side_effect=DatabaseConnectionError("Cannot connect to PostgreSQL"),
    )
    assert cli.main(["setup"]) == 1
    assert "Error: Cannot connect to PostgreSQL" in capsys.readouterr().err


def test_unknown_command_exits_with_usage_error() -> None:
    """argparse rejects a command that does not exist."""
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["nope"])
    assert exit_info.value.code == 2
