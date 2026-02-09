"""
Exercise 4: Mini-Project - Library Management System
=====================================================
Combine everything: functions, classes, files, and JSON

This exercise brings together all the concepts from the course.
Build a simple library system that tracks books and borrowers.

Instructions:
- Complete all TODOs
- The system should persist data to JSON files
- Run this file to test your implementation

Run with: python exercise_4_project.py
"""

import json
import os
from datetime import datetime
from zoneinfo import available_timezones

from exercises.src.files import save_json


# =============================================================================
# PART 1: HELPER FUNCTIONS
# =============================================================================

def format_date(dt: datetime = None) -> str:
    """
    Format a datetime object as a string "YYYY-MM-DD".
    If no datetime provided, use current date.

    Example:
        format_date(datetime(2024, 1, 15)) -> "2024-01-15"
        format_date() -> "2024-02-04" (today's date)
    """
    # TODO: Implement this function
    return dt.strftime("%Y-%m-%d") if dt else datetime.now().strftime("%Y-%m-%d")


def generate_id(prefix: str, existing_ids: list) -> str:
    """
    Generate a new unique ID with the given prefix.

    Parameters:
        prefix: String prefix (e.g., "BOOK", "USER")
        existing_ids: List of existing IDs to avoid duplicates

    Returns:
        New ID in format "{prefix}_{number:04d}"

    Example:
        generate_id("BOOK", ["BOOK_0001", "BOOK_0002"]) -> "BOOK_0003"
        generate_id("USER", []) -> "USER_0001"
    """
    # TODO: Implement this function
    # Hint: Find the highest existing number and add 1
    if not existing_ids:
        return f"{prefix}_0001"
    highest_id = max(existing_ids, key=lambda x: int(x.split("_")[1]))
    next_num = int(highest_id.split("_")[1]) + 1
    return f"{prefix}_{next_num:04d}"

def search_items(items: list, **criteria) -> list:
    """
    Search a list of dictionaries by matching criteria.
    Uses **kwargs to accept any search fields.

    Parameters:
        items: List of dictionaries to search
        **criteria: Field-value pairs to match (case-insensitive for strings)

    Returns:
        List of matching items

    Example:
        books = [
            {"title": "Python 101", "author": "Smith"},
            {"title": "Java Guide", "author": "Smith"},
            {"title": "Python Advanced", "author": "Jones"}
        ]
        search_items(books, author="Smith") -> [first two books]
        search_items(books, title="Python 101") -> [first book]
    """
    # TODO: Implement this function
    # Hint: For each item, check if ALL criteria match
    results = []
    for item in items:
        if all(item.get(key) == value for key, value in criteria.items()):
            results.append(item)
    return results


# =============================================================================
# PART 2: BOOK CLASS
# =============================================================================

class Book:
    """
    Represents a book in the library.

    Class Attributes:
        GENRES: List of valid genres ["Fiction", "Non-Fiction", "Science", "History", "Technology"]

    Instance Attributes:
        book_id (str): Unique identifier
        title (str): Book title
        author (str): Author name
        genre (str): Must be one of GENRES
        available (bool): Whether book is available for borrowing

    Methods:
        to_dict(): Convert to dictionary for JSON serialization
        from_dict(data): Class method to create Book from dictionary
        __str__(): Return readable string representation
    """

    GENRES = ["Fiction", "Non-Fiction", "Science", "History", "Technology"]

    def __init__(self, book_id: str, title: str, author: str, genre: str, available: bool = True):
        # TODO: Initialize attributes
        # TODO: Validate that genre is in GENRES, raise ValueError if not
        self.book_id = book_id
        self.title = title
        self.author = author
        self.available = available
        if genre not in Book.GENRES:
            raise ValueError(f"Invalid genre: {genre}. Must be one of {Book.GENRES}")
        else:
            self.genre = genre


    def to_dict(self) -> dict:
        # TODO: Return dictionary with all attributes
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        # TODO: Create and return a Book instance from dictionary
        return cls(**data)

    def __str__(self) -> str:
        # TODO: Return string like "[BOOK_0001] Python 101 by Smith (Technology) - Available"
        status = "Available" if self.available else "Not Available"
        return f"[{self.book_id}] {self.title} by {self.author} ({self.genre}) - {status}"


