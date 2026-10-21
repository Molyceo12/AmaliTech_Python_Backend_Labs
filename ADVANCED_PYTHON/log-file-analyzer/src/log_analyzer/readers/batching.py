"""A custom iterator that hands out items in fixed-size batches."""

from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Generic, TypeVar

T = TypeVar("T")


class Batches(Generic[T]):
    """Iterate over ``items`` in lists of ``size`` (the last one may be shorter).

    Only one batch is in memory at a time, so a huge stream of log lines can
    be processed piece by piece::

        for batch in Batches(read_lines("access.log"), 500):
            ...
    """

    def __init__(self, items: Iterable[T], size: int) -> None:
        """Prepare the batches.

        Args:
            items: Any iterable, including a one-time generator.
            size: How many items each batch holds.

        Raises:
            ValueError: If ``size`` is less than 1.
        """
        if size < 1:
            raise ValueError("batch size must be at least 1")
        self._items: Iterator[T] = iter(items)
        self.size = size

    def __iter__(self) -> "Batches[T]":
        """An iterator returns itself from ``iter()``."""
        return self

    def __next__(self) -> list[T]:
        """Return the next batch.

        Raises:
            StopIteration: When there are no items left.
        """
        batch = list(islice(self._items, self.size))
        if not batch:
            raise StopIteration
        return batch
