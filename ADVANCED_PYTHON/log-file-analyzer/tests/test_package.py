"""Smoke test: the package installs and imports."""

import log_analyzer


def test_package_has_a_version() -> None:
    """The package exposes its version."""
    assert log_analyzer.__version__ == "0.1.0"
