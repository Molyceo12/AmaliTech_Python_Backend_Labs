"""Tests for the JSON errors: crashes and unknown routes."""

import json
from typing import Any
from unittest.mock import MagicMock

import pytest
from django.db import DatabaseError
from django.test import Client, RequestFactory

from url_shortener.exceptions import bad_request, permission_denied, server_error

SERVER_ERROR = {
    "status_code": 500,
    "message": "Internal server error.",
    "detail": "Internal server error.",
}


@pytest.mark.django_db
@pytest.mark.usefixtures("auth_client")
@pytest.mark.parametrize(
    ("target", "call"),
    [
        (
            "shortener.views.short_url.list_create.create_short_url",
            ("post", "/api/v1/urls/"),
        ),
        ("shortener.models.ShortURL.objects.filter", ("get", "/abc1234/")),
    ],
)
def test_crash_returns_json_500_and_logs(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    target: str,
    call: tuple[str, str],
) -> None:
    """A database error in the API or the redirect → JSON 500 + logged traceback."""
    crash = MagicMock(side_effect=DatabaseError("database is down"))
    monkeypatch.setattr(target, crash)
    method, path = call
    response = getattr(client, method)(path, {"original_url": "https://example.com/"})
    crash.assert_called_once()
    assert response.status_code == 500
    assert response.json() == SERVER_ERROR
    assert "Unhandled error" in caplog.text
    assert "database is down" in caplog.text


def test_unknown_route_returns_json_404(client: Client) -> None:
    """A path no route matches gets JSON, not Django's HTML page."""
    response = client.get("/no/such/page/")
    assert response.status_code == 404
    assert response.json() == {
        "status_code": 404,
        "message": "Not found.",
        "detail": "Not found.",
    }


@pytest.mark.parametrize(
    ("handler", "status", "text"),
    [
        (bad_request, 400, "Bad request."),
        (permission_denied, 403, "Permission denied."),
        (lambda request, _: server_error(request), 500, "Internal server error."),
    ],
)
def test_django_errors_use_the_shared_shape(
    handler: Any, status: int, text: str
) -> None:
    """``handler400`` / ``403`` / ``500`` answer in the same JSON shape."""
    response = handler(RequestFactory().get("/"), Exception())
    assert response.status_code == status
    assert json.loads(response.content) == {
        "status_code": status,
        "message": text,
        "detail": text,
    }
