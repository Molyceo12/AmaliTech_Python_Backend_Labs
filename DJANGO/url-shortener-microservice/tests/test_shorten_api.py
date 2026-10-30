"""Tests for ``POST /api/urls/``."""

import pytest
from django.test import Client

from shortener.models import ShortURL
from shortener.serializers import ShortURLSerializer


@pytest.mark.django_db
def test_valid_url_returns_201_and_a_short_link(client: Client) -> None:
    """A valid URL is saved; the body has the status code, code and link."""
    response = client.post("/api/urls/", {"original_url": "https://example.com/page"})
    assert response.status_code == 201
    body = response.json()
    assert list(body) == [
        "status_code",
        "original_url",
        "short_code",
        "short_url",
        "created_at",
    ]
    assert body["status_code"] == 201
    assert ShortURL.objects.get(short_code=body["short_code"])
    assert body["short_url"] == f"http://testserver/{body['short_code']}/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"original_url": "not a url"}, "Enter a valid URL."),
        ({}, "This field is required."),
    ],
)
def test_invalid_or_missing_url_returns_400(
    client: Client, data: dict[str, str], message: str
) -> None:
    """Nothing is saved; the error has the status code and the field message."""
    response = client.post("/api/urls/", data)
    assert response.status_code == 400
    assert response.json() == {
        "status_code": 400,
        "detail": {"original_url": [message]},
    }
    assert not ShortURL.objects.exists()


def test_wrong_method_returns_the_json_error(client: Client) -> None:
    """Errors without a field keep DRF's message under ``detail``."""
    response = client.get("/api/urls/")
    assert response.status_code == 405
    assert response.json() == {
        "status_code": 405,
        "detail": 'Method "GET" not allowed.',
    }


def test_short_url_without_a_request_is_a_path() -> None:
    """Outside a request the serializer still gives a usable path."""
    short_url = ShortURL(original_url="https://example.com", short_code="abc1234")
    assert ShortURLSerializer(short_url).data["short_url"] == "/abc1234/"
