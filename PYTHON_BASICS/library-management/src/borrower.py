import json
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path

from author import Author
from book import Book, Categories, EBook, AudioBook, LibraryResource

DATA_FILE = Path("data/library.json")
DATA_FILE.parent.mkdir(exist_ok=True)


@dataclass
class BorrowRecord:
    """Represents a single book borrowing transaction."""
    book_title: str
    borrow_date: date
    due_date: date
    return_date: date = None

    def is_overdue(self):
        return self.return_date is None and date.today() > self.due_date

    def mark_returned(self):
        self.return_date = date.today()

    def to_dict(self):
        return {
            "book_title": self.book_title,
            "borrow_date": str(self.borrow_date),
            "due_date": str(self.due_date),
            "return_date": str(self.return_date) if self.return_date else None,
        }

    @classmethod
    def from_dict(cls, data):
        borrow_date = date.fromisoformat(data["borrow_date"]) if data.get("borrow_date") else date.today()
        due_date = date.fromisoformat(data["due_date"]) if data.get("due_date") else borrow_date + timedelta(days=14)
        return_date = date.fromisoformat(data["return_date"]) if data.get("return_date") else None
        return cls(
            book_title=data["book_title"],
            borrow_date=borrow_date,
            due_date=due_date,
            return_date=return_date,
        )


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
        self.borrowed_books = []  # list of BorrowRecord

    def borrow_book(self, book_title):
        """Create a new borrow record for a book."""
        record = BorrowRecord(
            book_title=book_title,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14),
        )
        self.borrowed_books.append(record)
        return record

    def return_book(self, book_title):
        """Mark a borrowed book as returned."""
        for record in self.borrowed_books:
            if record.book_title == book_title and record.return_date is None:
                record.mark_returned()
                return record
        return None

    def get_active_borrows(self):
        """Return list of unreturned borrow records."""
        return [r for r in self.borrowed_books if r.return_date is None]

    def get_borrow_history(self):
        """Return all borrow records."""
        return self.borrowed_books

    def has_overdue_books(self):
        """Check if borrower has any overdue books."""
        return any(r.is_overdue() for r in self.borrowed_books)

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
        "borrowed_books": [r.to_dict() for r in borrower.borrowed_books],
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
    for record_data in data.get("borrowed_books", []):
        borrower.borrowed_books.append(BorrowRecord.from_dict(record_data))
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