"""Tests for ``ShortURL``, ``Tag``, ``Click`` and the ``ShortURL`` queries."""

from datetime import timedelta
from importlib import import_module

import pytest
from django.apps import apps
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import User
from shortener.models import Click, ShortURL, Tag
from tests.helpers import expire

pytestmark = pytest.mark.django_db


def _url(code: str = "abc1234", **fields: object) -> ShortURL:
    """Save a short URL with the given code."""
    return ShortURL.objects.create(
        original_url="https://example.com/", short_code=code, **fields
    )


def test_new_url_defaults() -> None:
    """Active, no clicks, no owner, no expiry, no alias."""
    url = _url()
    assert (url.is_active, url.click_count) == (True, 0)
    assert (url.owner, url.expires_at, url.custom_alias) == (None, None, None)


def test_custom_alias_is_unique_but_many_urls_can_have_none() -> None:
    """Two ``None`` aliases are fine; the same alias twice is not."""
    _url("aaa1111")
    _url("bbb2222")
    _url("ccc3333", custom_alias="docs")
    with pytest.raises(IntegrityError):
        _url("ddd4444", custom_alias="docs")


def test_expiry_must_be_after_creation() -> None:
    """The database refuses an ``expires_at`` in the past at creation."""
    with pytest.raises(IntegrityError):
        _url(expires_at=timezone.now() - timedelta(days=1))


def test_tag_is_saved_lowercase_trimmed_and_unique() -> None:
    """``" Python "`` becomes ``python``; ``PYTHON`` then clashes."""
    assert Tag.objects.create(name=" Python ").name == "python"
    with pytest.raises(IntegrityError):
        Tag.objects.create(name="PYTHON")


def test_url_has_many_tags_and_tag_has_many_urls() -> None:
    """Many-to-many works both ways."""
    tag = Tag.objects.create(name="docs")
    first, second = _url("aaa1111"), _url("bbb2222")
    first.tags.add(tag)
    second.tags.add(tag)
    assert set(tag.short_urls.all()) == {first, second}


def test_deleting_url_deletes_its_clicks() -> None:
    """``Click`` uses ``CASCADE``."""
    url = _url()
    Click.objects.create(short_url=url, ip_address="203.0.113.5")
    url.delete()
    assert not Click.objects.exists()


def test_deleting_user_deletes_their_urls() -> None:
    """``owner`` uses ``CASCADE``."""
    user = User.objects.create_user(email="ana@example.com", username="ana")
    _url(owner=user)
    user.delete()
    assert not ShortURL.objects.exists()


def test_active_and_expired_urls() -> None:
    """Active skips switched-off and expired URLs; expired returns only expired."""
    live = _url("live111")
    _url("off1111", is_active=False)
    old = _url("old1111", expires_at=timezone.now() + timedelta(seconds=1))
    expire(old)
    assert list(ShortURL.objects.active_urls()) == [live]
    assert list(ShortURL.objects.expired_urls()) == [old]


def test_popular_urls_most_clicked_first_and_chainable() -> None:
    """Ordered by ``click_count``; chaining a filter keeps working."""
    user = User.objects.create_user(email="ana@example.com", username="ana")
    low = _url("low1111", click_count=1, owner=user)
    high = _url("high111", click_count=9, owner=user)
    _url("other11", click_count=50)
    popular = ShortURL.objects.popular_urls().filter(owner=user)
    assert list(popular) == [high, low]


def test_str_of_each_model() -> None:
    """``__str__`` shows something readable."""
    url = _url()
    click = Click.objects.create(short_url=url)
    assert str(url) == "abc1234 -> https://example.com/"
    assert str(Tag.objects.create(name="docs")) == "docs"
    assert str(click).startswith(f"{url.pk} at ")


def test_default_tags_come_from_the_data_migration() -> None:
    """Migration ``0003`` seeds ``marketing`` and ``social`` in every database."""
    names = set(Tag.objects.values_list("name", flat=True))
    assert {"marketing", "social"} <= names


def test_default_tags_migration_can_be_undone() -> None:
    """The reverse step removes the default tags and nothing else."""
    migration = import_module("shortener.migrations.0003_seed_default_tags")
    Tag.objects.create(name="docs")
    migration.remove_tags(apps, None)
    assert list(Tag.objects.values_list("name", flat=True)) == ["docs"]
    migration.add_tags(apps, None)
    assert Tag.objects.count() == 3
