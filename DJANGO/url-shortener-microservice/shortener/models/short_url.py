"""The ``ShortURL`` model: one long URL and its short code."""

from django.db import models

SHORT_CODE_MAX_LENGTH = 10


class ShortURL(models.Model):
    """A long URL saved under a unique short code."""

    original_url = models.URLField(max_length=2048)
    # unique=True also gives the column an index, so lookups by code are fast.
    short_code = models.CharField(max_length=SHORT_CODE_MAX_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Newest short URLs first."""

        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Show the code and where it points."""
        return f"{self.short_code} -> {self.original_url}"
