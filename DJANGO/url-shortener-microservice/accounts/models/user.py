"""The ``User`` model: Django's user, logged in by email, with a tier."""

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A user who logs in with email; ``tier`` sets their limits (Module 7)."""

    # TextChoices is str + Enum, so pylint counts many parents; that's Django's design.
    class Tier(models.TextChoices):  # pylint: disable=too-many-ancestors
        """Business tier. ``admin`` gives no admin rights: ``is_staff`` does."""

        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.FREE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Lowercase the email and keep ``is_premium`` in step with ``tier``."""
        self.email = self.email.lower()
        self.is_premium = self.tier == self.Tier.PREMIUM
        super().save(*args, **kwargs)
