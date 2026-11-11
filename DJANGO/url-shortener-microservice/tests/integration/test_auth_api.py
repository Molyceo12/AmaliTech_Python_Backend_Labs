"""Tests for ``/api/v1/auth/``: register."""

from typing import Any

import pytest
from django.test import Client

from accounts.models import User

pytestmark = pytest.mark.django_db

PASSWORD = "long-test-pass-42"


def _register(client: Client, **data: Any) -> Any:
    """POST a valid new account, changed by ``data``."""
    body = {"email": "Ann@Example.com", "username": "ann", "password": PASSWORD, **data}
    return client.post("/api/v1/auth/register/", body, content_type="application/json")


def test_register_creates_a_free_user_with_a_hashed_password(client: Client) -> None:
    """201 with the user (no password); the password is saved hashed."""
    response = _register(client, tier="premium")
    assert response.status_code == 201
    assert response.json() == {
        "status_code": 201,
        "message": "Account created.",
        "detail": {"email": "ann@example.com", "username": "ann", "tier": "free"},
    }
    user = User.objects.get(email="ann@example.com")
    assert user.password != PASSWORD
    assert user.check_password(PASSWORD)


@pytest.mark.parametrize(
    ("data", "field", "text"),
    [
        (
            {"email": "TAKEN@example.com"},
            "email",
            "A user with this email already exists.",
        ),
        ({"password": "short"}, "password", "This password is too short."),
        ({"password": "ann@example.com"}, "password", "too similar"),
        ({"username": ""}, "username", "This field may not be blank."),
    ],
)
def test_register_refuses_bad_input(
    client: Client, data: dict[str, str], field: str, text: str
) -> None:
    """400 for a taken email (any case), a weak password or a missing field."""
    User.objects.create_user(
        email="taken@example.com", username="taken", password=PASSWORD
    )
    response = _register(client, **data)
    assert response.status_code == 400
    assert text in " ".join(response.json()["detail"][field])
    assert User.objects.count() == 1
