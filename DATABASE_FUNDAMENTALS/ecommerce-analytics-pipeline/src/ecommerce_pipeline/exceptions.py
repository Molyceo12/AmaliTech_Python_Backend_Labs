"""Custom exceptions: every expected problem is an ``EcommerceError``."""


class EcommerceError(Exception):
    """Base class for all errors raised by the pipeline."""


class ConfigError(EcommerceError):
    """A ``.env`` value is missing or invalid."""


class LogSetupError(EcommerceError):
    """The log file cannot be created."""


class DatabaseConnectionError(EcommerceError):
    """PostgreSQL, Redis or MongoDB cannot be reached."""


class CustomerNotFoundError(EcommerceError):
    """An operation uses a customer id that does not exist."""


class ProductNotFoundError(EcommerceError):
    """An order uses a product id that does not exist."""


class DuplicateEmailError(EcommerceError):
    """A customer with this email already exists."""


class InsufficientStockError(EcommerceError):
    """An order asks for more units than are in stock."""
