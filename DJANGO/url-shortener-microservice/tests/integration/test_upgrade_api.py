"""Tests for ``POST /api/v1/account/upgrade/``."""

from typing import Any

import pytest
from django.test import Client

from accounts.models import User

pytestmark = pytest.mark.django_db

PATH = "/api/v1/account/upgrade/"


def _upgrade(client: Client, **data: Any) -> Any:
    """POST a payment id and the Premium plan, changed by ``data``."""
    body = {"payment_id": "pay_123", "plan": "premium", **data}
    return client.post(PATH, body, content_type="application/json")


def test_free_user_upgrades_to_premium(auth_client: Client, me: User) -> None:
    """Any ``payment_id`` makes a Free user Premium."""
    response = _upgrade(auth_client)
    assert response.status_code == 200
    assert response.json()["message"] == "Upgraded to Premium."
    assert response.json()["detail"] == {"tier": "premium"}
    me.refresh_from_db()
    assert me.tier == User.Tier.PREMIUM
    assert me.is_premium


@pytest.mark.parametrize("tier", [User.Tier.PREMIUM, User.Tier.ADMIN])
def test_only_free_users_can_upgrade(auth_client: Client, me: User, tier: str) -> None:
    """Premium has nothing to gain; Admin would lose its tier."""
    me.tier = tier
    me.save()
    response = _upgrade(auth_client)
    assert response.status_code == 400
    assert response.json()["message"] == "Only Free users can upgrade."


def test_payment_id_and_plan_are_required(auth_client: Client) -> None:
    """Neither sent → ``400`` on both fields."""
    response = auth_client.post(PATH, {}, content_type="application/json")
    assert response.status_code == 400
    assert {"payment_id", "plan"} <= set(response.json()["detail"])


@pytest.mark.parametrize("plan", ["free", "admin", "gold"])
def test_only_the_premium_plan_can_be_bought(auth_client: Client, plan: str) -> None:
    """Admin is not for sale; Free is not an upgrade."""
    response = _upgrade(auth_client, plan=plan)
    assert response.status_code == 400
    assert "plan" in response.json()["detail"]


def test_upgrade_needs_a_token(client: Client) -> None:
    """Anonymous → ``401``."""
    assert _upgrade(client).status_code == 401