# =============================================================================
# PART 3: BORROWER CLASS
# =============================================================================

class Borrower:
    """
    Represents a library member who can borrow books.

    Instance Attributes:
        borrower_id (str): Unique identifier
        name (str): Borrower's name
        email (str): Borrower's email
        borrowed_books (list): List of book_ids currently borrowed

    Methods:
        borrow_book(book_id): Add book to borrowed list
        return_book(book_id): Remove book from borrowed list
        to_dict(): Convert to dictionary
        from_dict(data): Class method to create Borrower from dictionary
    """

    MAX_BOOKS = 3  # Maximum books a borrower can have at once

    def __init__(self, borrower_id: str, name: str, email: str, borrowed_books: list = None):
        # TODO: Initialize attributes (use empty list if borrowed_books is None)
        self.borrower_id = borrower_id
        self.name = name
        self.email = email
        self.borrowed_books = borrowed_books if borrowed_books is not None else []

    def can_borrow(self) -> bool:
        """Check if borrower can borrow more books."""
        # TODO: Return True if len(borrowed_books) < MAX_BOOKS
        return len(self.borrowed_books) < Borrower.MAX_BOOKS

    def borrow_book(self, book_id: str) -> bool:
        """Add book to borrowed list. Return False if at max limit."""
        # TODO: Implement this method
        if len(self.borrowed_books) >= Borrower.MAX_BOOKS:
            return False
        self.borrowed_books.append(book_id)
        return True

    def return_book(self, book_id: str) -> bool:
        """Remove book from borrowed list. Return False if not found."""
        # TODO: Implement this method
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
            return True
        return False

    def to_dict(self) -> dict:
        # TODO: Return dictionary with all attributes
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> "Borrower":
        # TODO: Create and return a Borrower instance from dictionary
        return cls(**data)


# =============================================================================
# PART 4: LIBRARY CLASS (Main System)
# =============================================================================

