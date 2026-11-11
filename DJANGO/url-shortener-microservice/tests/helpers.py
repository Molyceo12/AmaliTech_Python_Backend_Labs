"""Helpers shared by the tests."""

from datetime import timedelta
from typing import Any

from django.utils import timezone

from accounts.models import User
from shortener.models import ShortURL

ME = "me@example.com"


def get_me() -> User:
    """The test user ``me``, made on first use."""
    user = User.objects.filter(email=ME).first()
    return user or User.objects.create_user(email=ME, username="me")


def make_url(code: str = "abc1234", **fields: Any) -> ShortURL:
    """Save a short URL with the given code, owned by ``me`` unless told."""
    fields.setdefault("original_url", "https://example.com/")
    if "owner" not in fields:
        fields["owner"] = get_me()
    return ShortURL.objects.create(short_code=code, **fields)


def expire(url: ShortURL) -> None:
    """Move ``url`` into the past, so it counts as expired.

    The database refuses ``expires_at`` before ``created_at``, so both move together.
    """
    ShortURL.objects.filter(pk=url.pk).update(
        expires_at=timezone.now() - timedelta(days=1),
        created_at=timezone.now() - timedelta(days=2),
    )
