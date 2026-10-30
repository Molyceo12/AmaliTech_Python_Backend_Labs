"""Tests for the OpenAPI schema and the Swagger UI."""

from django.test import Client


def test_schema_lists_the_shorten_endpoint(client: Client) -> None:
    """The OpenAPI schema documents ``POST /api/urls/``."""
    response = client.get("/api/schema/", {"format": "json"})
    assert response.status_code == 200
    assert "post" in response.json()["paths"]["/api/urls/"]


def test_swagger_ui_loads(client: Client) -> None:
    """``/api/docs/`` serves the Swagger UI page."""
    response = client.get("/api/docs/")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()
