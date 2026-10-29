"""Clients for the NoSQL stores: Redis (cache) and MongoDB (sessions)."""

import logging
from typing import Any

import redis
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from ecommerce_pipeline.config import Settings
from ecommerce_pipeline.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)

# Fail fast instead of waiting 30 seconds when MongoDB is down.
MONGO_TIMEOUT_MS = 3000


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


def create_mongo(settings: Settings) -> Database[dict[str, Any]]:
    """Connect to MongoDB and return the ``MONGO_DB`` database.

    Raises:
        DatabaseConnectionError: If MongoDB cannot be reached.
    """
    client: MongoClient[dict[str, Any]] = MongoClient(
        settings.mongo_uri, serverSelectionTimeoutMS=MONGO_TIMEOUT_MS
    )
    try:
        client.admin.command("ping")
    except PyMongoError as error:
        client.close()
        raise DatabaseConnectionError(f"Cannot connect to MongoDB: {error}") from error
    logger.info("Connected to MongoDB")
    return client[settings.mongo_db]
