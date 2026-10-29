"""Tests for reading the connection settings."""

import pytest
from pytest_mock import MockerFixture

from ecommerce_pipeline.config import load_settings
from ecommerce_pipeline.exceptions import ConfigError

ENV = {
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "ecommerce",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "secret",
    "REDIS_URL": "redis://localhost:6379/0",
    "MONGO_URI": "mongodb://localhost:27017",
    "MONGO_DB": "ecommerce",
}


def test_reads_every_setting() -> None:
    """Each variable lands in its field, and the port becomes an int."""
    settings = load_settings(ENV)
    assert settings.postgres_port == 5432
    assert settings.postgres_user == "user"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.mongo_db == "ecommerce"


@pytest.mark.parametrize("name", ["POSTGRES_HOST", "REDIS_URL", "MONGO_URI"])
def test_missing_or_empty_setting_raises(name: str) -> None:
    """A missing or blank variable gives ``ConfigError`` naming it."""
    with pytest.raises(ConfigError, match=name):
        load_settings({**ENV, name: " "})
    with pytest.raises(ConfigError, match=name):
        load_settings({k: v for k, v in ENV.items() if k != name})


def test_port_must_be_a_number() -> None:
    """A non-numeric port gives ``ConfigError``."""
    with pytest.raises(ConfigError, match="POSTGRES_PORT"):
        load_settings({**ENV, "POSTGRES_PORT": "abc"})


def test_reads_the_environment_by_default(mocker: MockerFixture) -> None:
    """Without ``env`` it loads ``.env`` and reads ``os.environ``."""
    load_dotenv = mocker.patch("ecommerce_pipeline.config.load_dotenv")
    mocker.patch.dict("os.environ", ENV, clear=True)
    assert load_settings().postgres_host == "localhost"
    load_dotenv.assert_called_once()
