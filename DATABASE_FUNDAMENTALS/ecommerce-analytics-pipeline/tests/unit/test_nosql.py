"""Tests for the Redis and MongoDB clients."""

from unittest.mock import MagicMock

import pytest
import redis
from pymongo.errors import ServerSelectionTimeoutError
from pytest_mock import MockerFixture

from ecommerce_pipeline.db.nosql import create_mongo, create_redis
from ecommerce_pipeline.exceptions import DatabaseConnectionError

SETTINGS = MagicMock(
    redis_url="redis://localhost:6379/0",
    mongo_uri="mongodb://localhost:27017",
    mongo_db="ecommerce",
)


def test_create_redis_pings_and_returns_the_client(mocker: MockerFixture) -> None:
    """The client is built from ``REDIS_URL`` and checked with ``ping``."""
    client = MagicMock()
    from_url = mocker.patch(
        "ecommerce_pipeline.db.nosql.redis.Redis.from_url", return_value=client
    )
    assert create_redis(SETTINGS) is client
    from_url.assert_called_once_with("redis://localhost:6379/0", decode_responses=True)
    client.ping.assert_called_once()


def test_create_redis_raises_when_redis_is_down(mocker: MockerFixture) -> None:
    """A failed ping becomes ``DatabaseConnectionError``."""
    from_url = mocker.patch("ecommerce_pipeline.db.nosql.redis.Redis.from_url")
    from_url.return_value.ping.side_effect = redis.ConnectionError("refused")
    with pytest.raises(DatabaseConnectionError, match="Redis"):
        create_redis(SETTINGS)


def test_create_mongo_pings_and_returns_the_database(mocker: MockerFixture) -> None:
    """The client pings MongoDB and the ``MONGO_DB`` database is returned."""
    client = MagicMock()
    mocker.patch("ecommerce_pipeline.db.nosql.MongoClient", return_value=client)
    assert create_mongo(SETTINGS) is client.__getitem__.return_value
    client.admin.command.assert_called_once_with("ping")
    client.__getitem__.assert_called_once_with("ecommerce")


def test_create_mongo_raises_and_closes_when_mongo_is_down(
    mocker: MockerFixture,
) -> None:
    """A failed ping closes the client and becomes ``DatabaseConnectionError``."""
    client = MagicMock()
    client.admin.command.side_effect = ServerSelectionTimeoutError("refused")
    mocker.patch("ecommerce_pipeline.db.nosql.MongoClient", return_value=client)
    with pytest.raises(DatabaseConnectionError, match="MongoDB"):
        create_mongo(SETTINGS)
    client.close.assert_called_once()
