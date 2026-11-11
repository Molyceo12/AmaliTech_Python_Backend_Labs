"""Shared test fixtures."""

import importlib
from collections.abc import Iterator
from types import ModuleType

import pytest
from django.core.cache import cache
from django.test import Client
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User
from tests.helpers import get_me
from url_shortener.settings import base


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Start each test with empty rate limit counters (they live in the cache)."""
    cache.clear()


@pytest.fixture(name="me")
def fixture_me(db: None) -> User:  # pylint: disable=unused-argument
    """The logged-in user of ``auth_client``."""
    return get_me()


@pytest.fixture(name="premium")
def fixture_premium(me: User) -> User:
    """Make ``me`` a Premium user."""
    me.tier = User.Tier.PREMIUM
    me.save()
    return me


@pytest.fixture(name="auth_client")
def fixture_auth_client(client: Client, me: User) -> Client:
    """``client`` that sends ``me``'s access token on every request."""
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {AccessToken.for_user(me)}"
    return client


@pytest.fixture(name="reload_base")
def fixture_reload_base(monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """Give the ``base`` settings module to reload with a fake environment.

    Afterwards the fake environment is undone and ``base`` reloaded, so later
    tests see the real values.
    """
    yield base
    monkeypatch.undo()
    importlib.reload(base)
