"""The ``Tag`` model: a label that groups short URLs."""

from typing import Any

from django.db import models


class Tag(models.Model):
    """A unique label, saved lowercase and trimmed."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        """Tags in alphabetical order."""

        ordering = ["name"]

    def __str__(self) -> str:
        """Show the tag name."""
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Store ``" Python "`` as ``"python"`` so tags don't repeat."""
        self.name = self.name.strip().lower()
        super().save(*args, **kwargs)
