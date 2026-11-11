"""Create short URLs with random, unique short codes, and set their tags."""

import secrets
import string
from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.db.models import Q

from shortener.models import ShortURL, Tag

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7  # 62**7 is about 3.5 trillion codes


def generate_short_code(length: int = CODE_LENGTH) -> str:
    """Return a random code of letters and digits."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def _is_taken(code: str) -> bool:
    """A code can't match another URL's short code or custom alias."""
    return ShortURL.objects.filter(Q(short_code=code) | Q(custom_alias=code)).exists()


@transaction.atomic
def create_short_url(
    original_url: str,
    *,
    owner: Any,
    tags: Iterable[str] = (),
    **details: Any,
) -> ShortURL:
    """Save ``original_url`` under a new code, drawing again on a clash.

    ``details`` are optional model fields: ``custom_alias``, ``expires_at``,
    ``title``, ``description``, ``is_active``.
    """
    code = generate_short_code()
    while _is_taken(code):
        code = generate_short_code()
    short_url = ShortURL.objects.create(
        original_url=original_url, short_code=code, owner=owner, **details
    )
    set_tags(short_url, tags)
    return short_url


def set_tags(short_url: ShortURL, names: Iterable[str]) -> None:
    """Replace the URL's tags; a name that doesn't exist yet becomes a new tag."""
    tags = [Tag.objects.get_or_create(name=name.strip().lower())[0] for name in names]
    short_url.tags.set(tags)
