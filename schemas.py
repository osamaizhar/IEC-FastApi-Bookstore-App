"""Pydantic schemas (request/response shapes) for the Bookstore API.

Schemas validate the data coming into the API and control the data going out.
They are separate from the ORM models in models.py, which describe DB tables.
"""
from pydantic import BaseModel  # gives us automatic type validation and JSON serialization

# Payload Structure defined
class BookBase(BaseModel):
    """Fields shared by every book schema.

    Input: title, description, author (str) and year (int).
    Output: a validated object; invalid types raise a validation error.
    Why: defined once so BookCreate and Book don't repeat the same fields.
    """

    title:str  # book title
    description: str  # short summary of the book
    author: str  # author's name
    year: int  # publication year


class BookCreate(BookBase):
    """Schema for the request body when creating a new book.

    Input: same fields as BookBase (no id; the database generates it).
    Output: a validated object ready to be saved as a Book row.
    Why: the client must not choose the id, so it is left out of this schema.
    """

    pass  # no extra fields needed; inherits everything from BookBase


class Book(BookBase):
    """Schema for a book returned by the API (response model).

    Input: a Book ORM object from the database (or matching data).
    Output: the book fields plus its id, serialized to JSON.
    Why: clients need the id to reference a book later (get, update, delete).
    """

    id: int  # database-generated unique ID

    class config:  # Pydantic settings for this schema
        orm_mode = True  # allows reading data from ORM objects (attributes), not only dicts
        from_attribute = True  # same purpose as orm_mode (its Pydantic v2 equivalent)
