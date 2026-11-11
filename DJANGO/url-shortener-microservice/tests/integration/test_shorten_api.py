"""Tests for ``POST /api/v1/urls/``."""

from typing import Any

import pytest
from django.test import Client

from shortener.models import ShortURL
from shortener.serializers import ShortURLSerializer

BAD_URL = "Enter a valid URL."
NO_URL = "This field is required."
NOT_ALLOWED = 'Method "DELETE" not allowed.'


@pytest.mark.django_db
@pytest.mark.usefixtures("auth_client")
def test_valid_url_returns_201_and_a_short_link(client: Client) -> None:
    """A valid URL is saved; the body has status code, message and the URL."""
    response = client.post(
        "/api/v1/urls/", {"original_url": "https://example.com/page"}
    )
    assert response.status_code == 201
    body = response.json()
    assert (body["status_code"], body["message"]) == (201, "Short URL created.")
    detail = body["detail"]
    assert (detail["tags"], detail["owner"], detail["is_active"]) == (
        [],
        "me@example.com",
        True,
    )
    assert ShortURL.objects.get(short_code=detail["short_code"])
    assert detail["short_url"] == f"http://testserver/{detail['short_code']}/"


@pytest.mark.django_db
@pytest.mark.usefixtures("auth_client")
@pytest.mark.parametrize(
    ("method", "data", "status", "detail"),
    [
        ("post", {"original_url": "x"}, 400, {"original_url": [BAD_URL]}),
        ("post", {}, 400, {"original_url": [NO_URL]}),
        ("delete", {}, 405, NOT_ALLOWED),
    ],
)
def test_bad_request_returns_the_json_error(
    client: Client, method: str, data: dict[str, str], status: int, detail: Any
) -> None:
    """Nothing is saved; the toast is the first error text."""
    response = getattr(client, method)("/api/v1/urls/", data)
    message = detail if isinstance(detail, str) else detail["original_url"][0]
    assert response.status_code == status
    assert response.json() == {
        "status_code": status,
        "message": message,
        "detail": detail,
    }
    assert not ShortURL.objects.exists()


@pytest.mark.django_db
def test_short_url_without_a_request_is_a_path() -> None:
    """Outside a request the serializer still gives a usable path."""
    short_url = ShortURL.objects.create(
        original_url="https://example.com", short_code="abc1234"
    )
    assert ShortURLSerializer(short_url).data["short_url"] == "/abc1234/"
