"""Data cleaning with ``re.sub()``."""

import re

from log_analyzer.patterns.validators import EMAIL_PATTERN

QUERY_STRING = re.compile(r"\?.*$")  # "?" and everything after it
WHITESPACE = re.compile(r"\s+")  # runs of spaces, tabs and line breaks
EMAIL_MASK = "***@***"


def strip_query_string(url: str) -> str:
    """Remove the query string from a URL path.

    Example: ``"/search?q=python"`` → ``"/search"``.
    """
    return QUERY_STRING.sub("", url)


def mask_emails(text: str) -> str:
    """Replace every email address with ``***@***`` (keeps logs anonymous).

    Example: ``"user=ann@mail.com"`` → ``"user=***@***"``.
    """
    return EMAIL_PATTERN.sub(EMAIL_MASK, text)


def normalize_whitespace(line: str) -> str:
    """Collapse tabs and repeated spaces into one space and trim the ends.

    Example: ``"  GET\\t /  "`` → ``"GET /"``.
    """
    return WHITESPACE.sub(" ", line).strip()
