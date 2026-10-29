"""Connection settings, read from the environment (and a ``.env`` file)."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

from ecommerce_pipeline.exceptions import ConfigError


@dataclass(frozen=True)
class Settings:
    """Everything needed to reach PostgreSQL, Redis and MongoDB."""

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    redis_url: str
    mongo_uri: str
    mongo_db: str


def _require(env: Mapping[str, str], name: str) -> str:
    """Return ``env[name]``, or raise ``ConfigError`` if it is missing or empty."""
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"Missing setting {name} (see .env.example)")
    return value


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build ``Settings`` from ``env``, or from ``.env`` and the environment.

    Raises:
        ConfigError: If a setting is missing or the port is not a number.
    """
    if env is None:
        load_dotenv()
        env = os.environ
    port = _require(env, "POSTGRES_PORT")
    if not port.isdigit():
        raise ConfigError(f"POSTGRES_PORT must be a number, got {port!r}")
    return Settings(
        postgres_host=_require(env, "POSTGRES_HOST"),
        postgres_port=int(port),
        postgres_db=_require(env, "POSTGRES_DB"),
        postgres_user=_require(env, "POSTGRES_USER"),
        postgres_password=_require(env, "POSTGRES_PASSWORD"),
        redis_url=_require(env, "REDIS_URL"),
        mongo_uri=_require(env, "MONGO_URI"),
        mongo_db=_require(env, "MONGO_DB"),
    )
