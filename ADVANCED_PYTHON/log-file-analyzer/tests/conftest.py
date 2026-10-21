"""Shared pytest fixtures."""

import pytest

from tests.helpers import DATA


@pytest.fixture(name="access_lines")
def fixture_access_lines() -> list[str]:
    """Return every line of the large sample log ``data/access.log``."""
    return (DATA / "access.log").read_text(encoding="utf-8").splitlines()
