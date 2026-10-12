# Library Management Lab - All Identified Issues

## 1. ABC Interface Problem (LibraryResource)
**File:** `src/book.py` lines 25-37
**Problem:** `LibraryResource` only defines `__repr__` and `__eq__` as abstract methods. These are Python dunder methods, not domain-specific interface methods. A real library resource interface should define what a resource *does* (e.g., `display_info()`, `to_dict()`, `get_identifier()`).

## 2. Missing Domain Methods on LibraryResource
**File:** `src/book.py` class `LibraryResource`
**Problem:** No abstract method for:
- Serialization (`to_dict()`)
- Display (`display_info()` or `get_summary()`)
- Unique identification (`get_id()`)
- Resource type identification

## 3. Book Subclasses Don't Implement New Interface
**File:** `src/book.py` classes `Book`, `EBook`, `AudioBook`
**Problem:** Once interface is defined, all subclasses must implement the new abstract methods.

## 4. Borrower Doesn't Implement LibraryResource Interface
**File:** `src/borrower.py` class `Borrower`
**Problem:** `Borrower` extends `LibraryResource` but only implements `__repr__`/`__eq__`. If interface adds `to_dict()`/`display_info()`, `Borrower` must implement them too.

## 5. Author Doesn't Implement LibraryResource Interface
**File:** `src/author.py` class `Author`
**Problem:** `Author` extends `LibraryResource` but only implements `__repr__`/`__eq__`. Same issue as Borrower.

## 6. Serialization Scattered Across Files
**File:** `src/borrower.py` functions `_serialize_book`, `_deserialize_book`, etc.
**Problem:** Serialization logic lives in `borrower.py` instead of on the classes themselves. Each class should have its own `to_dict()`/`from_dict()` methods.

## 7. Borrower Uses Private `_borrowed` List with Dicts
**File:** `src/borrower.py` class `Borrower`
**Problem:** Borrow records are plain dicts, not objects. No validation, no behavior. Should be a proper `BorrowRecord` class (even if nested/private).

## 8. No Borrowing Limits Enforcement
**File:** `src/borrower.py` class `Borrower` method `borrow_book`
**Problem:** No limit on how many books a borrower can have simultaneously. No max borrow duration config.

## 9. No Fine/Overdue Fee Calculation
**File:** `src/borrower.py` class `Borrower`
**Problem:** `has_overdue_books()` exists but no method to calculate fines based on days overdue.

## 10. Book Copies Management Incomplete
**File:** `src/book.py` class `Book`
**Problem:** `copies` tracks total copies but no `available_copies` property. Availability computed externally in `utils.py` by scanning all borrowers.

## 11. ISBN Uniqueness Not Enforced at Domain Level
**File:** `src/utils.py` function `add_book`
**Problem:** ISBN duplicate check only in CLI, not in `Book` constructor or a registry.

## 12. Category/Book Type Validation Inconsistent
**File:** `src/book.py` setters for `category`
**Problem:** `category` setter accepts both `Categories` enum and string. Should be consistent.

## 13. Circular Import Risk (author ↔ book)
**File:** `src/book.py` line 117, `src/author.py` line 3
**Problem:** `Book.author` setter imports `Author` inside method; `Author` imports `LibraryResource` from `book`. Works but fragile.

## 14. No Proper Equality for Borrow Records
**File:** `src/borrower.py` class `Borrower` `_borrowed` list
**Problem:** Borrow records are dicts compared by reference/value in lists. No `__eq__` for borrow record identity.

## 15. Date Handling Inconsistent
**File:** Multiple files
**Problem:** Some places use `date.today()` directly, others use `date.fromisoformat()`. No centralized date utility.

## 16. CLI Tightly Coupled to Domain Logic
**File:** `src/utils.py`
**Problem:** Business logic (borrowing, returning, validation) mixed with CLI input/output. Hard to test.

## 17. No Unit Tests
**Directory:** `tests/` (empty)
**Problem:** No automated tests for any domain logic.

## 18. Error Handling Inconsistent
**File:** Various
**Problem:** Some methods raise `ValueError`, others return `None`/print messages. No consistent pattern.

## 19. No Member Status (Active/Suspended/Expired)
**File:** `src/borrower.py` class `Borrower`
**Problem:** All borrowers treated equally. No membership status to control borrowing privileges.

## 20. Search/Filter Logic in CLI Layer
**File:** `src/utils.py` functions `search_books`, `filter_books`
**Problem:** Domain queries mixed with CLI. Should be on a `LibraryCatalog` or `Repository` class.

## 21. No Library/Repository Facade
**File:** N/A (missing)
**Problem:** No single entry point for library operations. `load_data`/`save_data` are low-level persistence, not domain API.

## 22. Data File Path Hardcoded
**File:** `src/borrower.py` line 9
**Problem:** `DATA_FILE = Path("data/library.json")` assumes working directory. Should be configurable.

## 23. Borrower Phone Validation Missing
**File:** `src/borrower.py` class `Borrower` `__init__`
**Problem:** Phone accepted as any string. No format validation.

## 24. Email Validation Missing
**File:** `src/borrower.py` class `Borrower` `__init__`
**Problem:** Email only checked for non-empty. No format validation.

## 25. Book Title Validation Overly Restrictive
**File:** `src/book.py` `title` setter lines 71-86
**Problem:** `.isalnum()` check after removing punctuation rejects valid titles with accented characters, numbers in words, etc.

---

## Summary by Priority

| Priority | Issues |
|----------|--------|
| **High** | 1, 2, 3, 4, 5 (ABC interface incomplete), 6 (serialization scattered) |
| **Medium** | 7, 8, 9, 10, 11, 19, 21 (domain logic gaps) |
| **Low** | 12, 13, 14, 15, 16, 17, 18, 20, 22, 23, 24, 25 (code quality) |