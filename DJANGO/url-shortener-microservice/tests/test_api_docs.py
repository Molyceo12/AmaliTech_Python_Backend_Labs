"""Tests for the OpenAPI schema and the Swagger UI."""

from django.test import Client


def test_schema_lists_the_shorten_endpoint(client: Client) -> None:
    """The OpenAPI schema documents ``POST /api/v1/urls/``."""
    response = client.get("/api/schema/", {"format": "json"})
    assert response.status_code == 200
    responses = response.json()["paths"]["/api/v1/urls/"]["post"]["responses"]
    assert set(responses) == {"201", "400", "500"}


def test_schema_lists_the_redirect_endpoint(client: Client) -> None:
    """The OpenAPI schema documents ``GET /{short_code}/``."""
    response = client.get("/api/schema/", {"format": "json"})
    responses = response.json()["paths"]["/{short_code}/"]["get"]["responses"]
    assert set(responses) == {"302", "404", "500"}


def test_swagger_ui_loads(client: Client) -> None:
    """``/api/docs/`` serves the Swagger UI page."""
    response = client.get("/api/docs/")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()
