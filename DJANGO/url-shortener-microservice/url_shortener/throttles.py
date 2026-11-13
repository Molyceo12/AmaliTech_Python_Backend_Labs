"""Per-view rate limits whose period can be more than one unit, e.g. ``"5/3min"``."""

import string

from rest_framework.throttling import ScopedRateThrottle

SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class ScopedMinutesThrottle(ScopedRateThrottle):
    """DRF's scoped throttle; ``5/3min`` means 5 calls per 180 seconds."""

    def parse_rate(self, rate: str | None) -> tuple[int | None, int | None]:
        """``"5/3min"`` → ``(5, 180)``; ``"5/min"`` → ``(5, 60)``."""
        if rate is None:
            return (None, None)
        num, period = rate.split("/")
        unit = period.lstrip(string.digits)
        count = int(period.removesuffix(unit) or 1)
        return int(num), count * SECONDS[unit[0]]
