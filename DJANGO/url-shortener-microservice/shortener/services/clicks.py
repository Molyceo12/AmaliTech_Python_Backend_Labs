"""Record a visit to a short URL."""

from django.db import transaction
from django.db.models import F
from rest_framework.request import Request

from shortener.models import Click, ShortURL


@transaction.atomic
def record_click(short_url: ShortURL, request: Request) -> None:
    """Save a ``Click`` and add 1 to ``click_count``.

    The IP comes from ``REMOTE_ADDR`` only: ``X-Forwarded-For`` is sent by the
    client, so it can be faked. ``F()`` adds 1 in the database, so two clicks
    at the same moment both count. City and country stay null (no geo lookup).
    """
    Click.objects.create(
        url=short_url,
        ip_address=request.META.get("REMOTE_ADDR") or None,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        referrer=(request.META.get("HTTP_REFERER") or "")[:2048] or None,
    )
    ShortURL.objects.filter(pk=short_url.pk).update(click_count=F("click_count") + 1)
