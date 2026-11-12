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
from tests.helpers import expire
from tests.helpers import make_url as _url

# Every test here is logged in as "me": auth_client adds the token to client.
pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("auth_client")]

FUTURE = (timezone.now() + timedelta(days=7)).isoformat()


def _post(client: Client, **data: Any) -> Any:
    """POST JSON to ``/api/v1/urls/`` with a valid URL plus ``data``."""
    body = {"original_url": "https://example.com/", **data}
    return client.post("/api/v1/urls/", body, content_type="application/json")


@pytest.mark.usefixtures("premium")
def test_create_with_alias_expiry_tags_and_details(client: Client) -> None:
    """Every optional field is saved; tags are trimmed, lowercased and reused."""
    Tag.objects.create(name="python")
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
    assert Tag.objects.filter(name="python").count() == 1


def test_client_cannot_set_read_only_fields(client: Client) -> None:
    """``owner``, ``short_code`` and ``click_count`` are ignored on input."""
    User.objects.create_user(email="ana@example.com", username="ana")
    response = _post(client, owner="ana@example.com", short_code="mine", click_count=9)
    detail = response.json()["detail"]
    assert (detail["owner"], detail["click_count"]) == ("me@example.com", 0)
    assert detail["short_code"] != "mine"


@pytest.mark.parametrize(
    ("method", "taken"), [("post", "docs"), ("post", "abc1234"), ("patch", "docs")]
)
def test_taken_alias_returns_409(client: Client, method: str, taken: str) -> None:
    """On create or update, an alias can't repeat another alias or short code."""
    _url(custom_alias="docs")
    if method == "post":
        response = _post(client, custom_alias=taken)
    else:
        _url("bbb2222")
        response = client.patch(
            "/api/v1/urls/bbb2222/",
            {"custom_alias": taken},
            content_type="application/json",
        )
    assert response.status_code == 409
    assert response.json() == {
        "status_code": 409,
        "message": "This alias is already taken.",
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


def test_list_is_paginated(client: Client) -> None:
    """The list has its toast, ``count`` and ``results``; newest first."""
    _url("aaa1111")
    _url("bbb2222")
    response = client.get("/api/v1/urls/").json()
    assert response["message"] == "Short URLs loaded."
    body = response["detail"]
    assert body["count"] == 2
    assert [item["short_code"] for item in body["results"]] == ["bbb2222", "aaa1111"]


def test_list_shows_only_my_urls(client: Client) -> None:
    """Another user's URL is not in my list."""
    _url("mine111")
    ana = User.objects.create_user(email="ana@example.com", username="ana")
    _url("anas111", owner=ana)
    results = client.get("/api/v1/urls/").json()["detail"]["results"]
    assert [url["short_code"] for url in results] == ["mine111"]


def test_list_filters_and_ordering(client: Client) -> None:
    """``?status=`` and ``?ordering=`` use the branch 6 queries."""
    _url("live111", click_count=1)
    _url("hot1111", click_count=9)
    _url("off1111", is_active=False)
    old = _url("old1111", expires_at=timezone.now() + timedelta(seconds=1))
    expire(old)

    def codes(query: str) -> list[str]:
        results = client.get(f"/api/v1/urls/?{query}").json()["detail"]["results"]
        return [item["short_code"] for item in results]

    assert set(codes("status=active")) == {"live111", "hot1111"}
    assert codes("status=expired") == ["old1111"]
    assert codes("status=active&ordering=popular") == ["hot1111", "live111"]


def test_tag_search_in_any_case_and_with_status(client: Client) -> None:
    """``?tag=`` keeps URLs with that tag; it works together with ``?status=``."""
    python = Tag.objects.create(name="python")
    _url("py11111").tags.add(python)
    _url("pyoff11", is_active=False).tags.add(python)
    _url("web1111").tags.add(Tag.objects.create(name="web"))

    def codes(query: str) -> list[str]:
        results = client.get(f"/api/v1/urls/?{query}").json()["detail"]["results"]
        return sorted(url["short_code"] for url in results)

    assert codes("tag=PYTHON") == ["py11111", "pyoff11"]
    assert codes("tag=python&status=active") == ["py11111"]


@pytest.mark.parametrize(
    ("query", "message"),
    [("status=old", "Use active or expired."), ("ordering=newest", "Use popular.")],
)
def test_unknown_filter_returns_400(client: Client, query: str, message: str) -> None:
    """Only the documented values are accepted; the error is the toast."""
    response = client.get(f"/api/v1/urls/?{query}")
    assert (response.status_code, response.json()["message"]) == (400, message)


def test_list_query_count_does_not_grow(client: Client) -> None:
    """Owners and tags are loaded together, so 5 URLs cost what 1 does."""
    tag = Tag.objects.create(name="docs")

    def queries_for_list() -> int:
        with CaptureQueriesContext(connection) as queries:
            client.get("/api/v1/urls/")
        return len(queries)

    _url("url0000").tags.add(tag)
    one = queries_for_list()
    for number in range(1, 5):
        _url(f"url000{number}").tags.add(tag)
    assert queries_for_list() == one


@pytest.mark.parametrize(
    ("countries", "by_country"),
    [
        ([], []),
        (
            ["Ghana", "Rwanda", "Rwanda", ""],
            [
                {"country": "Rwanda", "total": 2},
                {"country": "", "total": 1},
                {"country": "Ghana", "total": 1},
            ],
        ),
    ],
)
@pytest.mark.usefixtures("premium")
def test_detail_shows_click_totals(
    client: Client, countries: list[str], by_country: list[dict[str, Any]]
) -> None:
    """``total_clicks`` and per-country totals (most first; ``""`` = unknown)."""
    url = _url()
    for country in countries:
        Click.objects.create(url=url, country=country)
    response = client.get("/api/v1/urls/abc1234/")
    detail = response.json()["detail"]
    assert (response.status_code, detail["total_clicks"]) == (200, len(countries))
    assert detail["clicks_by_country"] == by_country


def test_free_user_gets_detail_without_country_stats(client: Client) -> None:
    """Country stats are geo analytics: Premium only. Totals stay."""
    Click.objects.create(url=_url(), country="Rwanda")
    detail = client.get("/api/v1/urls/abc1234/").json()["detail"]
    assert detail["total_clicks"] == 1
    assert "clicks_by_country" not in detail


def test_detail_query_count_does_not_grow_with_clicks(client: Client) -> None:
    """The country totals are one ``GROUP BY`` query, not one per click."""
    url = _url()

    def queries() -> int:
        with CaptureQueriesContext(connection) as context:
            client.get("/api/v1/urls/abc1234/")
        return len(context)

    Click.objects.create(url=url, country="Ghana")
    before = queries()
    for country in ["Kenya", "Rwanda", "Rwanda"]:
        Click.objects.create(url=url, country=country)
    assert queries() == before


def test_put_replaces_fields_and_tags(client: Client) -> None:
    """``PUT`` changes the URL, details and tags."""
    _url().tags.add(Tag.objects.create(name="old"))
    body = {
        "original_url": "https://example.com/new",
        "title": "New",
        "is_active": False,
        "tags": ["new"],
    }
    response = client.put(
        "/api/v1/urls/abc1234/", body, content_type="application/json"
    )
    assert response.status_code == 200
    detail = response.json()["detail"]
    assert (detail["title"], detail["tags"]) == ("New", ["new"])
    url = ShortURL.objects.get(short_code="abc1234")
    assert (url.original_url, url.is_active) == ("https://example.com/new", False)


def test_patch_keeps_own_alias_and_tags_and_null_clears_it(client: Client) -> None:
    """Own alias again is no clash; tags stay when not sent; ``null`` clears it."""
    _url(custom_alias="docs").tags.add(Tag.objects.create(name="keep"))
    response = client.patch(
        "/api/v1/urls/abc1234/",
        {"custom_alias": "docs", "title": "T"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["detail"]["tags"] == ["keep"]
    response = client.patch(
        "/api/v1/urls/abc1234/", {"custom_alias": None}, content_type="application/json"
    )
    assert response.status_code == 200
    assert ShortURL.objects.get().custom_alias is None


def test_delete_returns_200_with_a_message(client: Client) -> None:
    """The URL is gone afterwards."""
    _url()
    response = client.delete("/api/v1/urls/abc1234/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "message": "Short URL deleted.",
        "detail": None,
    }
    assert not ShortURL.objects.exists()


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_unknown_code_returns_404(client: Client, method: str) -> None:
    """Every detail method answers 404 for a code that doesn't exist."""
    response = getattr(client, method)(
        "/api/v1/urls/nothing/", {}, content_type="application/json"
    )
    assert response.status_code == 404


def test_detail_update_and_delete_by_alias(client: Client) -> None:
    """``/api/v1/urls/<alias>/`` works like the short code."""
    _url(custom_alias="docs")
    assert client.get("/api/v1/urls/docs/").json()["detail"]["short_code"] == "abc1234"
    response = client.patch(
        "/api/v1/urls/docs/", {"title": "Docs"}, content_type="application/json"
    )
    assert response.status_code == 200
    assert ShortURL.objects.get().title == "Docs"
    assert client.delete("/api/v1/urls/docs/").status_code == 200
    assert not ShortURL.objects.exists()


def test_someone_elses_url_by_alias_is_still_403(client: Client) -> None:
    """The owner check runs after the alias lookup."""
    ana = User.objects.create_user(email="ana@example.com", username="ana")
    _url(owner=ana, custom_alias="docs")
    response = client.delete("/api/v1/urls/docs/")
    assert response.status_code == 403


def test_anyone_logged_in_can_read_another_users_url(client: Client) -> None:
    """The "ReadOnly" part: GET works on a URL I don't own."""
    _url(owner=User.objects.create_user(email="ana@example.com", username="ana"))
    assert client.get("/api/v1/urls/abc1234/").status_code == 200


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
def test_only_the_owner_can_change_or_delete(client: Client, method: str) -> None:
    """Changing or deleting someone else's URL → 403; nothing changes."""
    _url(owner=User.objects.create_user(email="ana@example.com", username="ana"))
    body = {"original_url": "https://example.com/new"}
    response = getattr(client, method)(
        "/api/v1/urls/abc1234/", body, content_type="application/json"
    )
    assert response.status_code == 403
    assert response.json()["message"] == "You can only change your own short URLs."
    assert ShortURL.objects.get().original_url == "https://example.com/"


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/urls/"),
        ("post", "/api/v1/urls/"),
        ("get", "/api/v1/urls/abc1234/"),
        ("patch", "/api/v1/urls/abc1234/"),
        ("delete", "/api/v1/urls/abc1234/"),
    ],
)
def test_no_token_returns_401(method: str, path: str) -> None:
    """The URL API needs a login; a client with no token gets 401."""
    _url()
    response = getattr(Client(), method)(path)
    assert response.status_code == 401
    assert response.json()["message"] == (
        "Authentication credentials were not provided."
    )


def test_old_unversioned_route_is_gone(client: Client) -> None:
    """``/api/urls/`` moved to ``/api/v1/urls/``."""
    assert client.get("/api/urls/").status_code == 404
