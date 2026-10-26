"""Database models (ORM tables) for the Bookstore app.

Each class here maps to one table in the database. SQLAlchemy uses these
definitions to create the tables and to read/write rows as Python objects.
"""

from db import Base  # shared parent class that registers our models with SQLAlchemy

from sqlalchemy import Integer, Column, String  # column types and the Column constructor


class Book(Base):
    """ORM model for the "Books" table; one instance represents one book row.

    Input: field values (title, description, author, year) when creating a book.
    Output: a Book object that SQLAlchemy can save to / load from the database.
    Why: gives us a typed Python representation of a book instead of raw SQL.
    """

    __tablename__ = "Books"  # name of the table in the database
    id = Column(Integer, primary_key=True, index=True)  # unique book ID; indexed for fast lookups
    title = Column(String, index=True)  # book title; indexed so searching by title is fast
    description = Column(String, index=True)  # short summary; indexed for search
    author = Column(String, index=True)  # author's name; indexed to find books by author quickly
    year = Column(Integer)  # publication year (not indexed, we don't search by it)
