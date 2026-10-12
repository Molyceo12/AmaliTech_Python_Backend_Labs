#!/usr/bin/env python3
"""Library Management System - Main Entry Point"""

from utils import (
    add_book,
    list_books,
    list_authors,
    add_borrower,
    list_borrowers,
    borrow_book,
    return_book,
    list_borrows,
    list_borrower_history,
    search_book_cli,
    filter_books_cli,
    delete_book,
)
from storage import load_data, save_data


def cli():
    """Main CLI loop: load data, display menu, and dispatch user actions."""
    books, authors, borrowers = load_data()

    actions = {
        "1": lambda: add_book(books, authors, borrowers),
        "2": lambda: list_books(books, borrowers),
        "3": lambda: list_authors(authors),
        "4": lambda: list_borrowers(borrowers),
        "5": lambda: add_borrower(borrowers),
        "6": lambda: borrow_book(books, borrowers, authors),
        "7": lambda: return_book(books, borrowers, authors),
        "8": lambda: list_borrows(books, borrowers),
        "9": lambda: list_borrower_history(books, borrowers),
        "10": lambda: search_book_cli(books),
        "11": lambda: filter_books_cli(books, borrowers),
        "12": lambda: delete_book(books, borrowers, authors),
        "0": lambda: (save_data(books, authors, borrowers), print("Exiting...")),
    }

    while True:
        print("\nMenu:")
        print("1. Add a book")
        print("2. List all books")
        print("3. List authors")
        print("4. List borrowers")
        print("5. Add a borrower")
        print("6. Borrow a book")
        print("7. Return a book")
        print("8. List active borrows")
        print("9. View borrower history")
        print("10. Search a book")
        print("11. Filter records")
        print("12. Delete a book")
        print("0. Exit")

        choice = input("Enter your choice: ")
        actions.get(choice, lambda: print("Invalid choice. Try again."))()

        if choice == "0":
            break


if __name__ == "__main__":
    cli()