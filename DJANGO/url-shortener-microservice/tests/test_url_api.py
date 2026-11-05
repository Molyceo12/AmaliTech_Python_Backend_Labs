"""Tests for creating with details, listing, and one URL's get / update / delete."""

from datetime import timedelta
from typing import Any

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from accounts.models import User
from shortener.models import Click, ShortURL, Tag

pytestmark = pytest.mark.django_db

FUTURE = (timezone.now() + timedelta(days=7)).isoformat()


def _url(code: str = "abc1234", **fields: Any) -> ShortURL:
    """Save a short URL with the given code."""
    return ShortURL.objects.create(
        original_url="https://example.com/", short_code=code, **fields
    )


def _post(client: Client, **data: Any) -> Any:
    """POST JSON to ``/api/v1/urls/`` with a valid URL plus ``data``."""
    body = {"original_url": "https://example.com/", **data}
    return client.post("/api/v1/urls/", body, content_type="application/json")


# --- create -------------------------------------------------------------


def test_create_with_alias_expiry_tags_and_details(client: Client) -> None:
    """Every optional field is saved; tag names are trimmed and lowercased."""
    response = _post(
        client,
        custom_alias="docs",
        expires_at=FUTURE,
        title="Docs",
        description="Django docs",
        tags=[" Python ", "web"],
    )
    assert response.status_code == 201
    url = ShortURL.objects.get(custom_alias="docs")
    assert (url.title, url.description, url.expires_at is not None) == (
        "Docs",
        "Django docs",
        True,
    )
    assert response.json()["detail"]["tags"] == ["python", "web"]


def test_existing_tag_is_reused(client: Client) -> None:
    """A tag name already saved is linked, not created again."""
    Tag.objects.create(name="python")
    _post(client, tags=["Python"])
    assert Tag.objects.count() == 1


def test_client_cannot_set_read_only_fields(client: Client) -> None:
    """``owner``, ``short_code`` and ``click_count`` are ignored on input."""
    User.objects.create_user(email="ana@example.com", username="ana")
    response = _post(client, owner="ana@example.com", short_code="mine", click_count=9)
    detail = response.json()["detail"]
    assert (detail["owner"], detail["click_count"]) == (None, 0)
    assert detail["short_code"] != "mine"


@pytest.mark.parametrize("taken", ["docs", "abc1234"])
def test_alias_used_as_alias_or_code_returns_409(client: Client, taken: str) -> None:
    """An alias can't repeat another alias or another URL's short code."""
    _url(custom_alias="docs")
    response = _post(client, custom_alias=taken)
    assert response.status_code == 409
    assert response.json() == {
        "status_code": 409,
        "message": "Conflict",
        "detail": "This alias is already taken.",
    }


@pytest.mark.parametrize(
    ("data", "field"),
    [
        ({"custom_alias": "admin"}, "custom_alias"),
        ({"custom_alias": "API"}, "custom_alias"),
        ({"custom_alias": "has space"}, "custom_alias"),
        ({"expires_at": "2000-01-01T00:00:00Z"}, "expires_at"),
    ],
)
def test_bad_alias_or_past_expiry_returns_400(
    client: Client, data: dict[str, str], field: str
) -> None:
    """Reserved or badly formed alias, or an expiry in the past → 400."""
    response = _post(client, **data)
    assert response.status_code == 400
    assert field in response.json()["detail"]
    assert not ShortURL.objects.exists()


# --- list ---------------------------------------------------------------


def test_list_is_paginated(client: Client) -> None:
    """The list has ``count`` and ``results``; newest first."""
    _url("aaa1111")
    _url("bbb2222")
    body = client.get("/api/v1/urls/").json()["detail"]
    assert body["count"] == 2
    assert [item["short_code"] for item in body["results"]] == ["bbb2222", "aaa1111"]


