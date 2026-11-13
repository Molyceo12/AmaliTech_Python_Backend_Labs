"""Rates with a number of minutes, e.g. ``5/3min``."""

import pytest

from url_shortener.throttles import ScopedMinutesThrottle


@pytest.mark.parametrize(
    ("rate", "expected"),
    [
        ("5/3min", (5, 180)),
        ("5/min", (5, 60)),
        ("20/2hour", (20, 7200)),
        (None, (None, None)),
    ],
)
def test_parse_rate(rate: str | None, expected: tuple[int | None, int | None]) -> None:
    """The count in front of the unit multiplies it; no count means 1."""
    assert ScopedMinutesThrottle().parse_rate(rate) == expected
