"""Tests for ``GET /<short_code>/``."""

import pytest
from django.test import Client

from shortener.models import ShortURL


@pytest.mark.django_db
def test_known_code_redirects_to_the_original_url(client: Client) -> None:
    """A saved code answers with a 302 to the long URL."""
    ShortURL.objects.create(
        original_url="https://example.com/long", short_code="abc1234"
    )
    response = client.get("/abc1234/")
    assert response.status_code == 302
    assert response["Location"] == "https://example.com/long"


@pytest.mark.django_db
def test_unknown_code_returns_404(client: Client) -> None:
    """A code that was never saved gets the JSON error."""
    response = client.get("/nothing1/")
    assert response.status_code == 404
    assert response.json() == {"status_code": 404, "detail": "Short code not found."}


@pytest.mark.django_db
def test_admin_is_not_taken_as_a_short_code(client: Client) -> None:
    """``admin/`` still reaches the admin, not the redirect."""
    assert client.get("/admin/").status_code == 302
    assert "/admin/login/" in client.get("/admin/")["Location"]
