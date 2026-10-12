# Architecture / File Organization Issues

## Issue 1: CLI Logic in utils.py Instead of main.py
**File:** `src/utils.py` (592 lines)
**Problem:** The entire CLI loop (`cli()`), menu actions, and user I/O live in `utils.py`. The file is named "utils" but contains the main application entry point. `main.py` exists but is nearly empty.

## Issue 2: Persistence Logic in borrower.py Instead of storage.py
**File:** `src/borrower.py` (lines 140-165)
**Problem:** `load_data()` and `save_data()` — generic persistence for all entities (books, authors, borrowers) — live in `borrower.py`. The file is named for the `Borrower` domain class but contains cross-cutting storage concerns. No `storage.py` module exists.

## Issue 3: LibraryResource ABC in book.py Instead of Own Module
**File:** `src/book.py` (lines 25-40)
**Problem:** `LibraryResource` (the base interface for all library entities) is defined in `book.py` alongside `Book`, `EBook`, `AudioBook`, and `Categories`. It should be in its own module (e.g., `library_resource.py` or `interfaces.py`) since `Author` and `Borrower` also depend on it.

## Issue 4: Circular Import Risk (book.py ↔ author.py ↔ borrower.py)
**Files:** `book.py` imports `Author` in method; `author.py` imports `LibraryResource` from `book.py`; `borrower.py` imports from both
**Problem:** Fragile import structure. Moving `LibraryResource` to its own module breaks the cycle.

## Issue 5: utils.py Does Too Many Things
**File:** `src/utils.py`
**Problem:** Contains: search/filter logic, CLI menu actions, display formatting, AND domain helper functions (`get_available_copies`, `get_borrowed_count`). Violates single responsibility.

## Issue 6: No Clear Layer Separation
**Problem:** Domain logic (Book, Author, Borrower), persistence (load/save), CLI (input/output), and utilities all mixed across 3 files. Hard to test, extend, or replace layers independently.