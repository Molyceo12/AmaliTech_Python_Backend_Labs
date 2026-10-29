"""Customer CRUD."""

import logging

from psycopg2 import errorcodes, errors
from psycopg2.pool import ThreadedConnectionPool

from ecommerce_pipeline.db.pool import get_connection
from ecommerce_pipeline.db.rows import fetch_value
from ecommerce_pipeline.exceptions import DuplicateEmailError

logger = logging.getLogger(__name__)

UniqueViolation = errors.lookup(errorcodes.UNIQUE_VIOLATION)

INSERT_CUSTOMER = """
    INSERT INTO customers (name, email)
    VALUES (%s, %s)
    RETURNING customer_id
"""


def add_customer(pool: ThreadedConnectionPool, name: str, email: str) -> int:
    """Insert a customer and return the new ``customer_id``.

    Raises:
        DuplicateEmailError: If a customer already uses this email.
    """
    try:
        with get_connection(pool) as conn, conn.cursor() as cursor:
            cursor.execute(INSERT_CUSTOMER, (name, email))
            customer_id: int = fetch_value(cursor)
    except UniqueViolation as error:
        raise DuplicateEmailError(f"Email already in use: {email}") from error
    logger.info("Added customer %d", customer_id)
    return customer_id
