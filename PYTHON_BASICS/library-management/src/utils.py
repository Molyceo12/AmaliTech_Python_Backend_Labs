from author import Author
from book import Book, Categories, EBook, AudioBook
from borrower import Borrower, load_data, save_data
from datetime import date


def get_available_copies(book: Book, borrowers: list[Borrower]) -> int:
    """Return total copies minus the number of active (unreturned) borrows."""
    borrowed = sum(1 for b in borrowers for r in b.get_active_borrows() if r["book_title"] == book.title)
    return book.copies - borrowed


def get_borrowed_count(book: Book, borrowers: list[Borrower]) -> int:
    """Return the number of copies currently borrowed."""
    return sum(1 for b in borrowers for r in b.get_active_borrows() if r["book_title"] == book.title)


def search_books(books: list[Book], query: str, field: str) -> list[Book]:
    """Search books by a given field (title, author, isbn, category, year)."""
    query = query.lower()
    results = []
    for book in books:
        if field == "title" and query in book.title.lower():
            results.append(book)
        elif field == "author" and query in book.author.name.lower():
            results.append(book)
        elif field == "isbn" and query in book.isbn.lower():
            results.append(book)
        elif (
            field == "category"
            and book.category
            and query in book.category.value.lower()
        ):
            results.append(book)
        elif field == "year" and book.year and query in str(book.year):
            results.append(book)
    return results


def filter_books(
    books: list[Book], borrowers: list[Borrower], criteria: str, value=None
) -> list[Book]:
    """
    Filter books by criteria:
    - available: books with copies available
    - borrowed: books currently borrowed
    - category: books matching a Categories enum value
    - type: books matching a book class (Book, EBook, AudioBook)
    """
    filtered = []
    for book in books:
        available_count = get_available_copies(book, borrowers)
        borrowed_count = get_borrowed_count(book, borrowers)

        if criteria == "available" and available_count > 0:
            filtered.append(book)
        elif criteria == "borrowed" and borrowed_count > 0:
            filtered.append(book)
        elif (
            criteria == "category"
            and isinstance(value, Categories)
            and book.category == value
        ):
            filtered.append(book)
        elif (
            criteria == "type"
            and isinstance(value, type)
            and issubclass(value, Book)
            and isinstance(book, value)
        ):
            filtered.append(book)
    return filtered


