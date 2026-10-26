"""FastAPI entry point for the Bookstore app.

Defines the HTTP endpoints (CRUD for books). Each endpoint validates the request,
calls the matching function in services.py, and returns the result or a 404 error.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException  # app class, dependency injection and HTTP errors
import services, schemas  # business logic (DB operations) and request/response schemas
from db import get_db, create_table  # DB session dependency and the table-creation helper
from sqlalchemy.orm import Session  # type hint for the DB session
import models  # noqa: F401  # registers Book on Base so create_table() knows which tables to create

create_table()  # runs once at app startup; creates missing tables, leaves existing ones untouched

app = FastAPI()  # the application object uvicorn serves


@app.get("/books/", response_model=list[schemas.Book])  # GET /books returns a list of books
async def get_all_books(db: Session = Depends(get_db)):
    """List all books.
    Input: db (Session) - injected automatically by FastAPI.
    Output: list of books (JSON), empty list if there are none.
    Why: lets clients browse the whole catalog.
    """
    return services.get_books(db)  # fetch every book from the database

@app.get("/books/{id}", response_model=schemas.Book)  # GET /books/<id> returns one book
async def get_book_by_id(id: int, db: Session = Depends(get_db)):
    """Get a single book by id.

    Input: id (int) - from the URL path; db (Session) - injected by FastAPI.
    Output: the book (JSON), or a 404 error if the id doesn't exist.
    Why: lets clients view the details of one book.
    """
    book_queryset = services.get_book(db, id)  # look the book up (None if missing)
    if book_queryset:
        return book_queryset
    raise HTTPException(status_code=404, detail="Invalid Book ID Provided or Book ID does not exist")  # tell the client the id doesn't exist


@app.post("/books/", response_model=schemas.Book)  # POST /books/ creates a book
async def create_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """Create a new book.

    Input: book (BookCreate) - JSON body with title, description, author, year; db (Session) - injected.
    Output: the created book (JSON) including its generated id.
    Why: lets clients add books to the catalog.
    """
    return services.create_book(db, book)  # save the book and return it with its new id


@app.put("/books/{id}", response_model=schemas.Book)  # PUT /books/<id> updates a book
async def update_book(book: schemas.BookCreate, id: int, db: Session = Depends(get_db)):
    """Update an existing book.

    Input: book (BookCreate) - JSON body with the new values; id (int) - from the URL path; db (Session) - injected.
    Output: the updated book (JSON), or a 404 error if the id doesn't exist.
    Why: lets clients correct or change a book's details.
    """
    db_update = services.update_book(db, book, id)  # returns None if the book doesn't exist
    if not db_update:
        raise HTTPException(status_code=404, detail="Book Not Found")  # nothing to update

    return db_update


@app.delete("/books/{id}", response_model=schemas.Book)  # DELETE /books/<id> removes a book
async def delete_book(id: int, db: Session = Depends(get_db)):
    """Delete a book by id.

    Input: id (int) - from the URL path; db (Session) - injected by FastAPI.
    Output: the deleted book (JSON), or a 404 error if the id doesn't exist.
    Why: lets clients remove books from the catalog.
    """
    delete_entry = services.delete_book(db, id)  # returns None if the book doesn't exist
    if delete_entry:
        return delete_entry
    raise HTTPException(status_code=404, detail="Book Not Found")  # nothing to delete
