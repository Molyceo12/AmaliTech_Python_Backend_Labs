"""``@timer``: measure how long a function takes."""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)
LAST_SECONDS = "last_seconds"  # attribute the wrapper keeps the last time in


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """Log how long each call takes and remember the last time.

    The time is logged at ``INFO`` (``"run took 0.042 s"``) and kept on the
    wrapper, so callers can read it with ``last_duration(func)``.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            seconds = time.perf_counter() - start
            setattr(wrapper, LAST_SECONDS, seconds)
            logger.info("%s took %.3f s", func.__name__, seconds)

    setattr(wrapper, LAST_SECONDS, 0.0)
    return wrapper


def last_duration(func: Callable[..., object]) -> float:
    """Return the seconds the last call of a ``@timer`` function took.

    Works for bound methods too: their attributes come from the function.
    Returns ``0.0`` for a function that is not timed or not called yet.
    """
    seconds: float = getattr(func, LAST_SECONDS, 0.0)
    return seconds
