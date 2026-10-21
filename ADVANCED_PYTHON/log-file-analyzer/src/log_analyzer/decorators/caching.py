"""``@cache``: remember results with ``functools.lru_cache``."""

from collections.abc import Callable
from functools import lru_cache
from typing import TYPE_CHECKING, TypeVar, overload

if TYPE_CHECKING:
    from functools import _lru_cache_wrapper

R = TypeVar("R")
DEFAULT_MAXSIZE = 1024  # results kept before the least recently used is dropped


@overload
def cache(
    func: Callable[..., R], *, maxsize: int | None = DEFAULT_MAXSIZE
) -> "_lru_cache_wrapper[R]": ...


@overload
def cache(
    func: None = None, *, maxsize: int | None = DEFAULT_MAXSIZE
) -> Callable[[Callable[..., R]], "_lru_cache_wrapper[R]"]: ...


def cache(
    func: Callable[..., R] | None = None, *, maxsize: int | None = DEFAULT_MAXSIZE
) -> "_lru_cache_wrapper[R] | Callable[[Callable[..., R]], _lru_cache_wrapper[R]]":
    """Cache a function's results by its arguments (``functools.lru_cache``).

    Works with or without brackets::

        @cache
        def parse_timestamp(text): ...

        @cache(maxsize=256)
        def lookup(ip): ...

    The cached function keeps ``cache_info()`` and ``cache_clear()``.
    Arguments must be hashable (strings, numbers, tuples).
    """
    if func is None:
        return lru_cache(maxsize=maxsize)
    return lru_cache(maxsize=maxsize)(func)
