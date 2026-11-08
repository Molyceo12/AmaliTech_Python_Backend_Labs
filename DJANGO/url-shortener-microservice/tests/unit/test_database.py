"""Tests for the database setting read from ``DATABASE_URL``."""

import importlib
from types import ModuleType

import pytest


def test_no_database_url_uses_a_local_sqlite_file(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without ``DATABASE_URL`` the app uses ``db.sqlite3`` in the project."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(reload_base)
    database = reload_base.DATABASES["default"]
    assert database["ENGINE"] == "django.db.backends.sqlite3"
    assert str(database["NAME"]).endswith("db.sqlite3")


def test_postgres_url_sets_every_connection_value(
    reload_base: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ``postgres://`` URL is split into engine, host, port, name and user."""
    monkeypatch.setenv("DATABASE_URL", "postgres://shortener:secret@db:5432/shortener")
    importlib.reload(reload_base)
    database = reload_base.DATABASES["default"]
    assert database["ENGINE"] == "django.db.backends.postgresql"
    assert (database["HOST"], database["PORT"]) == ("db", 5432)
    assert (database["NAME"], database["USER"]) == ("shortener", "shortener")
    assert database["PASSWORD"] == "secret"
