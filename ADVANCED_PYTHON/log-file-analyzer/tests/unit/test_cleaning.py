"""Tests for the ``re.sub()`` cleaning helpers."""

from log_analyzer.patterns.cleaning import mask_emails, normalize_whitespace


def test_mask_emails_hides_every_address() -> None:
    """Each email becomes ``***@***``; other text stays."""
    assert mask_emails("to=ann@mail.com&cc=bo@x.org") == "to=***@***&cc=***@***"


def test_mask_emails_keeps_text_that_is_not_a_valid_email() -> None:
    """``is_valid_email`` rejects ``user@host`` (no top-level domain), so it stays."""
    assert mask_emails("/login?user=admin@localhost") == "/login?user=admin@localhost"


def test_normalize_whitespace_collapses_and_trims() -> None:
    """Tabs, repeated spaces and the line break become single spaces."""
    assert normalize_whitespace("  GET\t /index.html   200 \n") == "GET /index.html 200"
