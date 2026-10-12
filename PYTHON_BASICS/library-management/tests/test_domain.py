"""Tests for Library Management domain models."""

import pytest
from datetime import date

from book import Book, EBook, AudioBook, Categories
from author import Author
from borrower import Borrower


class TestAuthor:
    def test_author_creation(self):
        author = Author("Test Author", "USA", 1980)
        assert author.name == "Test Author"
        assert author.nationality == "USA"
        assert author.birth_year == 1980
        assert author.author_id is not None

    def test_author_get_id(self):
        author = Author("Test Author", "USA", 1980)
        assert author.get_id() == author.author_id

    def test_author_to_dict(self):
        author = Author("Test Author", "USA", 1980)
        data = author.to_dict()
        assert data["name"] == "Test Author"
        assert data["nationality"] == "USA"
        assert data["birth_year"] == 1980
        assert "author_id" in data

    def test_author_from_dict(self):
        data = {"name": "Test Author", "nationality": "USA", "birth_year": 1980}
        author = Author.from_dict(data)
        assert author.name == "Test Author"
        assert author.nationality == "USA"
        assert author.birth_year == 1980
        assert author.author_id is not None


class TestBook:
    def setup_method(self):
        self.author = Author("Test Author", "USA", 1980)

    def test_book_creation(self):
        book = Book("Test Book", self.author, "1234567890", 2020, Categories.FICTION, 2)
        assert book.title == "Test Book"
        assert book.isbn == "1234567890"
        assert book.year == 2020
        assert book.category == Categories.FICTION
        assert book.copies == 2

    def test_book_get_id(self):
        book = Book("Test Book", self.author, "1234567890", 2020, Categories.FICTION, 2)
        assert book.get_id() == "1234567890"

    def test_book_to_dict(self):
        book = Book("Test Book", self.author, "1234567890", 2020, Categories.FICTION, 2)
        data = book.to_dict()
        assert data["title"] == "Test Book"
        assert data["isbn"] == "1234567890"
        assert data["category"] == "Fiction"
        assert data["year"] == 2020
        assert data["copies"] == 2
        assert "author" in data

    def test_book_from_dict(self):
        data = {
            "title": "Test Book",
            "isbn": "1234567890",
            "category": "Fiction",
            "year": 2020,
            "copies": 2,
            "author": {"name": "Test Author", "nationality": "USA", "birth_year": 1980},
        }
        book = Book.from_dict(data)
        assert book.title == "Test Book"
        assert book.isbn == "1234567890"


class TestEBook:
    def setup_method(self):
        self.author = Author("Test Author", "USA", 1980)

    def test_ebook_creation(self):
        ebook = EBook("Test EBook", self.author, "1234567891", 2021, 5.5, Categories.SCIENCE_FICTION, 1)
        assert ebook.file_size_mb == 5.5

    def test_ebook_to_dict(self):
        ebook = EBook("Test EBook", self.author, "1234567891", 2021, 5.5, Categories.SCIENCE_FICTION, 1)
        data = ebook.to_dict()
        assert data["book_class"] == "EBook"
        assert data["file_size_mb"] == 5.5

    def test_ebook_from_dict(self):
        data = {
            "title": "Test EBook",
            "isbn": "1234567891",
            "category": "Science Fiction",
            "year": 2021,
            "copies": 1,
            "file_size_mb": 5.5,
            "author": {"name": "Test Author", "nationality": "USA", "birth_year": 1980},
            "book_class": "EBook",
        }
        ebook = EBook.from_dict(data)
        assert ebook.file_size_mb == 5.5


class TestAudioBook:
    def setup_method(self):
        self.author = Author("Test Author", "USA", 1980)

    def test_audiobook_creation(self):
        audiobook = AudioBook("Test AudioBook", self.author, "1234567892", 2022, 300, Categories.FANTASY, 1)
        assert audiobook.duration_minutes == 300

    def test_audiobook_to_dict(self):
        audiobook = AudioBook("Test AudioBook", self.author, "1234567892", 2022, 300, Categories.FANTASY, 1)
        data = audiobook.to_dict()
        assert data["book_class"] == "AudioBook"
        assert data["duration_minutes"] == 300

    def test_audiobook_from_dict(self):
        data = {
            "title": "Test AudioBook",
            "isbn": "1234567892",
            "category": "Fantasy",
            "year": 2022,
            "copies": 1,
            "duration_minutes": 300,
            "author": {"name": "Test Author", "nationality": "USA", "birth_year": 1980},
            "book_class": "AudioBook",
        }
        audiobook = AudioBook.from_dict(data)
        assert audiobook.duration_minutes == 300


class TestBorrower:
    def test_borrower_creation(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        assert borrower.member_id == "M001"
        assert borrower.name == "John Doe"
        assert borrower.email == "john@example.com"

    def test_borrower_get_id(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        assert borrower.get_id() == "M001"

    def test_borrow_book(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        record = borrower.borrow_book("1234567890")
        assert record["isbn"] == "1234567890"
        assert record["return_date"] is None

    def test_return_book(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        borrower.borrow_book("1234567890")
        record = borrower.return_book("1234567890")
        assert record["return_date"] is not None

    def test_active_borrows(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        borrower.borrow_book("1234567890")
        borrower.borrow_book("1234567891")
        assert len(borrower.get_active_borrows()) == 2
        borrower.return_book("1234567890")
        assert len(borrower.get_active_borrows()) == 1

    def test_borrower_to_dict(self):
        borrower = Borrower("M001", "John Doe", "john@example.com")
        borrower.borrow_book("1234567890")
        data = borrower.to_dict()
        assert data["member_id"] == "M001"
        assert "borrowed" in data
        assert len(data["borrowed"]) == 1

    def test_borrower_from_dict(self):
        data = {
            "member_id": "M001",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": None,
            "borrowed": [
                {"isbn": "1234567890", "borrow_date": "2026-10-12", "due_date": "2026-10-26", "return_date": None}
            ],
        }
        borrower = Borrower.from_dict(data)
        assert borrower.member_id == "M001"
        assert len(borrower.get_borrow_history()) == 1