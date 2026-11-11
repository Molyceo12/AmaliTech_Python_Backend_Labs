"""The ``Click`` model: one visit to a short URL."""

from django.db import models


class Click(models.Model):
    """A single redirect of a short URL, with where it came from."""

    url = models.ForeignKey(
        "shortener.ShortURL", on_delete=models.CASCADE, related_name="clicks"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)  # noqa: DJ001
    country = models.CharField(max_length=100, null=True, blank=True)  # noqa: DJ001
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=2048, null=True, blank=True)  # noqa: DJ001

    class Meta:
        """Newest clicks first."""

        ordering = ["-clicked_at"]

    def __str__(self) -> str:
        """Show which URL was clicked and when."""
        return f"{self.url_id} at {self.clicked_at}"
