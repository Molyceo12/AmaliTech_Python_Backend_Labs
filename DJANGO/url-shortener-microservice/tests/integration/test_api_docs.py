"""Tests for the OpenAPI schema and the Swagger UI."""

from typing import Any

import pytest
from django.test import Client


@pytest.fixture(name="paths")
def fixture_paths(client: Client) -> dict[str, Any]:
    """The ``paths`` part of the OpenAPI schema."""
    response = client.get("/api/schema/", {"format": "json"})
    assert response.status_code == 200
    paths: dict[str, Any] = response.json()["paths"]
    return paths


@pytest.mark.parametrize(
    ("path", "method", "codes"),
    [
        ("/api/v1/urls/", "get", {"200", "400", "401", "500"}),
        ("/api/v1/urls/", "post", {"201", "400", "401", "409", "500"}),
        ("/api/v1/urls/{short_code}/", "get", {"200", "400", "401", "404", "500"}),
        (
            "/api/v1/urls/{short_code}/",
            "put",
            {"200", "400", "401", "403", "404", "409", "500"},
        ),
        (
            "/api/v1/urls/{short_code}/",
            "patch",
            {"200", "400", "401", "403", "404", "409", "500"},
        ),
        ("/api/v1/urls/{short_code}/", "delete", {"200", "401", "403", "404"}),
        ("/{short_code}/", "get", {"302", "404", "410", "500"}),
        ("/api/v1/auth/register/", "post", {"201", "400", "500"}),
        ("/api/v1/auth/login/", "post", {"200", "400", "401", "429", "500"}),
        ("/api/v1/auth/refresh/", "post", {"200", "400", "401", "500"}),
    ],
)
def test_schema_lists_every_endpoint_with_its_codes(
    paths: dict[str, Any], path: str, method: str, codes: set[str]
) -> None:
    """Swagger documents each endpoint and its success and error codes."""
    assert set(paths[path][method]["responses"]) == codes


def test_list_documents_its_filters(paths: dict[str, Any]) -> None:
    """``?status=``, ``?ordering=`` and ``?tag=`` show up in Swagger."""
    names = {param["name"] for param in paths["/api/v1/urls/"]["get"]["parameters"]}
    assert {"status", "ordering", "tag", "page"} <= names


def test_swagger_ui_loads(client: Client) -> None:
    """``/api/docs/`` serves the Swagger UI page."""
    response = client.get("/api/docs/")
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()
