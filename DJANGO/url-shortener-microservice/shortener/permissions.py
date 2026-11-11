"""Who may do what with a short URL."""

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

from accounts.models import User


class IsOwnerOrReadOnly(BasePermission):
    """Anyone logged in can read a URL; only its owner can change or delete it."""

    message = "You can only change your own short URLs."

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """GET / HEAD / OPTIONS pass; PUT / PATCH / DELETE need the owner."""
        return request.method in SAFE_METHODS or obj.owner_id == request.user.pk


class IsOwner(BasePermission):
    """Only the URL's owner, for every method."""

    message = "You can only see your own short URLs."

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """The logged-in user owns ``obj``."""
        return bool(obj.owner_id == request.user.pk)


class IsPremium(BasePermission):
    """Paid tiers only: Premium and Admin."""

    message = "Analytics are for Premium users."

    def has_permission(self, request: Request, view: Any) -> bool:
        """The user's tier is Premium or Admin."""
        return getattr(request.user, "tier", None) in {
            User.Tier.PREMIUM,
            User.Tier.ADMIN,
        }
