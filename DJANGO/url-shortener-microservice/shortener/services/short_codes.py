"""Create short URLs with random, unique short codes."""

import secrets
import string

from shortener.models import ShortURL

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7  # 62**7 is about 3.5 trillion codes


def generate_short_code(length: int = CODE_LENGTH) -> str:
    """Return a random code of letters and digits."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_short_url(original_url: str) -> ShortURL:
    """Save ``original_url`` under a new code, drawing again on a clash."""
    code = generate_short_code()
    while ShortURL.objects.filter(short_code=code).exists():
        code = generate_short_code()
    return ShortURL.objects.create(original_url=original_url, short_code=code)
