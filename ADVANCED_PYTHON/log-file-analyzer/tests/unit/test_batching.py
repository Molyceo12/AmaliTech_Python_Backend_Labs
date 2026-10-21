"""Tests for the ``Batches`` custom iterator."""

import pytest

from log_analyzer.readers import Batches


def test_batches_have_the_given_size() -> None:
    """Full batches first; the last one holds what is left."""
    assert list(Batches(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]


def test_exact_multiple_has_no_empty_batch() -> None:
    """No empty batch at the end."""
    assert list(Batches(range(4), 2)) == [[0, 1], [2, 3]]


def test_empty_input_gives_no_batches() -> None:
    """Nothing in, nothing out."""
    assert not list(Batches([], 5))


def test_works_on_a_one_time_generator() -> None:
    """A generator is read once, batch by batch."""
    numbers = (n for n in range(5))
    assert list(Batches(numbers, 2)) == [[0, 1], [2, 3], [4]]


def test_is_its_own_iterator() -> None:
    """``iter()`` returns the same object, and ``next`` gives a batch."""
    batches = Batches("abc", 2)
    assert iter(batches) is batches
    assert next(batches) == ["a", "b"]
    assert next(batches) == ["c"]
    with pytest.raises(StopIteration):
        next(batches)


@pytest.mark.parametrize("size", [0, -1])
def test_size_must_be_at_least_one(size: int) -> None:
    """A batch needs room for one item."""
    with pytest.raises(ValueError, match="at least 1"):
        Batches([1, 2], size)
