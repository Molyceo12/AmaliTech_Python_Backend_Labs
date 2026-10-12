# Base Errors in Library Management Lab

## Error 1: Using Enum Instead of Inheritance — **FIXED**
**Location:** `src/book.py` lines 25-29 (`TypeOfBook` enum) and line 57 (`book_type` parameter)

**Fix Applied:**
- Removed `TypeOfBook` enum
- Removed `book_type` property from `Book` class
- Created `EBook` and `AudioBook` subclasses extending `Book`

## Error 2: Missing EBook and AudioBook Subclasses — **FIXED**
**Location:** `src/book.py` - entire file

**Fix Applied:**
- Added `EBook` class extending `Book` with `file_size_mb` attribute (validated as positive float)
- Added `AudioBook` class extending `Book` with `duration_minutes` attribute (validated as positive int)
- Both subclasses override `__str__` and `__repr__` methods to demonstrate polymorphism
- Both subclasses have property setters with validation

## Error 3: Serialization/Deserialization Doesn't Support Subclasses — **FIXED**
**Location:** `src/borrower.py` lines 92-121 (`_serialize_book` and `_deserialize_book`)

**Fix Applied:**
- Updated `_serialize_book()` to include `book_class` discriminator and subclass-specific attributes (`file_size_mb`, `duration_minutes`)
- Updated `_deserialize_book()` to instantiate correct subclass based on `book_class` field
- Updated imports to include `EBook` and `AudioBook`

## Error 4: Borrower vs Borrow Confusion
**Location:** `src/borrower.py` line 12 (`class Borrow`)

The file contains a `Borrow` class (representing a borrowing record), not a `Borrower` class (representing a library member/entity). The lab mentions "a Borrower class" — likely meaning a member class separate from borrow records, with attributes like member_id, contact_info, borrowed_books list, etc.