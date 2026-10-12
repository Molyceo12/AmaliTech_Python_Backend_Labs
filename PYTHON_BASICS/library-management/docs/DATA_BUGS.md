# Data Bugs

## Bug 1: Borrow Matching by Title Instead of ISBN
**File:** `src/utils.py` functions `get_available_copies`, `get_borrowed_count`, `borrow_book`, `return_book`, `delete_book`
**Problem:** Borrows are matched by `book_title`. Two different books with the same title (different ISBNs) get mixed up — borrowing one marks the other as borrowed, returns affect wrong book.

## Bug 2: DATA_FILE Path Depends on Working Directory
**File:** `src/borrower.py` line 8
**Problem:** `DATA_FILE = Path("data/library.json")` is relative to current working directory. Running from project root vs `src/` creates different files (stray `src/data/library.json`).

## Bug 3: Borrower History Stores Title Not ISBN
**File:** `src/borrower.py` class `Borrower` method `borrow_book` and `_borrowed` records
**Problem:** Borrow records store `book_title` instead of `isbn`. Same collision as Bug 1 — history cannot reliably identify which exact book was borrowed.