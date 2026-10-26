"""Business logic (CRUD operations) for books in the Bookstore app.

Each function talks to the database through a SQLAlchemy session.
Keeping this logic here, separate from the API routes, makes it easy to
reuse, test and change without touching the endpoints.
"""

from models import Book  # ORM model representing the Books table
from sqlalchemy.orm import Session  # type of the DB session passed into every function
from schemas import BookCreate  # validated input data for creating/updating a book


def create_book(db: Session, data: BookCreate):
    """Create a new book and save it to the database.

    Input: db (Session) - active DB session; data (BookCreate) - validated book fields.
    Output: the saved Book object, including its database-generated id.
    Why: single place for the "insert a book" logic so routes stay thin.
    """
    book_instance = Book(**data.model_dump())  # turn the schema into a dict and build an ORM object from it

    db.add(book_instance)  # stage the new row in the session

    db.commit()  # write the row to the database permanently

    db.refresh(book_instance)  # reload the object so it includes the generated id

    return book_instance


def get_books(db: Session):
    """Fetch all books.

    Input: db (Session) - active DB session.
    Output: list of Book objects (empty list if there are none).
    Why: powers the "list books" endpoint.
    """
    return db.query(Book).all()  # SELECT * FROM Books


def get_book(db: Session, book_id: int):
    """Fetch a single book by its id.

    Input: db (Session) - active DB session; book_id (int) - id of the book to find.
    Output: the matching Book object, or None if no book has that id.
    Why: lets the API return one book and also check a book exists before update/delete.
    """

    return db.query(Book).filter(Book.id == book_id).first()  # first match or None


def update_book(db: Session, book: BookCreate, book_id: int):
    """Update an existing book with new values.

    Input: db (Session) - active DB session; book (BookCreate) - new field values; book_id (int) - id of the book to update.
    Output: the updated Book object, or None if no book has that id.
    Why: single place for the "edit a book" logic; None tells the caller to return a 404.
    """
    book_queryset = db.query(Book).filter(Book.id == book_id).first()  # find the existing book

    if book_queryset:  # only update if the book exists
        for key, value in book.model_dump().items():  # go through each new field value
            setattr(book_queryset, key, value)  # overwrite the matching attribute on the ORM object

        db.commit()  # save the changes to the database

        db.refresh(book_queryset)  # reload so the object reflects the saved state

        return book_queryset


def delete_book(db: Session, book_id: int):
    """Delete a book by its id.

    Input: db (Session) - active DB session; book_id (int) - id of the book to delete.
    Output: the deleted Book object, or None if no book has that id.
    Why: single place for the "remove a book" logic; None tells the caller to return a 404.
    """

    book_queryset = db.query(Book).filter(Book.id == book_id).first()  # find the book to delete

    if book_queryset:  # only delete if the book exists
        db.delete(book_queryset)  # stage the row for deletion
        db.commit()  # remove the row from the database permanently
        return book_queryset
