"""Tests for the ``:`` table printer."""

from decimal import Decimal

import pytest

from ecommerce_pipeline.display import TABLE_WIDTH, format_table, print_table


def test_every_table_has_the_same_width() -> None:
    """Small and large tables are both ``TABLE_WIDTH`` characters wide."""
    small = format_table(["id"], [[1]])
    large = format_table(["a", "b", "c"], [["x" * 30, "y" * 30, "z" * 20]])
    for table in (small, large):
        assert {len(line) for line in table.splitlines()} == {TABLE_WIDTH}


def test_table_aligns_text_left_and_numbers_right() -> None:
    """Text columns align left, number columns right."""
    lines = format_table(["name", "price"], [["Shirt", Decimal("15.00")]])
    row = lines.splitlines()[3]
    assert row.startswith(": Shirt ")
    assert row.endswith(" 15.00 :")


def test_long_text_wraps_and_keeps_the_width() -> None:
    """A cell too long for one line wraps; no text is lost, the width stays."""
    text = "word " * 40
    lines = format_table(["id", "message"], [[1, text]]).splitlines()
    assert {len(line) for line in lines} == {TABLE_WIDTH}
    assert len(lines) > 5
    assert " ".join(" ".join(lines).replace(":", " ").split()).count("word") == 40


def test_empty_table_shows_only_the_headers() -> None:
    """With no rows the header sits between two rules."""
    lines = format_table(["id"], []).splitlines()
    assert len(lines) == 3
    assert lines[1].startswith(": id ")


def test_print_table_prints_the_title_first(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The title goes on the line above the table."""
    print_table("Products", ["id"], [[1]])
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "Products"
    assert lines[1] == ":" * TABLE_WIDTH
