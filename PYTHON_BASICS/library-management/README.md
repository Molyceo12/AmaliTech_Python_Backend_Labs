# Library Management

A Python CLI application for managing a library's books, members, and loans.

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
4. Borrow a book
5. Return a book
6. List borrow records
7. Search a book
8. Filter records
9. Delete a book
0. Exit

Enter your choice:
```

## Features

### 1. Add a book
Prompts for title, author name, nationality, birth year, ISBN, publication year, number of copies, category, and book type. Validates all input and saves to disk.

### 2. List all books
Displays a table of every book with columns: number, title, author, ISBN, category, type, year, copies, available, and status.

### 3. List authors
Shows all authors in the library.

### 4. Borrow a book
Prompts for a member name and book title. Decrements available copies and records the borrow.

### 5. Return a book
Prompts for a borrow record ID and marks the book as returned. Increments available copies.

### 6. List borrow records
Shows all active and returned borrow records.

### 7. Search a book
Searches books by title, author, ISBN, category, or publication year.

### 8. Filter records
Filters books by category, type, available, or borrowed.

### 9. Delete a book
Deletes a book by ISBN. Cannot delete if copies are currently borrowed.

### 0. Exit
Saves data and exits.

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
Science
History
General
Enter Category: Fiction

Available book types:
Hardcover
Paperback
Ebook
Audiobook
Book type: Hardcover

Book added successfully.
```

### List all books

```
  #   Title               Author              ISBN              Category    Type       Year  Copies  Avail  Status
  1   The Great Gatsby     F. Scott Fitzgerald 978-0-7432... Fiction     Hardcover   1925  3       3      Available
```

### Borrow a book

```
Enter member name: John Doe
Enter book title: The Great Gatsby
Book borrowed successfully.
```

### Return a book

```
Enter borrow record ID: 1
Book returned successfully.
```

## Project Structure

```
src/
  author.py          — Author data model
  book.py            — Book data model with categories and types
  borrower.py        — Borrower domain model with history
  library_resource.py — Abstract base class (LibraryResource)
  storage.py         — Data persistence (load/save)
  utils.py           — Search, filter, display helpers
  main.py            — CLI entry point
data/
  library.json       — Persisted library data
```

## Data Persistence

All data is saved to `data/library.json` on every change. The app loads it automatically on startup.