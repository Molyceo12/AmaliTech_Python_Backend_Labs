"""Named, chainable queries for ``ShortURL``."""

from __future__ import annotations

from django.db import models
from django.utils import timezone


class ShortURLQuerySet(models.QuerySet):  # type: ignore[type-arg]
    """Queries used by the URL list (``?status=`` and ``?ordering=``)."""

    def active_urls(self) -> ShortURLQuerySet:
        """URLs that are switched on and not expired."""
        not_expired = models.Q(expires_at__isnull=True) | models.Q(
            expires_at__gt=timezone.now()
        )
        return self.filter(not_expired, is_active=True)

    def expired_urls(self) -> ShortURLQuerySet:
        """URLs whose expiry time has passed."""
        return self.filter(expires_at__lte=timezone.now())

    def popular_urls(self) -> ShortURLQuerySet:
        """Most clicked first; newest first on a tie."""
        return self.order_by("-click_count", "-created_at")
