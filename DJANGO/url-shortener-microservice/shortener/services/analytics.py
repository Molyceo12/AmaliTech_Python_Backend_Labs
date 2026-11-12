"""Click numbers for one short URL, counted by the database."""

from dataclasses import dataclass
from typing import Any

from django.db.models import Count
from django.db.models.functions import TruncDate

from shortener.models import ShortURL


@dataclass(frozen=True)
class UrlAnalytics:
    """Total clicks, clicks per day (oldest first) and clicks per country."""

    short_code: str
    total_clicks: int
    clicks_per_day: list[dict[str, Any]]
    clicks_by_country: list[dict[str, Any]]


def url_analytics(url: ShortURL) -> UrlAnalytics:
    """Count the clicks of ``url`` in SQL: one ``GROUP BY`` per list."""
    per_day = list(
        url.clicks.annotate(day=TruncDate("clicked_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    return UrlAnalytics(
        short_code=url.short_code,
        total_clicks=sum(row["total"] for row in per_day),
        clicks_per_day=per_day,
        clicks_by_country=url.clicks_by_country(),
    )
