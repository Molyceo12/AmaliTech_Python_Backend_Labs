"""Helpers shared by the tests."""

from datetime import timedelta

from django.utils import timezone

from shortener.models import ShortURL


def expire(url: ShortURL) -> None:
    """Move ``url`` into the past, so it counts as expired.

    The database refuses ``expires_at`` before ``created_at``, so both move together.
    """
    ShortURL.objects.filter(pk=url.pk).update(
        expires_at=timezone.now() - timedelta(days=1),
        created_at=timezone.now() - timedelta(days=2),
    )
