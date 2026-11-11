"""Tests for the ``ShortURL`` model and the short code service."""

import pytest

from shortener.models import ShortURL
from shortener.services import short_codes
from tests.helpers import get_me, make_url


@pytest.mark.django_db
def test_create_short_url_saves_under_a_new_code() -> None:
    """The URL is stored under a 7-character letters-and-digits code."""
    code = short_codes.generate_short_code()
    assert (len(code), code.isalnum()) == (short_codes.CODE_LENGTH, True)
    short_url = short_codes.create_short_url(
        "https://example.com/a/long/path", owner=get_me()
    )
    saved = ShortURL.objects.get(short_code=short_url.short_code)
    assert saved.original_url == "https://example.com/a/long/path"
    assert str(saved) == f"{saved.short_code} -> https://example.com/a/long/path"


@pytest.mark.django_db
def test_a_taken_code_is_drawn_again(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the first code is already used, the next one is taken."""
    make_url("taken")
    codes = iter(["taken", "fresh"])
    monkeypatch.setattr(short_codes, "generate_short_code", lambda: next(codes))
    assert (
        short_codes.create_short_url("https://example.org", owner=get_me()).short_code
        == "fresh"
    )
