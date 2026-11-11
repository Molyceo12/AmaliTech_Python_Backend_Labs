"""Who may do what with a short URL."""

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request


class IsOwnerOrReadOnly(BasePermission):
    """Anyone logged in can read a URL; only its owner can change or delete it."""

    message = "You can only change your own short URLs."

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """GET / HEAD / OPTIONS pass; PUT / PATCH / DELETE need the owner."""
        return request.method in SAFE_METHODS or obj.owner_id == request.user.pk
