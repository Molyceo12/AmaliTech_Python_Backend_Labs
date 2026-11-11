"""``python manage.py seed_dev``: fill the dev database with seeders."""

from datetime import timedelta
from itertools import cycle, islice
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from shortener.models import Click, ShortURL, Tag

SEED_EMAIL = "seed@example.com"
TAGS = ["docs", "python", "news", "shopping"]

URLS: list[dict[str, Any]] = [
    {
        "short_code": "seedact",
        "original_url": "https://docs.djangoproject.com/en/5.2/",
        "title": "Django docs",
        "tags": ["docs", "python"],
        "clicks": 2,
    },
    {
        "short_code": "seedhot",
        "original_url": "https://www.python.org/",
        "title": "Python",
        "tags": ["python"],
        "clicks": 6,
    },
    {
        "short_code": "seedals",
        "original_url": "https://www.bbc.com/news",
        "custom_alias": "daily-news",
        "title": "News",
        "tags": ["news"],
        "clicks": 3,
    },
    {
        "short_code": "seedoff",
        "original_url": "https://www.example.com/shop",
        "title": "Old shop",
        "is_active": False,
        "tags": ["shopping"],
        "clicks": 1,
    },
    {
        "short_code": "seedold",
        "original_url": "https://www.example.com/sale",
        "title": "Past sale",
        "expired": True,
        "tags": ["shopping"],
        "clicks": 0,
    },
]

# Sample visitors, reused in turn. 203.0.113.x is a range kept for examples.
VISITORS = [
    ("203.0.113.10", "Kigali", "Rwanda", "Mozilla/5.0 (Windows NT 10.0)"),
    ("203.0.113.20", "Accra", "Ghana", "Mozilla/5.0 (iPhone)"),
    ("203.0.113.30", "Nairobi", "Kenya", "curl/8.5.0"),
]


class Command(BaseCommand):
    """Create one user, tags, URLs and clicks; running it again adds nothing."""

    help = "Fill the dev database with seeders (refused when DEBUG is off)."

    def handle(self, *args: Any, **options: Any) -> None:
        """Seed everything in one transaction, then print what was new."""
        if not settings.DEBUG:
            raise CommandError("seed_dev only runs with DEBUG=True.")
        with transaction.atomic():
            counts = self._seed()
        message = "Seeded {users} user, {tags} tags, {urls} URLs, {clicks} clicks."
        self.stdout.write(
            message.format(**counts) if any(counts.values()) else "Nothing new."
        )

    def _seed(self) -> dict[str, int]:
        """Create what is missing and count it."""
        user, user_created = User.objects.get_or_create(
            email=SEED_EMAIL,
            defaults={"username": "seed", "tier": User.Tier.PREMIUM},
        )
        if user_created:
            _set_password(user)
        tags = {name: Tag.objects.get_or_create(name=name) for name in TAGS}
        counts = {
            "users": int(user_created),
            "tags": sum(created for _, created in tags.values()),
            "urls": 0,
            "clicks": 0,
        }
        for data in URLS:
            url, created = _get_or_create_url(user, data)
            if created:
                url.tags.set(tags[name][0] for name in data["tags"])
                counts["urls"] += 1
                counts["clicks"] += _add_clicks(url, data["clicks"])
        return counts


def _set_password(user: User) -> None:
    """Password from ``.env``; without one the user exists but can't log in."""
    password = settings.SEED_USER_PASSWORD
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.save()


def _get_or_create_url(user: User, data: dict[str, Any]) -> tuple[ShortURL, bool]:
    """Find the URL by its code, or create it (expired ones moved into the past)."""
    now = timezone.now()
    url, created = ShortURL.objects.get_or_create(
        short_code=data["short_code"],
        defaults={
            "original_url": data["original_url"],
            "owner": user,
            "title": data["title"],
            "custom_alias": data.get("custom_alias"),
            "is_active": data.get("is_active", True),
            "click_count": data["clicks"],
            # The DB needs expires_at > created_at, so save a future expiry first.
            "expires_at": now + timedelta(hours=1) if data.get("expired") else None,
        },
    )
    if created and data.get("expired"):
        ShortURL.objects.filter(pk=url.pk).update(
            created_at=now - timedelta(days=30), expires_at=now - timedelta(days=1)
        )
    return url, created


def _add_clicks(url: ShortURL, number: int) -> int:
    """Save ``number`` clicks from the sample visitors."""
    clicks = [
        Click(
            url=url,
            ip_address=ip,
            city=city,
            country=country,
            user_agent=agent,
            referrer="https://www.google.com/",
        )
        for ip, city, country, agent in islice(cycle(VISITORS), number)
    ]
    Click.objects.bulk_create(clicks)
    return len(clicks)
