"""Tests on the sample log files in ``data/``."""

from log_analyzer.parsing import parse_line
from tests.helpers import DATA


def test_access_log_has_more_than_1000_lines(access_lines: list[str]) -> None:
    """The lab asks for sample logs with 1000+ lines."""
    assert len(access_lines) >= 1000


def test_every_sample_line_parses(access_lines: list[str]) -> None:
    """The generated logs contain only valid combined-format lines."""
    second = (DATA / "access_2.log").read_text(encoding="utf-8").splitlines()
    assert all(parse_line(line) is not None for line in access_lines + second)


def test_malformed_log_mixes_good_and_bad_lines() -> None:
    """``malformed.log`` has 4 valid lines out of 10."""
    lines = (DATA / "malformed.log").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 10
    assert sum(parse_line(line) is not None for line in lines) == 4
