"""Report sections in a fixed order with ``OrderedDict``."""

from collections import OrderedDict
from collections.abc import Iterable


def ordered_sections(
    sections: Iterable[tuple[str, object]],
) -> OrderedDict[str, object]:
    """Build report sections in exactly the order they are given.

    Args:
        sections: ``(name, value)`` pairs in the order they should appear.

    Returns:
        An ``OrderedDict`` keeping that order.

    Raises:
        ValueError: If a section name appears twice.
    """
    ordered: OrderedDict[str, object] = OrderedDict()
    for name, value in sections:
        if name in ordered:
            raise ValueError(f"Duplicate report section: {name}")
        ordered[name] = value
    return ordered
