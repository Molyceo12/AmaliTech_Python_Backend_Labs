import json
from datetime import date, timedelta
from pathlib import Path

from author import Author
from book import Book, Categories, EBook, AudioBook, LibraryResource

DATA_FILE = Path("data/library.json")
DATA_FILE.parent.mkdir(exist_ok=True)


class Borrower(LibraryResource):
    """Represents a library member/borrower with their borrowing history."""

    def __init__(self, member_id, name, email, phone=None):
        if not member_id or not str(member_id).strip():
            raise ValueError("Member ID cannot be empty")
        if not name or not str(name).strip():
            raise ValueError("Name cannot be empty")
        if not email or not str(email).strip():
            raise ValueError("Email cannot be empty")
        super().__init__(name)
        self.member_id = str(member_id).strip()
        self.name = name.strip()
        self.email = email.strip()
        self.phone = phone.strip() if phone else None
        self._borrowed = []  # list of dicts: {book_title, borrow_date, due_date, return_date}

    def borrow_book(self, book_title):
        """Borrow a book - creates a borrow record."""
        if self._has_active_borrow(book_title):
            raise ValueError(f"Already borrowed: {book_title}")
        record = {
            "book_title": book_title,
            "borrow_date": date.today(),
            "due_date": date.today() + timedelta(days=14),
            "return_date": None,
        }
        self._borrowed.append(record)
        return record

    def return_book(self, book_title):
        """Return a borrowed book."""
        for record in self._borrowed:
            if record["book_title"] == book_title and record["return_date"] is None:
                record["return_date"] = date.today()
                return record
        return None

    def _has_active_borrow(self, book_title):
        return any(r["book_title"] == book_title and r["return_date"] is None for r in self._borrowed)

    def get_active_borrows(self):
        """Return list of unreturned borrows."""
        return [r for r in self._borrowed if r["return_date"] is None]

    def get_borrow_history(self):
        """Return all borrow records."""
        return self._borrowed

    def has_overdue_books(self):
        """Check if borrower has any overdue books."""
        today = date.today()
        return any(r["return_date"] is None and today > r["due_date"] for r in self._borrowed)

    def get_overdue_borrows(self):
        """Return overdue borrows."""
        today = date.today()
        return [r for r in self._borrowed if r["return_date"] is None and today > r["due_date"]]

    def __str__(self):
        phone_str = f" | Phone: {self.phone}" if self.phone else ""
        active = len(self.get_active_borrows())
        return f"  [Borrower] ID: {self.member_id} | Name: {self.name} | Email: {self.email}{phone_str} | Active borrows: {active}"

    def __repr__(self):
        return f"Borrower(member_id={self.member_id}, name={self.name}, email={self.email}, phone={self.phone})"

    def __eq__(self, other):
        if not isinstance(other, Borrower):
            return False
        return self.member_id == other.member_id


# ── helpers ──────────────────────────────────────────────────────────────────


def _safe_int(value):
    """Return int(value) or None if value is not a valid integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# ── serialization ─────────────────────────────────────────────────────────────


def _serialize_book(book):
    """Convert a Book object to a JSON-serializable dict."""
    base = {
        "title": book.title,
        "isbn": book.isbn,
        "category": book.category.value,
        "year": book.year,
        "copies": book.copies,
        "author": {
            "name": book.author.name,
            "nationality": book.author.nationality,
            "birth_year": book.author.birth_year,
        },
    }
    if isinstance(book, EBook):
        base["book_class"] = "EBook"
        base["file_size_mb"] = book.file_size_mb
    elif isinstance(book, AudioBook):
        base["book_class"] = "AudioBook"
        base["duration_minutes"] = book.duration_minutes
    else:
        base["book_class"] = "Book"
    return base


def _deserialize_book(data):
    """Convert a dict from JSON back to a Book object."""
    a = data["author"]
    author = Author(a["name"], a.get("nationality"), _safe_int(a.get("birth_year")))
    book_class = data.get("book_class") or ("Book" if data.get("book_type") else "Book")
    base_args = {
        "title": data["title"],
        "author": author,
        "isbn": data["isbn"],
        "category": Categories(data.get("category", "General")),
        "year": _safe_int(data.get("year")),
        "copies": data.get("copies", 1),
    }
    if book_class == "EBook":
        return EBook(**base_args, file_size_mb=data.get("file_size_mb", 0))
    elif book_class == "AudioBook":
        return AudioBook(**base_args, duration_minutes=data.get("duration_minutes", 0))
    else:
        return Book(**base_args)


def _serialize_author(author):
    """Convert an Author object to a JSON-serializable dict."""
    return {
        "name": author.name,
        "nationality": author.nationality,
        "birth_year": author.birth_year,
    }


def _deserialize_author(data):
    """Convert a dict from JSON back to an Author object."""
    return Author(
        name=data["name"],
        nationality=data.get("nationality"),
        birth_year=_safe_int(data.get("birth_year")),
    )


def _serialize_borrower(borrower):
    """Convert a Borrower object to a JSON-serializable dict."""
    return {
        "member_id": borrower.member_id,
        "name": borrower.name,
        "email": borrower.email,
        "phone": borrower.phone,
        "borrowed": [
            {
                "book_title": r["book_title"],
                "borrow_date": str(r["borrow_date"]),
                "due_date": str(r["due_date"]),
                "return_date": str(r["return_date"]) if r["return_date"] else None,
            }
            for r in borrower._borrowed
        ],
    }


def _deserialize_borrower(data):
    """Convert a dict from JSON back to a Borrower object."""
    borrower = Borrower(
        member_id=data["member_id"],
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
    )
    # Load borrow history
    for record_data in data.get("borrowed", []):
        record = {
            "book_title": record_data["book_title"],
            "borrow_date": date.fromisoformat(record_data["borrow_date"]) if record_data.get("borrow_date") else date.today(),
            "due_date": date.fromisoformat(record_data["due_date"]) if record_data.get("due_date") else date.today() + timedelta(days=14),
            "return_date": date.fromisoformat(record_data["return_date"]) if record_data.get("return_date") else None,
        }
        borrower._borrowed.append(record)
    return borrower


# ── public I/O ────────────────────────────────────────────────────────────────


def load_data():
    """Load books, authors, and borrowers from library.json."""
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return [], [], []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    books = [_deserialize_book(b) for b in data.get("books", [])]
    authors = [_deserialize_author(a) for a in data.get("authors", [])]
    borrowers = [_deserialize_borrower(b) for b in data.get("borrowers", [])]
    return books, authors, borrowers


def save_data(books, authors, borrowers):
    """Save books, authors, and borrowers to library.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "books": [_serialize_book(b) for b in books],
                "authors": [_serialize_author(a) for a in authors],
                "borrowers": [_serialize_borrower(b) for b in borrowers],
            },
            f,
            indent=4,
        )