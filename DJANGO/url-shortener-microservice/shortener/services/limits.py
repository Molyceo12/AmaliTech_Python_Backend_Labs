"""Tier rules: paid tiers, active URL limit, and who may use an alias."""

from typing import Any

from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from shortener.models import ShortURL

FREE_ACTIVE_LIMIT = 10


def has_paid_tier(user: Any) -> bool:
    """Premium and Admin get the paid features; anonymous users have no tier."""
    return getattr(user, "tier", None) in {User.Tier.PREMIUM, User.Tier.ADMIN}


def check_active_limit(user: User) -> None:
    """A Free user who already has 10 active URLs can't make another one active."""
    if user.tier != User.Tier.FREE:
        return
    active = ShortURL.objects.filter(owner=user).active_urls().count()
    if active >= FREE_ACTIVE_LIMIT:
        raise PermissionDenied(f"Free plan: at most {FREE_ACTIVE_LIMIT} active URLs.")


def check_alias_allowed(user: User) -> None:
    """Custom aliases are a paid feature."""
    if user.tier == User.Tier.FREE:
        raise PermissionDenied("Custom aliases are for Premium users.")
