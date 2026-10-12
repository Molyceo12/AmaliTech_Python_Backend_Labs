# Library Management

A Python CLI application for managing a library's books, authors, borrowers, and loans.

## Setup

```powershell
poetry install
```

## Run

```powershell
poetry run python src/main.py
```

## Test

```powershell
poetry run pytest
```

## Menu

```
Menu:
1. Add a book
2. List all books
3. List authors
4. List borrowers
5. Add a borrower
6. Borrow a book
7. Return a book
8. List active borrows
9. View borrower history
10. Search a book
11. Filter records
12. Reports
13. Delete a book
0. Exit

Enter your choice:
```

## Features

### 1. Add a book
Prompts for title, author name, nationality, birth year, ISBN, publication year, number of copies, category, and book type (Physical Book / EBook / AudioBook). Validates all input and saves to disk.

### 2. List all books
Displays a table of every book with columns: number, title, author, ISBN, category, type, year, copies, available, and status.

### 3. List authors
Shows all authors in the library with name, nationality, birth year, and author ID.

### 4. List borrowers
Shows all registered borrowers with member ID, name, email, phone, and active borrow count.

### 5. Add a borrower
Prompts for member ID, name, email, and optional phone. Validates and adds to registry.

### 6. Borrow a book
Prompts for book ISBN and member ID. Checks availability, creates borrow record with 14-day due date, and saves.

### 7. Return a book
Prompts for member ID and ISBN. Marks the borrow record as returned with today's date.

### 8. List active borrows
Shows all currently borrowed books across all borrowers with member ID, book title, borrow date, due date, and status (Borrowed/Overdue).

### 9. View borrower history
Prompts for member ID and displays complete borrow history for that borrower including returned and overdue books.

### 10. Search a book
Searches books by title, author, ISBN, category, or publication year. Displays matching books with full details.

### 11. Filter records
Filters books by: category (Fiction, Science Fiction, etc.), type (Book, EBook, AudioBook), available (books with copies available), or borrowed (books currently checked out).

### 12. Reports
Generates three reports:
- **Available Books** — all books with at least one copy available
- **Borrowed Books** — all books currently checked out
- **Books by Author** — all books grouped by author with availability counts

### 13. Delete a book
Deletes a book by ISBN. Prevents deletion if any copies are currently borrowed.

### 0. Exit
Saves all data and exits.

## Sample Output

### Add a book

```
Title: The Great Gatsby
Author name: F. Scott Fitzgerald
Nationality (optional): American
Birth year (optional): 1896
ISBN: 978-0-7432-7356-5
Publication year: 1925
Number of copies: 3

Available categories:
Fiction
Non-Fiction
Science Fiction
Fantasy
Mystery
Thriller
Romance
Biography
History
Children
Poetry
Cookbooks
Self-Help
Technology
Science
General
Enter Category: Fiction

Available book types:
1. Book (Physical)
2. EBook
3. AudioBook
Enter book type (1/2/3): 1

Book added successfully.
```

### Add an EBook

```
Title: Digital Design
Author name: John Smith
Nationality (optional): British
Birth year (optional): 1975
ISBN: 978-1-2345-6789-0
Publication year: 2023
Number of copies: 1

Available categories:
...
Enter Category: Technology

Available book types:
1. Book (Physical)
2. EBook
3. AudioBook
Enter book type (1/2/3): 2
File size (MB): 12.5

Book added successfully.
```

### List all books

```
Books in library (2 total):
#  Title             Author              ISBN              Category  Type    Year  Copies  Avail  Status
1  The Great Gatsby  F. Scott Fitzgerald 978-0-7432-7356-5 Fiction   Book    1925  3       3      Available
2  Digital Design    John Smith          978-1-2345-6789-0 Technology EBook   2023  1       1      Available
```

### Borrow a book

```
ISBN of book to borrow: 978-0-7432-7356-5
Member ID: M001
Book borrowed successfully! Due date: 2026-10-26
```

### Return a book

```
Member ID: M001
ISBN of book to return: 978-0-7432-7356-5
Book returned successfully.
```

### Reports → Available Books

```
Available Books Report (2 total):
#  Title             Author              ISBN              Category  Type    Year  Copies  Avail
1  The Great Gatsby  F. Scott Fitzgerald 978-0-7432-7356-5 Fiction   Book    1925  3       3
2  Digital Design    John Smith          978-1-2345-6789-0 Technology EBook   2023  1       1
```

### Books by Author Report

```
Books by Author Report (2 total books, 2 authors):

  Author: F. Scott Fitzgerald (1 books)
    - The Great Gatsby (ISBN: 978-0-7432-7356-5) | Type: Book | Year: 1925 | Copies: 3 | Avail: 3 | Borrowed: 0

  Author: John Smith (1 books)
    - Digital Design (ISBN: 978-1-2345-6789-0) | Type: EBook | Year: 2023 | Copies: 1 | Avail: 1 | Borrowed: 0
```

## Project Structure

```
src/
  author.py          — Author data model with unique author_id
  book.py            — Book, EBook, AudioBook models with Categories enum
  borrower.py        — Borrower domain model with embedded borrow history
  library_resource.py — Abstract base class (LibraryResource)
  storage.py         — Data persistence (load/save to JSON)
  utils.py           — Search, filter, display helpers, report generation
  main.py            — CLI entry point
data/
  library.json       — Persisted library data (created at runtime)
tests/
  test_domain.py     — Unit tests for all domain models
```

## Data Persistence

All data is saved to `data/library.json` on every change. The app loads it automatically on startup. The file is git-ignored.

## Requirements

- Python 3.11+
- pytest (for testing)

Install dependencies with `poetry install`.