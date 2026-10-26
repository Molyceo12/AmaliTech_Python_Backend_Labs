"""Validation patterns for IP addresses, emails and URLs.

``fullmatch`` is used for validation, so the whole text must fit the pattern;
``search`` and ``findall`` find addresses inside longer text.
"""

import re

# One octet: 250–255, 200–249, 100–199 or 0–99 (no leading zeros like "01").
_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"

IP_PATTERN = re.compile(rf"\b{_OCTET}(?:\.{_OCTET}){{3}}\b")

EMAIL_PATTERN = re.compile(
    r"""
    [A-Za-z0-9._%+-]+          # name: letters, digits and . _ % + -
    @
    (?:[A-Za-z0-9-]+\.)+       # one or more domain labels, e.g. "mail."
    [A-Za-z]{2,}               # top-level domain, e.g. "com"
    """,
    re.VERBOSE,
)

URL_PATTERN = re.compile(
    r"""
    https?://                  # scheme: http or https
    (?:
        (?:[A-Za-z0-9-]+\.)+   # host labels, e.g. "www.example."
        [A-Za-z]{2,}           # top-level domain
    |
        \d{1,3}(?:\.\d{1,3}){3}  # or an IPv4 host, e.g. "10.0.0.5"
    )
    (?::\d{1,5})?              # optional port, e.g. ":8080"
    (?:/[^\s]*)?               # optional path and query string
    """,
    re.VERBOSE,
)


def is_valid_ip(text: str) -> bool:
    """Return whether ``text`` is exactly one IPv4 address (each part 0–255)."""
    return IP_PATTERN.fullmatch(text) is not None


def is_valid_url(text: str) -> bool:
    """Return whether ``text`` is exactly one http(s) URL."""
    return URL_PATTERN.fullmatch(text) is not None


def find_ip(text: str) -> str | None:
    """Return the first IPv4 address found anywhere in ``text``, or ``None``."""
    match = IP_PATTERN.search(text)
    return match.group() if match else None


def find_all_ips(text: str) -> list[str]:
    """Return every IPv4 address found in ``text``, in order."""
    return IP_PATTERN.findall(text)
