"""App configuration for the shortener app."""

from django.apps import AppConfig


class ShortenerConfig(AppConfig):
    """Registers the shortener app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shortener"
