"""The ``Click`` model: one visit to a short URL."""

from django.db import models


class Click(models.Model):
    """A single redirect of a short URL, with where it came from."""

    short_url = models.ForeignKey(
        "shortener.ShortURL", on_delete=models.CASCADE, related_name="clicks"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=2048, blank=True)

    class Meta:
        """Newest clicks first; indexed for "clicks of one URL over time"."""

        ordering = ["-clicked_at"]
        indexes = [models.Index(fields=["short_url", "clicked_at"])]

    def __str__(self) -> str:
        """Show which URL was clicked and when."""
        return f"{self.short_url_id} at {self.clicked_at}"
