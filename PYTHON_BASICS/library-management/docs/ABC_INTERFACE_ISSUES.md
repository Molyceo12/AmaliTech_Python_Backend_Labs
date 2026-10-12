# ABC Interface Issues (LibraryResource)

## Issue 1: LibraryResource Defines No Domain Interface
**File:** `src/book.py` lines 25-37
**Problem:** `LibraryResource` only declares `__repr__` and `__eq__` as abstract. These are Python infrastructure methods, not domain operations. A library resource interface should define what a resource *does* in the domain (e.g., `display_info()`, `to_dict()`, `get_id()`).

## Issue 2: Subclasses Missing Domain Method Implementations
**File:** `src/book.py` classes `Book`, `EBook`, `AudioBook`; `src/author.py` class `Author`; `src/borrower.py` class `Borrower`
**Problem:** Once a proper abstract method like `to_dict()` or `display_info()` is added to `LibraryResource`, all 5 subclasses must implement it. Currently none do.

## Issue 3: Serialization Logic Not Part of Interface
**File:** `src/borrower.py` functions `_serialize_book`, `_serialize_author`, `_serialize_borrower`
**Problem:** Serialization lives in external functions instead of being a contract on the resource classes. Each `LibraryResource` subclass should implement its own `to_dict()` / `from_dict()` per the interface.