"""Tests for the ``ecommerce`` command line."""

from decimal import Decimal

import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline import cli
from ecommerce_pipeline.analytics.reports import CustomerRevenue, ProductRank
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


def test_seed_loads_sample_data_and_closes_the_pool(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """``seed`` loads the sample data, closes the pool and exits with 0."""
    mocker.patch("ecommerce_pipeline.cli.load_settings")
    pool = mocker.patch("ecommerce_pipeline.cli.create_pool").return_value
    load_sample_data = mocker.patch("ecommerce_pipeline.cli.load_sample_data")
    assert cli.main(["seed"]) == 0
    load_sample_data.assert_called_once_with(pool)
    pool.closeall.assert_called_once()
    assert "Sample data loaded." in capsys.readouterr().out


def test_demo_opens_and_closes_every_connection(mocker: MockerFixture) -> None:
    """``demo`` runs with all three stores and closes each one."""
    mocker.patch("ecommerce_pipeline.cli.load_settings")
    pool = mocker.patch("ecommerce_pipeline.cli.create_pool").return_value
    cache = mocker.patch("ecommerce_pipeline.cli.create_redis").return_value
    mongo = mocker.patch("ecommerce_pipeline.cli.create_mongo").return_value
    run_demo = mocker.patch("ecommerce_pipeline.cli.run_demo")
    assert cli.main(["demo"]) == 0
    run_demo.assert_called_once_with(pool, cache, mongo)
    pool.closeall.assert_called_once()
    cache.close.assert_called_once()
    mongo.client.close.assert_called_once()


def test_report_prints_both_tables(
    mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """``report`` prints the ranking and the revenue table, then closes the pool."""
    mocker.patch("ecommerce_pipeline.cli.load_settings")
    pool = mocker.patch("ecommerce_pipeline.cli.create_pool").return_value
    mocker.patch(
        "ecommerce_pipeline.cli.product_ranking",
        return_value=[ProductRank(1, 4, "Shirt", 12, Decimal("180.00"))],
    )
    mocker.patch(
        "ecommerce_pipeline.cli.revenue_per_customer",
        return_value=[CustomerRevenue(2, "Kofi", 3, Decimal("276.00"))],
    )
    assert cli.main(["report"]) == 0
    out = capsys.readouterr().out
    assert "Shirt" in out
    assert "Kofi" in out
    pool.closeall.assert_called_once()
