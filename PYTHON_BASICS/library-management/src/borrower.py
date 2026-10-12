import json
from datetime import date, timedelta
from pathlib import Path

from author import Author
from book import Book, Categories, EBook, AudioBook, LibraryResource

DATA_FILE = Path(__file__).parent / "data" / "library.json"
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
        self._borrowed = []  # list of dicts: {isbn, borrow_date, due_date, return_date}

    def borrow_book(self, isbn):
        """Borrow a book - creates a borrow record."""
        if self._has_active_borrow(isbn):
            raise ValueError(f"Already borrowed: {isbn}")
        record = {
            "isbn": isbn,
            "borrow_date": date.today(),
            "due_date": date.today() + timedelta(days=14),
            "return_date": None,
        }
        self._borrowed.append(record)
        return record

    def return_book(self, isbn):
        """Return a borrowed book."""
        for record in self._borrowed:
            if record["isbn"] == isbn and record["return_date"] is None:
                record["return_date"] = date.today()
                return record
        return None

    def _has_active_borrow(self, isbn):
        return any(r["isbn"] == isbn and r["return_date"] is None for r in self._borrowed)

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

    def get_id(self) -> str:
        return self.member_id

    def display_info(self) -> str:
        phone_str = f" | Phone: {self.phone}" if self.phone else ""
        active = len(self.get_active_borrows())
        return f"Borrower: {self.name} | ID: {self.member_id} | Email: {self.email}{phone_str} | Active borrows: {active}"

    def to_dict(self) -> dict:
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "borrowed": [
                {
                    "isbn": r["isbn"],
                    "borrow_date": str(r["borrow_date"]),
                    "due_date": str(r["due_date"]),
                    "return_date": str(r["return_date"]) if r["return_date"] else None,
                }
                for r in self._borrowed
            ],
        }

    @classmethod
    def from_dict(cls, data: dict):
        borrower = cls(
            member_id=data["member_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
        )
        for record_data in data.get("borrowed", []):
            # Support both old format (book_title) and new format (isbn)
            isbn = record_data.get("isbn") or record_data.get("book_title")
            record = {
                "isbn": isbn,
                "borrow_date": date.fromisoformat(record_data["borrow_date"]) if record_data.get("borrow_date") else date.today(),
                "due_date": date.fromisoformat(record_data["due_date"]) if record_data.get("due_date") else date.today() + timedelta(days=14),
                "return_date": date.fromisoformat(record_data["return_date"]) if record_data.get("return_date") else None,
            }
            borrower._borrowed.append(record)
        return borrower


# ── helpers ──────────────────────────────────────────────────────────────────


def _safe_int(value):
    """Return int(value) or None if value is not a valid integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# ── public I/O ────────────────────────────────────────────────────────────────


def load_data():
    """Load books, authors, and borrowers from library.json."""
    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        return [], [], []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    books = [Book.from_dict(b) for b in data.get("books", [])]
    authors = [Author.from_dict(a) for a in data.get("authors", [])]
    borrowers = [Borrower.from_dict(b) for b in data.get("borrowers", [])]
    return books, authors, borrowers


def save_data(books, authors, borrowers):
    """Save books, authors, and borrowers to library.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "books": [b.to_dict() for b in books],
                "authors": [a.to_dict() for a in authors],
                "borrowers": [b.to_dict() for b in borrowers],
            },
            f,
            indent=4,
        )