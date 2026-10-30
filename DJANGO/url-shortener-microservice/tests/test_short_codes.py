"""Tests for the ``ShortURL`` model and the short code service."""

import pytest

from shortener.models import ShortURL
from shortener.services import short_codes


def test_codes_are_seven_letters_or_digits() -> None:
    """A new code has the default length and only letters and digits."""
    code = short_codes.generate_short_code()
    assert len(code) == short_codes.CODE_LENGTH
    assert code.isalnum()


@pytest.mark.django_db
def test_create_short_url_saves_the_url() -> None:
    """The URL is stored under a new code."""
    short_url = short_codes.create_short_url("https://example.com/a/long/path")
    saved = ShortURL.objects.get(short_code=short_url.short_code)
    assert saved.original_url == "https://example.com/a/long/path"
    assert str(saved) == f"{saved.short_code} -> https://example.com/a/long/path"


@pytest.mark.django_db
def test_a_taken_code_is_drawn_again(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the first code is already used, the next one is taken."""
    ShortURL.objects.create(original_url="https://example.com", short_code="taken")
    codes = iter(["taken", "fresh"])
    monkeypatch.setattr(short_codes, "generate_short_code", lambda: next(codes))
    assert short_codes.create_short_url("https://example.org").short_code == "fresh"
