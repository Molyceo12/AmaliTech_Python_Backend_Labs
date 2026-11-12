"""Tests for ``GET /api/v1/analytics/<short_code>/``."""

import pytest
from django.test import Client

from accounts.models import User
from shortener.models import Click
from tests.helpers import make_url

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("auth_client")]

PATH = "/api/v1/analytics/abc1234/"


@pytest.mark.parametrize("tier", [User.Tier.PREMIUM, User.Tier.ADMIN])
def test_premium_owner_gets_the_numbers(client: Client, me: User, tier: str) -> None:
    """Premium and Admin owners → 200 with total, per day and per country."""
    me.tier = tier
    me.save()
    url = make_url()
    Click.objects.create(url=url, country="Rwanda")
    response = client.get(PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Analytics loaded."
    detail = body["detail"]
    assert (detail["short_code"], detail["total_clicks"]) == ("abc1234", 1)
    assert [row["total"] for row in detail["clicks_per_day"]] == [1]
    assert detail["clicks_by_country"] == [{"country": "Rwanda", "total": 1}]


@pytest.mark.usefixtures("premium")
def test_analytics_by_alias(client: Client) -> None:
    """``/api/v1/analytics/<alias>/`` works like the short code."""
    make_url(custom_alias="docs")
    response = client.get("/api/v1/analytics/docs/")
    assert response.status_code == 200
    assert response.json()["detail"]["short_code"] == "abc1234"


def test_free_user_gets_403(client: Client) -> None:
    """Analytics are a Premium feature."""
    make_url()
    response = client.get(PATH)
    assert response.status_code == 403
    assert response.json()["message"] == "Analytics are for Premium users."


@pytest.mark.usefixtures("premium")
def test_someone_elses_url_gets_403(client: Client) -> None:
    """Premium can't see other users' numbers."""
    make_url(owner=User.objects.create_user(email="ana@example.com", username="ana"))
    response = client.get(PATH)
    assert response.status_code == 403
    assert response.json()["message"] == "You can only see your own short URLs."


@pytest.mark.usefixtures("premium")
def test_unknown_code_gets_404(client: Client) -> None:
    """No such short code."""
    assert client.get(PATH).status_code == 404


def test_no_token_gets_401() -> None:
    """Login needed, like the rest of the API."""
    assert Client().get(PATH).status_code == 401