def add_book(books, authors, borrowers):
    """Prompt user for book details, validate input, and add the book."""
    title = input("Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    author_name = input("Author name: ").strip()
    if not author_name:
        print("Author name cannot be empty.")
        return

    nationality = input("Nationality (optional): ").strip() or None
    birth_year_input = input("Birth year (optional): ").strip() or None
    if birth_year_input is not None:
        try:
            birth_year_input = int(birth_year_input)
        except ValueError:
            print("Birth year must be a number.")
            return

    author = next((a for a in authors if a.name == author_name), None)
    if not author:
        try:
            author = Author(author_name, nationality, birth_year_input)
        except ValueError as e:
            print(f"Invalid author data: {e}")
            return
        authors.append(author)

    isbn = input("ISBN: ").strip()
    if not isbn:
        print("ISBN cannot be empty.")
        return
    if any(b.isbn == isbn for b in books):
        print("ISBN already exists! Book not added.")
        return

    year_input = input("Publication year: ").strip()
    if not year_input:
        print("Publication year cannot be empty.")
        return
    try:
        year = int(year_input)
    except ValueError:
        print("Publication year must be a number.")
        return

    copies_input = input("Number of copies: ").strip()
    if not copies_input:
        print("Number of copies cannot be empty.")
        return
    try:
        copies = int(copies_input)
        if copies < 1:
            raise ValueError
    except ValueError:
        print("Number of copies must be a positive integer.")
        return

    print("\nAvailable categories:")
    for cat in Categories:
        print(cat.value)
    category_input = input("Enter Category: ").strip().title()
    try:
        category = Categories(category_input) if category_input else Categories.GENERAL
    except ValueError:
        print(f"Invalid category '{category_input}'. Using General.")
        category = Categories.GENERAL

    print("\nAvailable book types:")
    print("1. Book (Physical)")
    print("2. EBook")
    print("3. AudioBook")
    book_class_input = input("Enter book type (1/2/3): ").strip()
    
    if book_class_input == "2":
        # EBook
        file_size_input = input("File size (MB): ").strip()
        try:
            file_size_mb = float(file_size_input)
            if file_size_mb <= 0:
                raise ValueError
        except ValueError:
            print("File size must be a positive number.")
            return
        try:
            book = EBook(title, author, isbn, year, file_size_mb, category, copies)
        except ValueError as e:
            print(f"Invalid book data: {e}")
            return
    elif book_class_input == "3":
        # AudioBook
        duration_input = input("Duration (minutes): ").strip()
        try:
            duration_minutes = int(duration_input)
            if duration_minutes <= 0:
                raise ValueError
        except ValueError:
            print("Duration must be a positive integer.")
            return
        try:
            book = AudioBook(title, author, isbn, year, duration_minutes, category, copies)
        except ValueError as e:
            print(f"Invalid book data: {e}")
            return
    else:
        # Physical Book
        try:
            book = Book(title, author, isbn, year, category, copies)
        except ValueError as e:
            print(f"Invalid book data: {e}")
            return

    books.append(book)
    save_data(books, authors, borrowers)
    print("Book added successfully.")


def _fmt_row(widths, values):
    return "  ".join(str(v).ljust(w) for w, v in zip(widths, values))


def list_books(books, borrowers):
    """Display all books in a column-aligned table without border lines."""
    if not books:
        print("No books in the library.")
        return
    headers = [
        "#",
        "Title",
        "Author",
        "ISBN",
        "Category",
        "Type",
        "Year",
        "Copies",
        "Avail",
        "Status",
    ]
    rows = []
    for i, b in enumerate(books, 1):
        available = get_available_copies(b, borrowers)
        book_type = type(b).__name__
        rows.append(
            [
                i,
                b.title,
                b.author.name,
                b.isbn,
                b.category.value if b.category else "",
                book_type,
                b.year or "",
                b.copies,
                available,
                "Available" if available > 0 else "Not Available",
            ]
        )
    widths = [
        max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))
    ]
    print(f"\nBooks in library ({len(books)} total):")
    print(_fmt_row(widths, headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(_fmt_row(widths, row))


def list_authors(authors):
    """Display all authors in a column-aligned table without border lines."""
    if not authors:
        print("No authors found.")
        return
    headers = ["#", "Name", "Nationality", "Birth Year"]
    rows = [
        [i, a.name, a.nationality or "", a.birth_year or ""]
        for i, a in enumerate(authors, 1)
    ]
    widths = [
        max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))
    ]
    print(f"\nAuthors ({len(authors)} total):")
    print(_fmt_row(widths, headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(_fmt_row(widths, row))


def add_borrower(borrowers):
    """Prompt user for borrower details and add the borrower."""
    member_id = input("Member ID: ").strip()
    if not member_id:
        print("Member ID cannot be empty.")
        return
    if any(b.member_id == member_id for b in borrowers):
        print("Member ID already exists!")
        return

    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    email = input("Email: ").strip()
    if not email:
        print("Email cannot be empty.")
        return

    phone = input("Phone (optional): ").strip() or None

    try:
        borrower = Borrower(member_id, name, email, phone)
    except ValueError as e:
        print(f"Invalid borrower data: {e}")
        return

    borrowers.append(borrower)
    print("Borrower added successfully.")


def list_borrowers(borrowers):
    """Display all borrowers in a column-aligned table."""
    if not borrowers:
        print("No borrowers registered.")
        return
    headers = ["#", "Member ID", "Name", "Email", "Phone", "Active Borrows"]
    rows = [
        [i, b.member_id, b.name, b.email, b.phone or "", len(b.get_active_borrows())]
        for i, b in enumerate(borrowers, 1)
    ]
    widths = [
        max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))
    ]
    print(f"\nBorrowers ({len(borrowers)} total):")
    print(_fmt_row(widths, headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(_fmt_row(widths, row))


def borrow_book(books, borrowers, authors):
    """Borrow a book by ISBN if copies are available."""
    isbn = input("ISBN of book to borrow: ").strip()
    if not isbn:
        print("ISBN cannot be empty.")
        return
    book_to_borrow = next((b for b in books if b.isbn == isbn), None)
    if not book_to_borrow:
        print("Book not found.")
        return

    available = get_available_copies(book_to_borrow, borrowers)
    if available <= 0:
        print("No available copies to borrow.")
        return

    member_id = input("Member ID: ").strip()
    if not member_id:
        print("Member ID cannot be empty.")
        return
    
    borrower = next((b for b in borrowers if b.member_id == member_id), None)
    if not borrower:
        print("Borrower not found. Please register first.")
        return

    record = borrower.borrow_book(book_to_borrow.title)
    save_data(books, authors, borrowers)
    print(f"Book borrowed successfully! Due date: {record.due_date}")


def return_book(books, borrowers, authors):
    """Mark a borrowed book as returned."""
    member_id = input("Member ID: ").strip()
    if not member_id:
        print("Member ID cannot be empty.")
        return
    isbn = input("ISBN of book to return: ").strip()
    if not isbn:
        print("ISBN cannot be empty.")
        return

    book_to_return = next((b for b in books if b.isbn == isbn), None)
    if not book_to_return:
        print("Book not found.")
        return

    borrower = next((b for b in borrowers if b.member_id == member_id), None)
    if not borrower:
        print("Borrower not found.")
        return

    record = borrower.return_book(book_to_return.title)
    if record:
        save_data(books, authors, borrowers)
        print("Book returned successfully.")
    else:
        print("No active borrow record found for this book and borrower.")


def list_borrows(borrowers):
    """Display all active (unreturned) borrow records from all borrowers."""
    active = []
    for b in borrowers:
        for r in b.get_active_borrows():
            active.append((b.member_id, r))
    
    if not active:
        print("No active borrow records found.")
        return
    headers = ["#", "Member ID", "Book Title", "Borrowed On", "Due Date", "Status"]
    rows = [
        [
            i,
            member_id,
            r["book_title"],
            r["borrow_date"],
            r["due_date"],
            "Overdue" if r["return_date"] is None and date.today() > r["due_date"] else "Borrowed",
        ]
        for i, (member_id, r) in enumerate(active, 1)
    ]
    widths = [
        max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))
    ]
    print(f"\nActive Borrow records ({len(active)} total):")
    print(_fmt_row(widths, headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(_fmt_row(widths, row))


def list_borrower_history(borrowers):
    """Display full borrow history for a specific borrower."""
    member_id = input("Member ID: ").strip()
    if not member_id:
        print("Member ID cannot be empty.")
        return
    
    borrower = next((b for b in borrowers if b.member_id == member_id), None)
    if not borrower:
        print("Borrower not found.")
        return
    
    history = borrower.get_borrow_history()
    if not history:
        print("No borrow history found.")
        return
    
    headers = ["#", "Book Title", "Borrowed On", "Due Date", "Returned On", "Status"]
    rows = []
    for i, r in enumerate(history, 1):
        if r["return_date"]:
            status = "Returned"
        elif r["return_date"] is None and date.today() > r["due_date"]:
            status = "Overdue"
        else:
            status = "Borrowed"
        rows.append([
            i,
            r["book_title"],
            r["borrow_date"],
            r["due_date"],
            r["return_date"] or "N/A",
            status,
        ])
    widths = [
        max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))
    ]
    print(f"\nBorrow history for {borrower.name} ({member_id}):")
    print(_fmt_row(widths, headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(_fmt_row(widths, row))


def search_book_cli(books):
    """Prompt user for a search field and query, then display matching books."""
    field = input("Search by (title/author/isbn/category/year): ").strip().lower()
    if field not in ("title", "author", "isbn", "category", "year"):
        print("Invalid search field.")
        return
    query = input("Enter search query: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return
    results = search_books(books, query, field)
    if results:
        for b in results:
            print(b)
    else:
        print("No books found.")


def filter_books_cli(books, borrowers):
    """Prompt user for filter criteria and display matching books."""
    print("Filter by: category / type / available / borrowed")
    criteria = input("Enter filter criteria: ").strip().lower()
    value = None

    if criteria == "category":
        print("\nAvailable Categories:")
        for cat in Categories:
            print(cat.value)
        value_input = input("Enter category: ").strip().title()
        if not value_input:
            print("Category cannot be empty.")
            return
        try:
            value = Categories(value_input)
        except ValueError:
            print(f"Invalid category '{value_input}'.")
            return

    elif criteria == "type":
        print("\nAvailable Book Types:")
        print("1. Book (Physical)")
        print("2. EBook")
        print("3. AudioBook")
        value_input = input("Enter type (1/2/3): ").strip()
        if not value_input:
            print("Book type cannot be empty.")
            return
        if value_input == "1":
            value = Book
        elif value_input == "2":
            value = EBook
        elif value_input == "3":
            value = AudioBook
        else:
            print(f"Invalid book type '{value_input}'.")
            return

    elif criteria in ["available", "borrowed"]:
        value = criteria

    else:
        print("Invalid filter criteria.")
        return

    results = filter_books(books, borrowers, criteria, value)
    if results:
        for b in results:
            available = get_available_copies(b, borrowers)
            borrowed = get_borrowed_count(b, borrowers)
            print(f"{b} | Available: {available} | Borrowed: {borrowed}")
    else:
        print("No books match the filter criteria.")


def delete_book(books, borrowers, authors):
    """Delete a book by ISBN if it has no active borrows."""
    isbn = input("Enter ISBN of the book to delete: ").strip()
    if not isbn:
        print("ISBN cannot be empty.")
        return
    book = next((b for b in books if b.isbn == isbn), None)
    if not book:
        print("Book not found.")
        return

    if any(r["book_title"] == book.title for b in borrowers for r in b.get_active_borrows()):
        print("Cannot delete. Some copies are currently borrowed.")
        return

    books.remove(book)
    save_data(books, authors, borrowers)
    print(f"Book '{book.title}' deleted successfully.")


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
        "8": lambda: list_borrows(borrowers),
        "9": lambda: list_borrower_history(borrowers),
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