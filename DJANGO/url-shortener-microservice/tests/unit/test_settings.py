"""Tests for the project settings and its entry points."""

import importlib
import logging
import sys
from types import ModuleType

import decouple
import pytest
from django.conf import settings


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
    monkeypatch.setenv("SECRET_KEY", "from-env")
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com,api.example.com")
    importlib.reload(reload_base)
    assert reload_base.SECRET_KEY == "from-env"
    assert reload_base.ALLOWED_HOSTS == ["example.com", "api.example.com"]


def test_missing_secret_key_stops_the_app(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no ``SECRET_KEY`` anywhere, loading the settings fails."""
    monkeypatch.setattr(decouple, "config", decouple.Config(decouple.RepositoryEmpty()))
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(decouple.UndefinedValueError, match="SECRET_KEY"):
        importlib.reload(reload_base)


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
