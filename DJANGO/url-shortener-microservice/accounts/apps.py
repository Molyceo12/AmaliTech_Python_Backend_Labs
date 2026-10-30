"""App configuration for the accounts app."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Registers the accounts app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
