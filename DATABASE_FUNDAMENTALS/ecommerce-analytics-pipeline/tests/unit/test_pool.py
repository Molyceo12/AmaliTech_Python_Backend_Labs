"""Tests for the PostgreSQL pool and per-connection transactions."""

from unittest.mock import MagicMock

import psycopg2
import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline.config import Settings
from ecommerce_pipeline.db.pool import create_pool, get_connection
from ecommerce_pipeline.exceptions import DatabaseConnectionError

SETTINGS = Settings(
    postgres_host="localhost",
    postgres_port=5432,
    postgres_db="ecommerce",
    postgres_user="user",
    postgres_password="secret",
    redis_url="redis://localhost:6379/0",
    mongo_uri="mongodb://localhost:27017",
    mongo_db="ecommerce",
)


def test_create_pool_uses_the_settings(mocker: MockerFixture) -> None:
    """The pool connects with the host, port, database and user from settings."""
    pool_class = mocker.patch("ecommerce_pipeline.db.pool.ThreadedConnectionPool")
    assert create_pool(SETTINGS) is pool_class.return_value
    kwargs = pool_class.call_args.kwargs
    assert kwargs["host"] == "localhost"
    assert kwargs["port"] == 5432
    assert kwargs["dbname"] == "ecommerce"
    assert kwargs["user"] == "user"


def test_create_pool_raises_when_postgres_is_down(mocker: MockerFixture) -> None:
    """A driver connection error becomes ``DatabaseConnectionError``."""
    mocker.patch(
        "ecommerce_pipeline.db.pool.ThreadedConnectionPool",
        side_effect=psycopg2.OperationalError("refused"),
    )
    with pytest.raises(DatabaseConnectionError, match="localhost:5432"):
        create_pool(SETTINGS)


def test_get_connection_commits_on_success() -> None:
    """A block that finishes commits and returns the connection."""
    pool = MagicMock()
    with get_connection(pool) as conn:
        assert conn is pool.getconn.return_value
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()
    pool.putconn.assert_called_once_with(conn)


def test_get_connection_rolls_back_on_error() -> None:
    """A block that raises rolls back, re-raises and returns the connection."""
    pool = MagicMock()
    conn = pool.getconn.return_value
    with pytest.raises(ValueError), get_connection(pool):
        raise ValueError("boom")
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
    pool.putconn.assert_called_once_with(conn)
