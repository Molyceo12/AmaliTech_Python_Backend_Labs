"""Helper functions for formatting text and numbers."""

SCREEN_WIDTH = 68


def format_currency(val: float, prefix: str = "RWF ") -> str:
    """Format a number into money format, for example RWF 1,000.00."""
    return f"{prefix}{val:,.2f}"


def divider(width: int = SCREEN_WIDTH, char: str = ":") -> str:
    """Make a solid border line out of the given character."""
    if width < 1:
        raise ValueError(f"width must be at least 1, got {width}.")
    return char * width


def format_header(heading: str, width: int = SCREEN_WIDTH) -> str:
    """Make a centered heading wrapped in double-colon border lines."""
    border = divider(width)
    inner = heading.center(width - 4)
    return f"{border}\n::{inner}::\n{border}"


def format_row(text: str, width: int = SCREEN_WIDTH) -> str:
    """Place a line of text between double-colon side borders."""
    inner = text.ljust(width - 6)
    return f":: {inner} ::"
