import json
from datetime import date, timedelta
from pathlib import Path

from author import Author
from book import Book, Categories, EBook, AudioBook, LibraryResource

DATA_FILE = Path("data/library.json")
DATA_FILE.parent.mkdir(exist_ok=True)


class Borrower(LibraryResource):
    """Represents a library member/borrower."""

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

    def __str__(self):
        phone_str = f" | Phone: {self.phone}" if self.phone else ""
        return f"  [Borrower] ID: {self.member_id} | Name: {self.name} | Email: {self.email}{phone_str}"

    def __repr__(self):
        return f"Borrower(member_id={self.member_id}, name={self.name}, email={self.email}, phone={self.phone})"

    def __eq__(self, other):
        if not isinstance(other, Borrower):
            return False
        return self.member_id == other.member_id


class Borrow(LibraryResource):
    """Represents a book borrowing record."""

    def __init__(
        self,
        member_id,
        book_title,
        borrow_date=None,
        return_date=None,
        due_date=None,
    ):
        if not member_id or not str(member_id).strip():
            raise ValueError("Member ID cannot be empty")
        if not book_title or not str(book_title).strip():
            raise ValueError("Book title cannot be empty")
        super().__init__(member_id)
        self.member_id = member_id.strip()
        self.book_title = book_title.strip()
        self.borrow_date = borrow_date or date.today()
        self.due_date = due_date or self.borrow_date + timedelta(days=14)
        self.return_date = return_date

    def is_overdue(self):
        """Return True if the book is past its due date and not yet returned."""
        return self.return_date is None and date.today() > self.due_date

    def mark_returned(self):
        """Mark this borrow record as returned today."""
        self.return_date = date.today()

    def __str__(self):
        status = (
            "Returned"
            if self.return_date
            else ("Overdue" if self.is_overdue() else "Borrowed")
        )
        return (
            f"  [Borrow] Member ID: {self.member_id} | Book: {self.book_title} "
            f"| Borrowed: {self.borrow_date} | Due: {self.due_date} "
            f"| Returned: {self.return_date or 'N/A'} | Status: {status}"
        )

    def __repr__(self):
        return (
            f"Borrow(member_id={self.member_id}, book_title={self.book_title}, "
            f"borrow_date={self.borrow_date}, return_date={self.return_date}, due_date={self.due_date})"
        )

    def __eq__(self, other):
        if not isinstance(other, Borrow):
            return False
        return (
            self.member_id == other.member_id
            and self.book_title == other.book_title
            and self.borrow_date == other.borrow_date
            and self.return_date == other.return_date
        )


# ── helpers ──────────────────────────────────────────────────────────────────


def _safe_int(value):
    """Return int(value) or None if value is not a valid integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_date(value):
    """Return a date from an ISO string, or None if missing/invalid."""
    if value and value != "None":
        return date.fromisoformat(value)
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
    # Support both old format (book_type) and new format (book_class)
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
    }


def _deserialize_borrower(data):
    """Convert a dict from JSON back to a Borrower object."""
    return Borrower(
        member_id=data["member_id"],
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
    )


def _serialize_borrow(borrow):
    """Convert a Borrow object to a JSON-serializable dict."""
    return {
        "member_id": borrow.member_id,
        "book_title": borrow.book_title,
        "borrow_date": str(borrow.borrow_date),
        "return_date": str(borrow.return_date) if borrow.return_date else None,
        "due_date": str(borrow.due_date),
    }


def _deserialize_borrow(data):
    """Convert a dict from JSON back to a Borrow object."""
    borrow_date = _parse_date(data.get("borrow_date")) or date.today()
    due_date = _parse_date(data.get("due_date")) or borrow_date + timedelta(days=14)
    # Support old format with borrower_name
    member_id = data.get("member_id") or data.get("borrower_name")
    return Borrow(
        member_id=member_id,
        book_title=data["book_title"],
        borrow_date=borrow_date,
        due_date=due_date,
        return_date=_parse_date(data.get("return_date")),
    )


# ── public I/O ────────────────────────────────────────────────────────────────


def load_data():
    """Load books, authors, borrowers, and borrows from library.json."""
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return [], [], [], []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    books = [_deserialize_book(b) for b in data.get("books", [])]
    authors = [_deserialize_author(a) for a in data.get("authors", [])]
    borrowers = [_deserialize_borrower(b) for b in data.get("borrowers", [])]
    borrows = [_deserialize_borrow(b) for b in data.get("borrows", [])]
    return books, authors, borrowers, borrows


def save_data(books, authors, borrowers, borrows):
    """Save books, authors, borrowers, and borrows to library.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "books": [_serialize_book(b) for b in books],
                "authors": [_serialize_author(a) for a in authors],
                "borrowers": [_serialize_borrower(b) for b in borrowers],
                "borrows": [_serialize_borrow(b) for b in borrows],
            },
            f,
            indent=4,
        )
