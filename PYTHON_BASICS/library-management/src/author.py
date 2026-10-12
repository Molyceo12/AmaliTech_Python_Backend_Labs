"""Author data model for the Library Management System.

This module defines the Author class which represents a book author
with name, nationality, and birth year. It inherits from LibraryResource
to provide a common interface for serialization and display.
"""

from datetime import date
from uuid import uuid4

from library_resource import LibraryResource


class Author(LibraryResource):
    """Represents a book author."""

    def __init__(self, name, nationality, birth_year, author_id=None):
        if not name or not str(name).strip():
            raise ValueError("Author name cannot be empty")
        if nationality is not None and not str(nationality).strip():
            raise ValueError("Nationality cannot be blank if provided")
        if birth_year is not None:
            try:
                birth_year = int(birth_year)
            except (ValueError, TypeError):
                raise ValueError("Birth year must be a number")
            if birth_year < 1 or birth_year > date.today().year:
                raise ValueError(
                    f"Birth year must be between 1 and {date.today().year}"
                )
        super().__init__(name)
        self.author_id = author_id or str(uuid4())[:8]
        self.name = name.strip()
        self.nationality = nationality
        self.birth_year = birth_year

    def __str__(self):
        return (
            f"  Author : {self.name}\n"
            f"  Origin : {self.nationality or 'N/A'}\n"
            f"  Born   : {self.birth_year or 'N/A'}\n"
            f"  ID     : {self.author_id}"
        )

    def __repr__(self):
        return f"Author(name={self.name}, nationality={self.nationality}, birth_year={self.birth_year}, author_id={self.author_id})"

    def __eq__(self, other):
        if not isinstance(other, Author):
            return False
        return self.author_id == other.author_id

    def get_id(self) -> str:
        return self.author_id

    def display_info(self) -> str:
        return f"Author: {self.name} | Nationality: {self.nationality or 'N/A'} | Born: {self.birth_year or 'N/A'} | ID: {self.author_id}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "nationality": self.nationality,
            "birth_year": self.birth_year,
            "author_id": self.author_id,
        }

    @classmethod
    def from_dict(cls, data: dict):
        from borrower import _safe_int
        return cls(
            name=data["name"],
            nationality=data.get("nationality"),
            birth_year=_safe_int(data.get("birth_year")),
            author_id=data.get("author_id"),
        )
