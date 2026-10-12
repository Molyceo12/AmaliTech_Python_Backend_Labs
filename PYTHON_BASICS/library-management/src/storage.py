import json
from datetime import date, timedelta
from pathlib import Path

from author import Author
from book import Book, Categories, EBook, AudioBook
from borrower import Borrower
from library_resource import LibraryResource

DATA_FILE = Path(__file__).parent / "data" / "library.json"
DATA_FILE.parent.mkdir(exist_ok=True)


def _safe_int(value):
    """Return int(value) or None if value is not a valid integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


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