class Library:
    """
    Main library system that manages books and borrowers.
    Persists data to JSON files.

    Attributes:
        name (str): Library name
        books (dict): book_id -> Book
        borrowers (dict): borrower_id -> Borrower
        books_file (str): Path to books JSON file
        borrowers_file (str): Path to borrowers JSON file

    Methods:
        add_book(title, author, genre) -> Book: Add a new book
        add_borrower(name, email) -> Borrower: Add a new borrower
        checkout_book(book_id, borrower_id) -> bool: Borrower checks out a book
        return_book(book_id, borrower_id) -> bool: Borrower returns a book
        search_books(**criteria) -> list: Search books by criteria
        get_available_books() -> list: Get all available books
        get_borrower_books(borrower_id) -> list: Get books borrowed by a borrower
        save(): Save all data to JSON files
        load(): Load data from JSON files
    """

    def __init__(self, name: str, data_dir: str = "."):
        self.name = name
        self.books = {}
        self.borrowers = {}
        self.books_file = os.path.join(data_dir, "library_books.json")
        self.borrowers_file = os.path.join(data_dir, "library_borrowers.json")
        # TODO: Call self.load() to load existing data
        self.load()

    def load(self) -> None:
        """Load books and borrowers from JSON files."""
        # TODO: Load books from self.books_file
        # TODO: Load borrowers from self.borrowers_file
        # Hint: Use try/except to handle files not existing
        try:
            with open(self.books_file, "r", encoding="utf-8") as f:
                books_data = json.load(f)
                self.books = {book_id: Book.from_dict(book_dict) for book_id, book_dict in books_data.items()}
        except FileNotFoundError:
            self.books = {}
        try:
            with open(self.borrowers_file, "r", encoding="utf-8") as f:
                borrowers_data = json.load(f)
                self.borrowers = {borrower_id: Borrower.from_dict(borrower_dict) for borrower_id, borrower_dict in borrowers_data.items()}
        except FileNotFoundError:
            self.borrowers = {}

    def save(self) -> None:
        """Save books and borrowers to JSON files."""
        # TODO: Save self.books to self.books_file
        # TODO: Save self.borrowers to self.borrowers_file
        # Hint: Convert Book/Borrower objects to dicts using to_dict()
        books_data = {book_id: book.to_dict() for book_id, book in self.books.items()}
        borrowers_data = {borrower_id: borrower.to_dict() for borrower_id, borrower in self.borrowers.items()}
        save_json(self.books_file, books_data)
        save_json(self.borrowers_file, borrowers_data)

    def add_book(self, title: str, author: str, genre: str) -> Book:
        """Add a new book to the library."""
        # TODO: Generate new book_id using generate_id
        # TODO: Create Book, add to self.books, save, and return
        book_id = generate_id("BOOK", list(self.books.keys()))
        book = Book(book_id=book_id, title=title, author=author, genre=genre)
        self.books[book.book_id] = book
        self.save()
        return book

    def add_borrower(self, name: str, email: str) -> Borrower:
        """Register a new borrower."""
        # TODO: Generate new borrower_id, create Borrower, add to self.borrowers, save, return
        borrower_id = generate_id("USER", list(self.borrowers.keys()))
        borrower = Borrower(borrower_id, name, email)
        self.borrowers[borrower.borrower_id] = borrower
        self.save()
        return borrower

    def checkout_book(self, book_id: str, borrower_id: str) -> bool:
        """
        Borrower checks out a book.
        Returns False if book unavailable, borrower not found, or at max limit.
        """
        # TODO: Validate book exists and is available
        # TODO: Validate borrower exists and can borrow
        # TODO: Update book.available, borrower.borrowed_books
        # TODO: Save and return True
        book = self.books.get(book_id)
        borrower = self.borrowers.get(borrower_id)

        if not book or not borrower:
            return False

        if book.available and borrower.can_borrow():
            book.available = False
            borrower.borrow_book(book_id)
            self.save()
            return True

        return False

    def return_book(self, book_id: str, borrower_id: str) -> bool:
        """
        Borrower returns a book.
        Returns False if book/borrower not found or book wasn't borrowed by this person.
        """
        # TODO: Validate book and borrower exist
        # TODO: Validate book is in borrower's borrowed_books
        # TODO: Update book.available, remove from borrowed_books
        # TODO: Save and return True
        book = self.books.get(book_id)
        borrower = self.borrowers.get(borrower_id)

        if not book or not borrower:
            return False
        if book_id not in borrower.borrowed_books:
            return False
        book.available = True
        borrower.return_book(book_id)
        self.save()
        return True

    def search_books(self, **criteria) -> list:
        """Search books by any criteria (title, author, genre, available)."""
        # TODO: Use search_items helper function
        # Hint: Convert self.books.values() to list of dicts first
        books_as_dicts = [book.to_dict() for book in self.books.values()]
        return search_items(books_as_dicts, **criteria)

    def get_available_books(self) -> list:
        """Get list of all available books."""
        # TODO: Return books where available=True
        return [book for book in self.books.values() if book.available]

    def get_borrower_books(self, borrower_id: str) -> list:
        """Get list of books currently borrowed by a borrower."""
        # TODO: Get borrower, return list of Book objects for their borrowed_books
        borrower = self.borrowers.get(borrower_id)
        if not borrower:
            return []
        return [self.books[book_id] for book_id in borrower.borrowed_books if book_id in self.books]

    def get_statistics(self) -> dict:
        """
        Return library statistics.
        Uses the concepts of dict comprehension and aggregation.
        """
        # TODO: Return dict with:
        # - total_books: total number of books
        # - available_books: number of available books
        # - checked_out: number of checked out books
        # - total_borrowers: number of borrowers
        # - books_by_genre: dict of genre -> count
        stats = {
            "total_books": len(self.books),
            "available_books": 0,
            "checked_out": 0,
            "total_borrowers": len(self.borrowers),
            "books_by_genre": {}
        }

        for book in self.books.values():
            if book.available:
                stats["available_books"] += 1
            else:
                stats["checked_out"] += 1

            genre = book.genre
            stats["books_by_genre"][genre] = stats["books_by_genre"].get(genre, 0) + 1

        return stats


