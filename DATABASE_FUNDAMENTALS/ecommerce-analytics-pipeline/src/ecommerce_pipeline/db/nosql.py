"""Clients for the NoSQL stores: Redis (cache) and MongoDB (sessions)."""

import logging

import redis

from ecommerce_pipeline.config import Settings
from ecommerce_pipeline.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


def create_redis(settings: Settings) -> redis.Redis:
    """Connect to Redis and check it answers.

    Raises:
        DatabaseConnectionError: If Redis cannot be reached.
    """
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        client.ping()
    except redis.RedisError as error:
        raise DatabaseConnectionError(f"Cannot connect to Redis: {error}") from error
    logger.info("Connected to Redis")
    return client
