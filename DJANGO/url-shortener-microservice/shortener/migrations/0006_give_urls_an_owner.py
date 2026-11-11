"""Data migration: give every short URL without an owner to the seed user.

Runs before ``0007`` makes ``owner`` required. The seed user is made (with no
usable password) only if some URL needs it.
"""

from typing import Any

from django.contrib.auth.hashers import make_password
from django.db import migrations

SEED_EMAIL = "seed@example.com"


def give_urls_an_owner(apps: Any, schema_editor: Any) -> None:
    """Set ``owner`` to the seed user on every URL that has none."""
    ownerless = apps.get_model("shortener", "ShortURL").objects.filter(
        owner__isnull=True
    )
    if not ownerless.exists():
        return
    seed, _ = apps.get_model("accounts", "User").objects.get_or_create(
        email=SEED_EMAIL,
        defaults={"username": "seed", "password": make_password(None)},
    )
    ownerless.update(owner=seed)


class Migration(migrations.Migration):
    """Ownerless URLs → seed user (undo leaves them owned)."""

    dependencies = [
        ("accounts", "0001_initial"),
        ("shortener", "0005_click_fields_like_brief"),
    ]

    operations = [migrations.RunPython(give_urls_an_owner, migrations.RunPython.noop)]
