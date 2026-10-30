"""Tests for ``POST /api/urls/``."""

import pytest
from django.test import Client

from shortener.models import ShortURL
from shortener.serializers import ShortURLSerializer


@pytest.mark.django_db
def test_valid_url_returns_201_and_a_short_link(client: Client) -> None:
    """A valid URL is saved and the response holds its code and link."""
    response = client.post("/api/urls/", {"original_url": "https://example.com/page"})
    assert response.status_code == 201
    body = response.json()
    assert ShortURL.objects.get(short_code=body["short_code"])
    assert body["short_url"] == f"http://testserver/{body['short_code']}/"


@pytest.mark.django_db
@pytest.mark.parametrize("data", [{"original_url": "not a url"}, {}])
def test_invalid_or_missing_url_returns_400(
    client: Client, data: dict[str, str]
) -> None:
    """Nothing is saved when the URL is invalid or missing."""
    response = client.post("/api/urls/", data)
    assert response.status_code == 400
    assert "original_url" in response.json()
    assert not ShortURL.objects.exists()


def test_short_url_without_a_request_is_a_path() -> None:
    """Outside a request the serializer still gives a usable path."""

    short_url = ShortURL(original_url="https://example.com", short_code="abc1234")
    assert ShortURLSerializer(short_url).data["short_url"] == "/abc1234/"
