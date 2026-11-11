"""``?status=``, ``?ordering=`` and ``?tag=`` for the URL list."""

from typing import Any

from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from shortener.models import ShortURL

# ?status= picks one of the custom queries on ShortURLQuerySet.
STATUS_QUERIES = {"active": "active_urls", "expired": "expired_urls"}
ORDERINGS = ["popular"]


def apply_filters(queryset: Any, params: Any) -> QuerySet[ShortURL]:
    """Apply ``?status=active|expired``, ``?ordering=popular`` and ``?tag=<name>``.

    A wrong status or ordering → 400.
    """
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
    tag = params.get("tag")
    if tag:
        # Tag names are saved lowercase, so any case matches.
        queryset = queryset.filter(tags__name=tag.strip().lower())
    return queryset  # type: ignore[no-any-return]
