"""Tests for ``GET /<short_code>/``."""

from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from shortener.models import Click, ShortURL
from tests.helpers import expire


def _url(**fields: object) -> ShortURL:
    """Save ``abc1234`` pointing at ``https://example.com/long``."""
    return ShortURL.objects.create(
        original_url="https://example.com/long", short_code="abc1234", **fields
    )


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/abc1234/", "/docs/"])
def test_code_or_alias_redirects_to_the_original_url(client: Client, path: str) -> None:
    """The short code and the custom alias both answer with a 302."""
    _url(custom_alias="docs")
    response = client.get(path)
    assert response.status_code == 302
    assert response["Location"] == "https://example.com/long"


@pytest.mark.django_db
def test_redirect_records_a_click(client: Client) -> None:
    """One ``Click`` is saved and ``click_count`` goes up by 1."""
    url = _url()
    client.get("/abc1234/", HTTP_USER_AGENT="pytest", HTTP_REFERER="https://a.io/")
    click = Click.objects.get(short_url=url)
    assert (click.ip_address, click.user_agent, click.referrer) == (
        "127.0.0.1",
        "pytest",
        "https://a.io/",
    )
    url.refresh_from_db()
    assert url.click_count == 1


@pytest.mark.django_db
@pytest.mark.parametrize("code", ["nothing1", "abc1234"])
def test_unknown_or_inactive_returns_404(client: Client, code: str) -> None:
    """Unknown and switched-off URLs get the same 404; no click is saved."""
    _url(is_active=False)
    response = client.get(f"/{code}/")
    assert response.status_code == 404
    assert response.json() == {
        "status_code": 404,
        "message": "Short code not found.",
        "detail": "Short code not found.",
    }
    assert not Click.objects.exists()


@pytest.mark.django_db
def test_expired_returns_410(client: Client) -> None:
    """An expired URL is gone; no click is saved."""
    url = _url(expires_at=timezone.now() + timedelta(seconds=1))
    expire(url)
    response = client.get("/abc1234/")
    assert response.status_code == 410
    assert response.json() == {
        "status_code": 410,
        "message": "This short URL has expired.",
        "detail": "This short URL has expired.",
    }
    assert not Click.objects.exists()


@pytest.mark.django_db
def test_admin_is_not_taken_as_a_short_code(client: Client) -> None:
    """``admin/`` still reaches the admin, not the redirect."""
    assert client.get("/admin/").status_code == 302
    assert "/admin/login/" in client.get("/admin/")["Location"]


@pytest.mark.django_db
def test_admin_page_loads(client: Client) -> None:
    """The admin redirects to its login page, which loads."""
    response = client.get("/admin/", follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].startswith("/admin/login/")
