from datetime import date
from enum import Enum

from library_resource import LibraryResource


class Categories(Enum):
    FICTION = "Fiction"
    NON_FICTION = "Non-Fiction"
    SCIENCE_FICTION = "Science Fiction"
    FANTASY = "Fantasy"
    MYSTERY = "Mystery"
    THRILLER = "Thriller"
    ROMANCE = "Romance"
    BIOGRAPHY = "Biography"
    HISTORY = "History"
    CHILDREN = "Children"
    POETRY = "Poetry"
    COOKBOOKS = "Cookbooks"
    SELF_HELP = "Self-Help"
    TECHNOLOGY = "Technology"
    SCIENCE = "Science"
    GENERAL = "General"


class Book(LibraryResource):
    """Represents a book in the library."""

    def __init__(
        self,
        title,
        author,
        isbn,
        year,
        category: Categories = Categories.GENERAL,
        copies=1,
    ):
        self._title = None
        self._isbn = None
        self._category = None
        self._author = None
        self._year = None
        self._copies = None

        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.category = category
        self.copies = copies

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        if (
            not value.replace(" ", "")
            .replace("-", "")
            .replace("'", "")
            .replace(":", "")
            .replace(",", "")
            .replace(".", "")
            .isalnum()
        ):
            raise ValueError(
                "Title must contain only letters, numbers, spaces, or common punctuation"
            )
        self._title = value.strip()

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, value):
        if not value or not str(value).strip():
            raise ValueError("ISBN cannot be empty")
        self._isbn = str(value).strip()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if isinstance(value, Categories):
            self._category = value
        elif isinstance(value, str):
            self._category = Categories(value)
        else:
            raise ValueError("Invalid category")

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        from author import Author

        if not isinstance(value, Author):
            raise ValueError("author must be an Author object")
        self._author = value

    @property
    def year(self):
        """Publication year — positive integer not in the future."""
        return self._year

    @year.setter
    def year(self, value):
        if value is None:
            self._year = None
            return
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValueError("Publication year must be a number")
        if value < 1 or value > date.today().year:
            raise ValueError(
                f"Publication year must be between 1 and {date.today().year}"
            )
        self._year = value

    @property
    def copies(self):
        """Total number of copies — must be a positive integer."""
        return self._copies

    @copies.setter
    def copies(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValueError("Copies must be a number")
        if value < 1:
            raise ValueError("Copies must be at least 1")
        self._copies = value

    def __str__(self):
        return (
            f"  [Book] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| Copies: {self.copies}"
        )

    def __repr__(self):
        return (
            f"Book(title={self.title}, author={self.author}, isbn={self.isbn}, "
            f"year={self._year}, category={self.category.value})"
        )

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.isbn == other.isbn

    def get_id(self) -> str:
        return self.isbn

    def display_info(self) -> str:
        return (
            f"[Book] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| Copies: {self.copies}"
        )

    def to_dict(self) -> dict:
        base = {
            "title": self.title,
            "isbn": self.isbn,
            "category": self.category.value,
            "year": self.year,
            "copies": self.copies,
            "author": {
                "name": self.author.name,
                "nationality": self.author.nationality,
                "birth_year": self.author.birth_year,
            },
        }
        return base

    @classmethod
    def from_dict(cls, data: dict):
        from author import Author
        from borrower import _safe_int
        book_class = data.get("book_class", "Book")
        if book_class == "EBook":
            return EBook.from_dict(data)
        elif book_class == "AudioBook":
            return AudioBook.from_dict(data)
        a = data["author"]
        author = Author(a["name"], a.get("nationality"), _safe_int(a.get("birth_year")))
        return cls(
            title=data["title"],
            author=author,
            isbn=data["isbn"],
            category=Categories(data.get("category", "General")),
            year=_safe_int(data.get("year")),
            copies=data.get("copies", 1),
        )


class EBook(Book):
    """Represents an electronic book."""

    def __init__(
        self,
        title,
        author,
        isbn,
        year,
        file_size_mb,
        category: Categories = Categories.GENERAL,
        copies=1,
    ):
        super().__init__(title, author, isbn, year, category, copies)
        self._file_size_mb = None
        self.file_size_mb = file_size_mb

    @property
    def file_size_mb(self):
        return self._file_size_mb

    @file_size_mb.setter
    def file_size_mb(self, value):
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValueError("File size must be a number")
        if value <= 0:
            raise ValueError("File size must be positive")
        self._file_size_mb = value

    def __str__(self):
        return (
            f"  [EBook] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| File Size: {self.file_size_mb} MB | Copies: {self.copies}"
        )

    def __repr__(self):
        return (
            f"EBook(title={self.title}, author={self.author}, isbn={self.isbn}, "
            f"year={self._year}, category={self.category.value}, file_size_mb={self.file_size_mb})"
        )

    def get_id(self) -> str:
        return self.isbn

    def display_info(self) -> str:
        return (
            f"[EBook] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| File Size: {self.file_size_mb} MB | Copies: {self.copies}"
        )

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["book_class"] = "EBook"
        base["file_size_mb"] = self.file_size_mb
        return base

    @classmethod
    def from_dict(cls, data: dict):
        from author import Author
        from borrower import _safe_int
        a = data["author"]
        author = Author(a["name"], a.get("nationality"), _safe_int(a.get("birth_year")))
        return cls(
            title=data["title"],
            author=author,
            isbn=data["isbn"],
            year=_safe_int(data.get("year")),
            file_size_mb=data.get("file_size_mb", 0),
            category=Categories(data.get("category", "General")),
            copies=data.get("copies", 1),
        )


class AudioBook(Book):
    """Represents an audio book."""

    def __init__(
        self,
        title,
        author,
        isbn,
        year,
        duration_minutes,
        category: Categories = Categories.GENERAL,
        copies=1,
    ):
        super().__init__(title, author, isbn, year, category, copies)
        self._duration_minutes = None
        self.duration_minutes = duration_minutes

    @property
    def duration_minutes(self):
        return self._duration_minutes

    @duration_minutes.setter
    def duration_minutes(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValueError("Duration must be a number")
        if value <= 0:
            raise ValueError("Duration must be positive")
        self._duration_minutes = value

    def __str__(self):
        return (
            f"  [AudioBook] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| Duration: {self.duration_minutes} min | Copies: {self.copies}"
        )

    def __repr__(self):
        return (
            f"AudioBook(title={self.title}, author={self.author}, isbn={self.isbn}, "
            f"year={self._year}, category={self.category.value}, duration_minutes={self.duration_minutes})"
        )

    def get_id(self) -> str:
        return self.isbn

    def display_info(self) -> str:
        return (
            f"[AudioBook] ISBN: {self.isbn} | Title: {self.title} | Author: {self.author.name} "
            f"| Year: {self._year or 'N/A'} | Category: {self.category.value} "
            f"| Duration: {self.duration_minutes} min | Copies: {self.copies}"
        )

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["book_class"] = "AudioBook"
        base["duration_minutes"] = self.duration_minutes
        return base

    @classmethod
    def from_dict(cls, data: dict):
        from author import Author
        from borrower import _safe_int
        a = data["author"]
        author = Author(a["name"], a.get("nationality"), _safe_int(a.get("birth_year")))
        return cls(
            title=data["title"],
            author=author,
            isbn=data["isbn"],
            year=_safe_int(data.get("year")),
            duration_minutes=data.get("duration_minutes", 0),
            category=Categories(data.get("category", "General")),
            copies=data.get("copies", 1),
        )
