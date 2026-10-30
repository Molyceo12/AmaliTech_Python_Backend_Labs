"""Shared test fixtures."""

import importlib
from collections.abc import Iterator
from types import ModuleType

import pytest

from url_shortener.settings import base


@pytest.fixture(name="reload_base")
def fixture_reload_base(monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """Give the ``base`` settings module to reload with a fake environment.

    Afterwards the fake environment is undone and ``base`` reloaded, so later
    tests see the real values.
    """
    yield base
    monkeypatch.undo()
    importlib.reload(base)
