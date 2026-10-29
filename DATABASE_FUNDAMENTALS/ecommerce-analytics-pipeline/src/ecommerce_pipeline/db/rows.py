"""Small helpers for reading query results."""

from typing import Any

from psycopg2.extensions import cursor


def fetch_value(cur: cursor) -> Any:
    """Return the first column of the next row (e.g. an id from ``RETURNING``)."""
    row = cur.fetchone()
    if row is None:
        raise LookupError("The query returned no row")
    return row[0]
