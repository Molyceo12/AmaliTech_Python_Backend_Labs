"""``?status=`` and ``?ordering=`` for the URL list."""

from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from shortener.models import ShortURL

# ?status= picks one of the custom queries on ShortURLQuerySet.
STATUS_QUERIES = {"active": "active_urls", "expired": "expired_urls"}
ORDERINGS = ["popular"]


def apply_filters(queryset: Any, params: Any) -> QuerySet[ShortURL]:
    """Apply ``?status=active|expired`` and ``?ordering=popular``; else 400."""
    status = params.get("status")
    if status is not None:
        if status not in STATUS_QUERIES:
            raise ValidationError({"status": ["Use active or expired."]})
        queryset = getattr(queryset, STATUS_QUERIES[status])()
    ordering = params.get("ordering")
    if ordering is not None:
        if ordering not in ORDERINGS:
            raise ValidationError({"ordering": ["Use popular."]})
        queryset = queryset.popular_urls()
    return queryset  # type: ignore[no-any-return]
