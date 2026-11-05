"""Tests for the JSON errors: crashes and unknown routes."""

import json

import pytest
from django.db import DatabaseError
from django.test import Client, RequestFactory

from url_shortener.exceptions import server_error

SERVER_ERROR = {"status_code": 500, "detail": "Internal server error."}


def _crash(*args: object, **kwargs: object) -> None:
    """Stand-in for a database call that fails."""
    raise DatabaseError("database is down")


@pytest.mark.django_db
def test_crash_in_shorten_returns_json_500_and_logs(
    client: Client, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """A database error while saving gives a JSON 500 and a logged traceback."""
    monkeypatch.setattr("shortener.views.short_url.create_short_url", _crash)
    response = client.post("/api/urls/", {"original_url": "https://example.com/"})
    assert response.status_code == 500
    assert response.json() == SERVER_ERROR
    assert "Unhandled error" in caplog.text
    assert "database is down" in caplog.text


def test_crash_in_redirect_returns_json_500(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A database error while looking up a code gives a JSON 500."""
    monkeypatch.setattr("shortener.models.ShortURL.objects.filter", _crash)
    response = client.get("/abc1234/")
    assert response.status_code == 500
    assert response.json() == SERVER_ERROR


def test_unknown_route_returns_json_404(client: Client) -> None:
    """A path no route matches gets JSON, not Django's HTML page."""
    response = client.get("/no/such/page/")
    assert response.status_code == 404
    assert response.json() == {"status_code": 404, "detail": "Not found."}


def test_crash_outside_a_view_returns_json_500() -> None:
    """``handler500`` answers with the same JSON body."""
    response = server_error(RequestFactory().get("/"))
    assert response.status_code == 500
    assert json.loads(response.content) == SERVER_ERROR
