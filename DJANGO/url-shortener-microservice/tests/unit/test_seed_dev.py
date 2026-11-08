"""Tests for ``python manage.py seed_dev``."""

from io import StringIO
from typing import Any

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Count

from accounts.models import User
from shortener.models import Click, ShortURL, Tag

pytestmark = pytest.mark.django_db


@pytest.fixture(name="dev")
def fixture_dev(settings: Any) -> Any:
    """Run as in development: ``DEBUG`` on, no seed password."""
    settings.DEBUG = True
    settings.SEED_USER_PASSWORD = ""
    return settings


def _seed() -> str:
    """Run the command and return what it printed."""
    out = StringIO()
    call_command("seed_dev", stdout=out)
    return out.getvalue().strip()


@pytest.mark.usefixtures("dev")
def test_creates_user_tags_urls_and_clicks() -> None:
    """One run fills every table, covers every case and says what it made."""
    assert _seed() == "Seeded 1 user, 4 tags, 5 URLs, 12 clicks."
    user = User.objects.get(email="seed@example.com")
    assert user.tier == User.Tier.PREMIUM
    # 2 default tags from the migration + 4 seed tags.
    assert (Tag.objects.count(), Click.objects.count()) == (6, 12)
    assert ShortURL.objects.filter(owner=user).count() == 5
    # Every case: active, popular, alias, switched off, expired.
    assert ShortURL.objects.active_urls().count() == 3
    assert list(
        ShortURL.objects.expired_urls().values_list("short_code", flat=True)
    ) == ["seedold"]
    assert ShortURL.objects.popular_urls().first().short_code == "seedhot"  # type: ignore[union-attr]
    assert ShortURL.objects.get(custom_alias="daily-news").short_code == "seedals"
    assert ShortURL.objects.get(short_code="seedoff").is_active is False
    # click_count equals the saved Click rows of each URL.
    for url in ShortURL.objects.annotate(total=Count("clicks")):
        assert url.click_count == url.total


@pytest.mark.usefixtures("dev")
def test_second_run_adds_nothing() -> None:
    """``get_or_create`` makes the command safe to repeat."""
    _seed()
    assert _seed() == "Nothing new."
    assert (ShortURL.objects.count(), Click.objects.count()) == (5, 12)


def test_refuses_when_debug_is_off(settings: Any) -> None:
    """Never seed a production database."""
    settings.DEBUG = False
    with pytest.raises(CommandError, match="DEBUG=True"):
        _seed()
    assert not User.objects.exists()


@pytest.mark.parametrize("password", ["test-only-seed-pass", ""])
def test_password_comes_from_env_or_is_unusable(dev: Any, password: str) -> None:
    """``SEED_USER_PASSWORD`` is the password; without it, nobody can log in."""
    dev.SEED_USER_PASSWORD = password
    _seed()
    user = User.objects.get()
    if password:
        assert user.check_password(password)
    else:
        assert not user.has_usable_password()
