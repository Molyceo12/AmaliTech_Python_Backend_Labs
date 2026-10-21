"""Tests for the ``re.sub()`` cleaning helpers."""

import pytest

from log_analyzer.patterns.cleaning import (
    mask_emails,
    normalize_whitespace,
    strip_query_string,
)


@pytest.mark.parametrize(
    ("url", "cleaned"),
    [
        ("/search?q=python", "/search"),
        ("/search?q=regex&page=2", "/search"),
        ("/about", "/about"),
    ],
)
def test_strip_query_string(url: str, cleaned: str) -> None:
    """Everything from ``?`` on is removed."""
    assert strip_query_string(url) == cleaned


def test_mask_emails_hides_every_address() -> None:
    """Each email becomes ``***@***``; other text stays."""
    assert mask_emails("to=ann@mail.com&cc=bo@x.org") == "to=***@***&cc=***@***"


def test_normalize_whitespace_collapses_and_trims() -> None:
    """Tabs, repeated spaces and the line break become single spaces."""
    assert normalize_whitespace("  GET\t /index.html   200 \n") == "GET /index.html 200"
