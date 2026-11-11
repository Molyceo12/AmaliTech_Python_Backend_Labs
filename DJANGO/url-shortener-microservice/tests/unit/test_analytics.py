"""Tests for ``url_analytics``."""

from datetime import timedelta

import pytest
from django.utils import timezone

from shortener.models import Click
from shortener.services.analytics import url_analytics
from tests.helpers import make_url

pytestmark = pytest.mark.django_db


def test_counts_clicks_per_day_and_per_country() -> None:
    """2 clicks yesterday, 1 today → 2 day rows, oldest first; countries grouped."""
    url = make_url()
    for country in ["Rwanda", "Rwanda", "Ghana"]:
        Click.objects.create(url=url, country=country)
    yesterday = timezone.now() - timedelta(days=1)
    Click.objects.filter(country="Rwanda").update(clicked_at=yesterday)

    numbers = url_analytics(url)

    assert (numbers.short_code, numbers.total_clicks) == ("abc1234", 3)
    assert numbers.clicks_per_day == [
        {"day": yesterday.date(), "total": 2},
        {"day": timezone.now().date(), "total": 1},
    ]
    assert numbers.clicks_by_country == [
        {"country": "Rwanda", "total": 2},
        {"country": "Ghana", "total": 1},
    ]


def test_no_clicks_gives_zero_and_empty_lists() -> None:
    """A URL nobody opened yet."""
    numbers = url_analytics(make_url())
    assert numbers.total_clicks == 0
    assert numbers.clicks_per_day == numbers.clicks_by_country == []
