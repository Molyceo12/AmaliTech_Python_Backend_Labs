"""Abstract base class for all library resources.

This module defines the LibraryResource abstract base class that provides
a common interface for all library domain objects (Book, Author, Borrower).
It enforces implementation of serialization, display, identification, and
comparison methods across all subclasses.
"""

from abc import ABC, abstractmethod


class LibraryResource(ABC):
    """Abstract base class for all library resources."""

    def __init__(self, title):
        self.title = title

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize resource to a dictionary for persistence."""
        pass

    @abstractmethod
    def display_info(self) -> str:
        """Return a human-readable summary of the resource."""
        pass

    @abstractmethod
    def get_id(self) -> str:
        """Return a unique identifier for the resource."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Deserialize resource from a dictionary."""
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass