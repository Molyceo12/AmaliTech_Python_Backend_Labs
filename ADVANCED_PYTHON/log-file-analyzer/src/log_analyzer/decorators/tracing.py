"""``@log_call``: trace when a function is called and what it returns.

Named ``tracing`` (not ``logging``) so it never hides the standard module.
"""

import logging
import reprlib
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)
_short = reprlib.Repr(maxstring=40, maxother=40, maxlist=4)  # keeps log lines short


def log_call(func: Callable[P, R]) -> Callable[P, R]:
    """Log each call with its arguments and the value it returns (``DEBUG``).

    Long arguments are shortened with ``reprlib``, e.g. ``['a.log', ...]``.
    Exceptions are logged and raised again unchanged.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        shown = [_short.repr(arg) for arg in args]
        shown += [f"{name}={_short.repr(value)}" for name, value in kwargs.items()]
        logger.debug("Calling %s(%s)", func.__name__, ", ".join(shown))
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.debug("%s raised an exception", func.__name__)
            raise
        logger.debug("%s returned %s", func.__name__, _short.repr(result))
        return result

    return wrapper