def test_list_filters_and_ordering(client: Client) -> None:
    """``?status=`` and ``?ordering=`` use the branch 6 queries."""
    _url("live111", click_count=1)
    _url("hot1111", click_count=9)
    _url("off1111", is_active=False)
    old = _url("old1111", expires_at=timezone.now() + timedelta(seconds=1))
    ShortURL.objects.filter(pk=old.pk).update(
        expires_at=timezone.now() - timedelta(days=1),
        created_at=timezone.now() - timedelta(days=2),
    )

    def codes(query: str) -> list[str]:
        results = client.get(f"/api/v1/urls/?{query}").json()["detail"]["results"]
        return [item["short_code"] for item in results]

    assert set(codes("status=active")) == {"live111", "hot1111"}
    assert codes("status=expired") == ["old1111"]
    assert codes("status=active&ordering=popular") == ["hot1111", "live111"]


@pytest.mark.parametrize("query", ["status=old", "ordering=newest"])
def test_unknown_filter_returns_400(client: Client, query: str) -> None:
    """Only the documented values are accepted."""
    response = client.get(f"/api/v1/urls/?{query}")
    assert response.status_code == 400


def test_list_query_count_does_not_grow(client: Client) -> None:
    """Owners and tags are loaded together, so 5 URLs cost what 1 does."""
    user = User.objects.create_user(email="ana@example.com", username="ana")
    tag = Tag.objects.create(name="docs")

    def queries_for_list() -> int:
        with CaptureQueriesContext(connection) as queries:
            client.get("/api/v1/urls/")
        return len(queries)

    _url("url0000", owner=user).tags.add(tag)
    one = queries_for_list()
    for number in range(1, 5):
        _url(f"url000{number}", owner=user).tags.add(tag)
    assert queries_for_list() == one


# --- detail, update, delete ---------------------------------------------


def test_detail_shows_total_clicks(client: Client) -> None:
    """``total_clicks`` is counted by the database."""
    url = _url()
    Click.objects.create(short_url=url)
    Click.objects.create(short_url=url)
    response = client.get("/api/v1/urls/abc1234/")
    assert response.status_code == 200
    assert response.json()["detail"]["total_clicks"] == 2


def test_put_replaces_fields_and_tags(client: Client) -> None:
    """``PUT`` changes the URL, details and tags."""
    _url().tags.add(Tag.objects.create(name="old"))
    body = {
        "original_url": "https://example.com/new",
        "title": "New",
        "is_active": False,
        "tags": ["new"],
    }
    response = client.put("/api/v1/urls/abc1234/", body, content_type="application/json")
    assert response.status_code == 200
    assert (response.json()["detail"]["title"], response.json()["detail"]["tags"]) == ("New", ["new"])
    url = ShortURL.objects.get(short_code="abc1234")
    assert (url.original_url, url.is_active) == ("https://example.com/new", False)


def test_patch_keeps_own_alias_and_tags(client: Client) -> None:
    """Sending its own alias again is not a clash; tags stay when not sent."""
    _url(custom_alias="docs").tags.add(Tag.objects.create(name="keep"))
    response = client.patch(
        "/api/v1/urls/abc1234/",
        {"custom_alias": "docs", "title": "T"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["detail"]["tags"] == ["keep"]


def test_patch_null_removes_the_alias(client: Client) -> None:
    """``"custom_alias": null`` clears it, so the code alone works again."""
    _url(custom_alias="docs")
    response = client.patch(
        "/api/v1/urls/abc1234/", {"custom_alias": None}, content_type="application/json"
    )
    assert response.status_code == 200
    assert ShortURL.objects.get().custom_alias is None


def test_patch_to_taken_alias_returns_409(client: Client) -> None:
    """Another URL's alias can't be taken on update either."""
    _url("aaa1111", custom_alias="docs")
    _url("bbb2222")
    response = client.patch(
        "/api/v1/urls/bbb2222/",
        {"custom_alias": "docs"},
        content_type="application/json",
    )
    assert response.status_code == 409


def test_delete_returns_204(client: Client) -> None:
    """The URL is gone afterwards."""
    _url()
    assert client.delete("/api/v1/urls/abc1234/").status_code == 204
    assert not ShortURL.objects.exists()


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_unknown_code_returns_404(client: Client, method: str) -> None:
    """Every detail method answers 404 for a code that doesn't exist."""
    response = getattr(client, method)(
        "/api/v1/urls/nothing/", {}, content_type="application/json"
    )
    assert response.status_code == 404
