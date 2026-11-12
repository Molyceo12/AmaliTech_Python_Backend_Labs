"""Find a short URL from the ``<short_code>`` part of the path."""

from typing import Any

from django.db.models import Q
from django.shortcuts import get_object_or_404

from shortener.models import ShortURL


def get_by_code_or_alias(view: Any) -> ShortURL:
    """One query for the short code or the alias; then the object permissions run."""
    value = view.kwargs["short_code"]
    url: ShortURL = get_object_or_404(
        view.get_queryset(), Q(short_code=value) | Q(custom_alias=value)
    )
    view.check_object_permissions(view.request, url)
    return url
