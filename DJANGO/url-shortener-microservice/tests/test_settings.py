"""Tests for the project settings and its entry points."""

import importlib
import sys
from collections.abc import Iterator
from types import ModuleType

import decouple
import pytest
from django.conf import settings
from django.test import Client

from url_shortener.settings import base


@pytest.fixture(name="reload_base")
def fixture_reload_base(monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """Give ``base``; afterwards undo the fake environment and reload it."""
    yield base
    monkeypatch.undo()
    importlib.reload(base)


def test_apps_are_installed() -> None:
    """DRF and both project apps are registered."""
    for app in ("rest_framework", "shortener", "accounts"):
        assert app in settings.INSTALLED_APPS


def test_dev_shows_debug_pages_and_prod_does_not() -> None:
    """``dev`` turns debug on; ``prod`` keeps it off."""
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


def test_wsgi_and_asgi_expose_an_application() -> None:
    """Gunicorn and async servers find ``application`` in both modules."""
    for name in ("url_shortener.wsgi", "url_shortener.asgi"):
        assert callable(importlib.import_module(name).application)


def test_manage_py_runs_a_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """``manage.py check`` runs without errors."""
    manage = importlib.import_module("manage")
    monkeypatch.setattr(sys, "argv", ["manage.py", "check"])
    manage.main()


@pytest.mark.django_db
def test_admin_page_loads(client: Client) -> None:
    """The admin redirects to its login page, which loads."""
    response = client.get("/admin/", follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0].startswith("/admin/login/")
