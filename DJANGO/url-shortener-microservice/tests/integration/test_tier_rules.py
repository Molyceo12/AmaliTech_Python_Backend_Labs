"""Tier rules on ``/api/v1/urls/``: active URL limit for Free users."""

from datetime import timedelta
from typing import Any

import pytest
from django.test import Client
from django.utils import timezone

from accounts.models import User
from shortener.services.limits import FREE_ACTIVE_LIMIT
from tests.helpers import expire, make_url

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("auth_client")]

LIMIT_MESSAGE = "Free plan: at most 10 active URLs."


def _post(client: Client, **data: Any) -> Any:
    """Create a URL as ``me``."""
    body = {"original_url": "https://example.com/", **data}
    return client.post("/api/v1/urls/", body, content_type="application/json")


def _fill_active_urls() -> None:
    """Give ``me`` exactly the Free limit of active URLs."""
    for number in range(FREE_ACTIVE_LIMIT):
        make_url(f"act{number:04}")


def test_free_user_cannot_create_an_11th_active_url(client: Client) -> None:
    """10 active URLs are allowed; the 11th → 403."""
    _fill_active_urls()
    response = _post(client)
    assert response.status_code == 403
    assert response.json()["message"] == LIMIT_MESSAGE


def test_switched_off_and_expired_urls_do_not_count(client: Client) -> None:
    """Only active URLs count towards the limit."""
    for number in range(FREE_ACTIVE_LIMIT - 1):
        make_url(f"act{number:04}")
    make_url("off1111", is_active=False)
    expire(make_url("old1111", expires_at=timezone.now() + timedelta(seconds=1)))
    assert _post(client).status_code == 201
    assert _post(client, is_active=False).status_code == 201


def test_free_user_cannot_reactivate_at_the_limit(client: Client) -> None:
    """Turning a URL back on counts like a new one."""
    _fill_active_urls()
    make_url("off1111", is_active=False)
    response = client.patch(
        "/api/v1/urls/off1111/", {"is_active": True}, content_type="application/json"
    )
    assert response.status_code == 403
    assert response.json()["message"] == LIMIT_MESSAGE


@pytest.mark.parametrize("tier", [User.Tier.PREMIUM, User.Tier.ADMIN])
def test_premium_and_admin_have_no_limit(client: Client, me: User, tier: str) -> None:
    """Paid tiers can go past 10 active URLs."""
    me.tier = tier
    me.save()
    _fill_active_urls()
    assert _post(client).status_code == 201
