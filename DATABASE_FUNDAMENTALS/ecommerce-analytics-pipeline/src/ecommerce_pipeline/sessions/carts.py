"""Shopping carts: one MongoDB document per user session.

Document shape::

    {"_id": "<session id>", "customer_id": 1, "cart": {"4": 2}, "updated_at": ...}

Cart keys are product ids as strings, because MongoDB keys must be strings.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pymongo.database import Database

from ecommerce_pipeline.exceptions import SessionNotFoundError

logger = logging.getLogger(__name__)

SESSIONS = "sessions"


def create_session(db: Database[dict[str, Any]], customer_id: int) -> str:
    """Start a session with an empty cart and return its id."""
    session_id = uuid4().hex
    db[SESSIONS].insert_one(
        {
            "_id": session_id,
            "customer_id": customer_id,
            "cart": {},
            "updated_at": datetime.now(UTC),
        }
    )
    logger.info("Created session %s for customer %d", session_id, customer_id)
    return session_id


def add_to_cart(
    db: Database[dict[str, Any]], session_id: str, product_id: int, quantity: int
) -> None:
    """Add ``quantity`` units of a product (adding again increases it)."""
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    _update(db, session_id, {"$inc": {f"cart.{product_id}": quantity}})


def remove_from_cart(
    db: Database[dict[str, Any]], session_id: str, product_id: int
) -> None:
    """Remove a product from the cart."""
    _update(db, session_id, {"$unset": {f"cart.{product_id}": ""}})


def get_cart(db: Database[dict[str, Any]], session_id: str) -> dict[int, int]:
    """Return the cart as ``{product_id: quantity}``, ready for ``create_order``."""
    session = db[SESSIONS].find_one({"_id": session_id}, {"cart": 1})
    if session is None:
        raise SessionNotFoundError(f"Session {session_id} does not exist")
    return {int(product_id): qty for product_id, qty in session["cart"].items()}


def _update(
    db: Database[dict[str, Any]], session_id: str, change: dict[str, Any]
) -> None:
    """Apply ``change`` to the session's cart and refresh ``updated_at``."""
    result = db[SESSIONS].update_one(
        {"_id": session_id}, {**change, "$set": {"updated_at": datetime.now(UTC)}}
    )
    if result.matched_count == 0:
        raise SessionNotFoundError(f"Session {session_id} does not exist")
