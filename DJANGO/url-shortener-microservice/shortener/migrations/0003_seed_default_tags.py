"""Data migration: the default tags every database starts with."""

from typing import Any

from django.db import migrations

DEFAULT_TAGS = ["marketing", "social"]


def add_tags(apps: Any, schema_editor: Any) -> None:
    """Create the default tags (skip any that already exist)."""
    tag_model = apps.get_model("shortener", "Tag")
    for name in DEFAULT_TAGS:
        tag_model.objects.get_or_create(name=name)


def remove_tags(apps: Any, schema_editor: Any) -> None:
    """Undo: delete the default tags."""
    apps.get_model("shortener", "Tag").objects.filter(name__in=DEFAULT_TAGS).delete()


class Migration(migrations.Migration):
    """Seed ``marketing`` and ``social``."""

    dependencies = [("shortener", "0002_url_fields_tag_click")]

    operations = [migrations.RunPython(add_tags, remove_tags)]
