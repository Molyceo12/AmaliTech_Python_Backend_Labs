"""Tests for the IP, email and URL validation patterns."""

import pytest

from log_analyzer.patterns.validators import (
    find_all_ips,
    find_ip,
    is_valid_ip,
    is_valid_url,
)


@pytest.mark.parametrize(
    ("text", "valid"),
    [
        ("0.0.0.0", True),
        ("192.168.1.10", True),
        ("255.255.255.255", True),
        ("256.1.1.1", False),
        ("1.2.3", False),
        ("1.2.3.4.5", False),
        ("01.2.3.4", False),
        ("a.b.c.d", False),
        (" 1.2.3.4", False),
    ],
)
def test_is_valid_ip(text: str, valid: bool) -> None:
    """Exactly four octets, each from 0 to 255."""
    assert is_valid_ip(text) is valid


@pytest.mark.parametrize(
    ("text", "valid"),
    [
        ("https://example.com", True),
        ("http://www.example.org:8080/path?q=1", True),
        ("http://10.0.0.5/admin", True),
        ("ftp://example.com", False),
        ("https://", False),
        ("example.com", False),
        ("https://exa mple.com", False),
    ],
)
def test_is_valid_url(text: str, valid: bool) -> None:
    """``http``/``https`` scheme, a host, optional port and path."""
    assert is_valid_url(text) is valid


def test_find_ip_returns_the_first_address() -> None:
    """``search`` finds an address inside longer text."""
    assert find_ip("blocked 10.1.2.3 then 8.8.8.8") == "10.1.2.3"
    assert find_ip("no address here") is None


def test_find_all_ips_skips_invalid_addresses() -> None:
    """``findall`` returns every valid address, in order."""
    assert find_all_ips("10.1.2.3, 999.1.1.1, 8.8.8.8") == ["10.1.2.3", "8.8.8.8"]
