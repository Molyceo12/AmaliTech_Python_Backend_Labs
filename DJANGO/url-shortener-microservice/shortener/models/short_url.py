"""The ``ShortURL`` model: one long URL and its short code."""

from django.conf import settings
from django.db import models

from shortener.models.managers import ShortURLQuerySet
from shortener.models.tag import Tag

SHORT_CODE_MAX_LENGTH = 10


class ShortURL(models.Model):
    """A long URL saved under a unique short code."""

    original_url = models.URLField(max_length=2048)
    # unique=True also gives the column an index, so lookups by code are fast.
    short_code = models.CharField(max_length=SHORT_CODE_MAX_LENGTH, unique=True)
    # null=True: many URLs have no alias, and unique allows many NULLs.
    custom_alias = models.CharField(max_length=50, unique=True, null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="short_urls",
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    favicon = models.URLField(max_length=2048, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name="short_urls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ShortURLQuerySet.as_manager()

    class Meta:
        """Newest short URLs first."""

        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["expires_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expires_at__isnull=True)
                | models.Q(expires_at__gt=models.F("created_at")),
                name="expires_after_created",
            )
        ]

    def __str__(self) -> str:
        """Show the code and where it points."""
        return f"{self.short_code} -> {self.original_url}"
