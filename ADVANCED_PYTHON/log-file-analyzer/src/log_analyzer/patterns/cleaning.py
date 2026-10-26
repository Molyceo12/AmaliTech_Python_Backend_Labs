"""Data cleaning with ``re.sub()``."""

import re

from log_analyzer.patterns.validators import is_valid_email

WHITESPACE = re.compile(r"\s+")  # runs of spaces, tabs and line breaks
EMAIL_MASK = "***@***"
# Anything shaped like name@host inside a URL; is_valid_email decides.
EMAIL_CANDIDATE = re.compile(r"[^\s/?&=@]+@[^\s/?&=@]+")


def _mask_if_valid(match: re.Match[str]) -> str:
    """``re.sub`` callback: mask the candidate only if it is a valid email."""
    candidate = match.group()
    return EMAIL_MASK if is_valid_email(candidate) else candidate


def mask_emails(text: str) -> str:
    """Replace every valid email address with ``***@***`` (keeps logs anonymous).

    Each ``name@host`` candidate is checked with ``is_valid_email``; text that
    only looks like an email (e.g. ``"user@host"``) is left as it is.

    Example: ``"user=ann@mail.com"`` → ``"user=***@***"``.
    """
    return EMAIL_CANDIDATE.sub(_mask_if_valid, text)


def normalize_whitespace(line: str) -> str:
    """Collapse tabs and repeated spaces into one space and trim the ends.

    Example: ``"  GET\\t /  "`` → ``"GET /"``.
    """
    return WHITESPACE.sub(" ", line).strip()
