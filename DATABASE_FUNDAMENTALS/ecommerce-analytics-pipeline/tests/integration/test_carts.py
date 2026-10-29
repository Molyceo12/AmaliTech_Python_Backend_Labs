"""Integration test: carts in the real MongoDB."""

from typing import Any

from pymongo.database import Database

from ecommerce_pipeline.sessions.carts import (
    add_to_cart,
    create_session,
    get_cart,
    remove_from_cart,
)


def test_cart_add_twice_remove_and_read(mongo_db: Database[dict[str, Any]]) -> None:
    """Quantities add up, removed products disappear."""
    session_id = create_session(mongo_db, 1)
    add_to_cart(mongo_db, session_id, 4, 1)
    add_to_cart(mongo_db, session_id, 4, 2)
    add_to_cart(mongo_db, session_id, 9, 1)
    remove_from_cart(mongo_db, session_id, 9)
    assert get_cart(mongo_db, session_id) == {4: 3}
