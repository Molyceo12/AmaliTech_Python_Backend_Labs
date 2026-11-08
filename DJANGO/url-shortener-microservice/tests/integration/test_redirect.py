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
def test_code_or_alias_redirects_and_records_a_click(client: Client, path: str) -> None:
    """Code or alias → 302; one ``Click`` is saved and ``click_count`` goes up."""
    url = _url(custom_alias="docs")
    response = client.get(path, HTTP_USER_AGENT="pytest", HTTP_REFERER="https://a.io/")
    assert response.status_code == 302
    assert response["Location"] == "https://example.com/long"
    click = Click.objects.get(url=url)
    assert (click.ip_address, click.user_agent, click.referrer) == (
        "127.0.0.1",
        "pytest",
        "https://a.io/",
    )
    url.refresh_from_db()
    assert url.click_count == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("case", "status", "text"),
    [
        ("unknown", 404, "Short code not found."),
        ("inactive", 404, "Short code not found."),
        ("expired", 410, "This short URL has expired."),
    ],
)
def test_unknown_inactive_or_expired_is_refused(
    client: Client, case: str, status: int, text: str
) -> None:
    """Unknown or switched off → 404, expired → 410; no click is saved."""
    if case == "inactive":
        _url(is_active=False)
    elif case == "expired":
        expire(_url(expires_at=timezone.now() + timedelta(seconds=1)))
    response = client.get("/abc1234/")
    assert response.status_code == status
    assert response.json() == {"status_code": status, "message": text, "detail": text}
    assert not Click.objects.exists()


@pytest.mark.django_db
def test_admin_is_not_taken_as_a_short_code(client: Client) -> None:
    """``admin/`` reaches the admin login page, not the redirect."""
    response = client.get("/admin/", follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].startswith("/admin/login/")
