"""Tests for the database setting read from ``DATABASE_URL``."""

import importlib
from types import ModuleType

import pytest

POSTGRES = "postgres://shortener:secret@db:5432/shortener"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (None, {"ENGINE": "django.db.backends.sqlite3"}),
        (
            POSTGRES,
            {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "db",
                "PORT": 5432,
                "NAME": "shortener",
                "USER": "shortener",
                "PASSWORD": "secret",
            },
        ),
    ],
)
def test_database_comes_from_database_url(
    reload_base: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    url: str | None,
    expected: dict[str, object],
) -> None:
    """No URL: local ``db.sqlite3``. A ``postgres://`` URL is split into parts."""
    if url is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", url)
    importlib.reload(reload_base)
    database = reload_base.DATABASES["default"]
    assert {key: database[key] for key in expected} == expected
    if url is None:
        assert str(database["NAME"]).endswith("db.sqlite3")
