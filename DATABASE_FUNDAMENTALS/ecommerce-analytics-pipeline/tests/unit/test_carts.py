"""Tests for MongoDB carts (mocked collection)."""

from unittest.mock import MagicMock

import pytest

from ecommerce_pipeline.exceptions import SessionNotFoundError
from ecommerce_pipeline.sessions.carts import (
    SESSIONS,
    add_to_cart,
    create_session,
    get_cart,
    remove_from_cart,
)


@pytest.fixture(name="db")
def fixture_db() -> MagicMock:
    """A database mock; ``db[SESSIONS]`` is ``db.sessions``."""
    db = MagicMock()
    db.sessions = db.__getitem__.return_value
    return db


def test_create_session_inserts_an_empty_cart(db: MagicMock) -> None:
    """A new session belongs to the customer and starts empty."""
    session_id = create_session(db, 1)
    db.__getitem__.assert_called_with(SESSIONS)
    document = db.sessions.insert_one.call_args.args[0]
    assert document["_id"] == session_id
    assert document["customer_id"] == 1
    assert document["cart"] == {}


def test_add_to_cart_increments_the_quantity(db: MagicMock) -> None:
    """Adding uses ``$inc`` on the product's key."""
    add_to_cart(db, "s1", 4, 2)
    query, update = db.sessions.update_one.call_args.args
    assert query == {"_id": "s1"}
    assert update["$inc"] == {"cart.4": 2}


def test_add_to_cart_rejects_a_quantity_below_1(db: MagicMock) -> None:
    """Zero or negative quantities never reach MongoDB."""
    with pytest.raises(ValueError):
        add_to_cart(db, "s1", 4, 0)
    db.sessions.update_one.assert_not_called()


def test_remove_from_cart_unsets_the_product(db: MagicMock) -> None:
    """Removing uses ``$unset`` on the product's key."""
    remove_from_cart(db, "s1", 4)
    assert db.sessions.update_one.call_args.args[1]["$unset"] == {"cart.4": ""}


def test_get_cart_turns_keys_back_into_ints(db: MagicMock) -> None:
    """String keys from MongoDB become product ids."""
    db.sessions.find_one.return_value = {"cart": {"4": 2, "9": 1}}
    assert get_cart(db, "s1") == {4: 2, 9: 1}


def test_unknown_session_raises(db: MagicMock) -> None:
    """Reading or changing a missing session raises ``SessionNotFoundError``."""
    db.sessions.find_one.return_value = None
    db.sessions.update_one.return_value.matched_count = 0
    with pytest.raises(SessionNotFoundError):
        get_cart(db, "nope")
    with pytest.raises(SessionNotFoundError):
        remove_from_cart(db, "nope", 4)
