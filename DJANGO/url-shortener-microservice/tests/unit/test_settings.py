"""Tests for the project settings and its entry points."""

import importlib
import logging
import sys
from types import ModuleType

import decouple
import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def test_apps_are_installed_and_debug_is_dev_only() -> None:
    """DRF and both apps are registered; ``dev`` turns debug on, ``prod`` off."""
    for app in ("rest_framework", "shortener", "accounts"):
        assert app in settings.INSTALLED_APPS
    dev = importlib.import_module("url_shortener.settings.dev")
    prod = importlib.import_module("url_shortener.settings.prod")
    assert dev.DEBUG is True
    assert prod.DEBUG is False


def test_values_come_from_the_environment(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Environment variables set the secret key and the allowed hosts."""
    monkeypatch.setenv("SECRET_KEY", "from-env-" + "x" * 32)
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com,api.example.com")
    importlib.reload(reload_base)
    assert reload_base.SECRET_KEY == "from-env-" + "x" * 32
    assert reload_base.ALLOWED_HOSTS == ["example.com", "api.example.com"]


def test_missing_secret_key_stops_the_app(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no ``SECRET_KEY`` anywhere, loading the settings fails."""
    monkeypatch.setattr(decouple, "config", decouple.Config(decouple.RepositoryEmpty()))
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(decouple.UndefinedValueError, match="SECRET_KEY"):
        importlib.reload(reload_base)


def test_short_secret_key_stops_the_app(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``SECRET_KEY`` signs the JWTs: under 32 characters the app refuses to start."""
    monkeypatch.setenv("SECRET_KEY", "x" * 31)
    with pytest.raises(ImproperlyConfigured, match="at least 32 characters"):
        importlib.reload(reload_base)


HTTPS_OFF = {
    "SECURE_SSL_REDIRECT": "False",
    "SECURE_COOKIES": "False",
    "SECURE_HSTS_SECONDS": "0",
}
HTTPS_ON = {
    "SECURE_SSL_REDIRECT": "True",
    "SECURE_COOKIES": "True",
    "SECURE_HSTS_SECONDS": "3600",
}


@pytest.mark.parametrize(("env", "on"), [(HTTPS_OFF, False), (HTTPS_ON, True)])
def test_prod_https_settings_come_from_env(
    monkeypatch: pytest.MonkeyPatch, env: dict[str, str], on: bool
) -> None:
    """Off for local Docker (plain HTTP); ``.env`` turns them on behind HTTPS."""
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    prod = importlib.reload(importlib.import_module("url_shortener.settings.prod"))
    assert prod.SECURE_SSL_REDIRECT is on
    assert prod.SESSION_COOKIE_SECURE is prod.CSRF_COOKIE_SECURE is on
    assert (prod.SECURE_HSTS_SECONDS > 0) is on


def test_entry_points_work(monkeypatch: pytest.MonkeyPatch) -> None:
    """WSGI and ASGI expose ``application``; ``manage.py check`` runs."""
    for name in ("url_shortener.wsgi", "url_shortener.asgi"):
        assert callable(importlib.import_module(name).application)
    manage = importlib.import_module("manage")
    monkeypatch.setattr(sys, "argv", ["manage.py", "check"])
    manage.main()


def test_logs_are_also_saved_to_a_file() -> None:
    """Every logger writes to ``logs/app.log`` too, not only the console."""
    logging.getLogger("tests").warning("log file check")
    log_file = settings.LOG_DIR / "app.log"
    assert "WARNING tests: log file check" in log_file.read_text(encoding="utf-8")
