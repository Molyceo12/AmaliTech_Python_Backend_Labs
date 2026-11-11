"""Tests for ``/api/v1/auth/``: register, login, refresh."""

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


# --- login and refresh --------------------------------------------------


@pytest.fixture(name="user")
def fixture_user() -> User:
    """A saved user who can log in with ``PASSWORD``."""
    return User.objects.create_user(
        email="ann@example.com", username="ann", password=PASSWORD
    )


def _login(client: Client, email: str = "ann@example.com", **data: Any) -> Any:
    """POST email + password to the login endpoint."""
    body = {"email": email, "password": PASSWORD, **data}
    return client.post("/api/v1/auth/login/", body, content_type="application/json")


def _refresh(client: Client, token: str) -> Any:
    """POST a refresh token to get a new access token."""
    body = {"refresh": token}
    return client.post("/api/v1/auth/refresh/", body, content_type="application/json")


@pytest.mark.usefixtures("user")
@pytest.mark.parametrize("email", ["ann@example.com", "ANN@Example.com"])
def test_login_returns_access_and_refresh_tokens(client: Client, email: str) -> None:
    """Right password (email in any case) → both tokens."""
    response = _login(client, email)
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Logged in."
    assert set(body["detail"]) == {"access", "refresh"}


@pytest.mark.usefixtures("user")
@pytest.mark.parametrize("email", ["ann@example.com", "nobody@example.com"])
def test_wrong_login_gets_401_with_one_message(client: Client, email: str) -> None:
    """Wrong password and unknown email look the same, so emails can't be guessed."""
    response = _login(client, email, password="not-the-password")
    assert response.status_code == 401
    assert response.json()["message"] == (
        "No active account found with the given credentials"
    )


@pytest.mark.usefixtures("user")
def test_refresh_gives_a_new_access_token(client: Client) -> None:
    """A refresh token from login → a new access token."""
    refresh = _login(client).json()["detail"]["refresh"]
    response = _refresh(client, refresh)
    assert response.status_code == 200
    assert response.json()["message"] == "Token refreshed."
    assert "access" in response.json()["detail"]


@pytest.mark.usefixtures("user")
def test_sixth_login_in_a_minute_gets_429(client: Client) -> None:
    """5 tries pass (even wrong ones); the 6th is refused, even if it is right."""
    for _ in range(5):
        assert _login(client, password="wrong-guess").status_code == 401
    response = _login(client)
    assert response.status_code == 429
    assert response.json()["message"].startswith("Request was throttled.")


def test_bad_tokens_get_401(client: Client) -> None:
    """A broken refresh token, or a broken access token on any API call → 401."""
    assert _refresh(client, "not-a-token").status_code == 401
    response = client.get("/api/v1/urls/", HTTP_AUTHORIZATION="Bearer not-a-token")
    assert response.status_code == 401
