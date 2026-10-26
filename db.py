"""Database configuration for the Bookstore app.

Loads the database connection URL from the environment (.env file) so that
the rest of the app can build its SQLAlchemy engine/session from it.
Keeping the URL in the environment avoids hard-coding credentials in code.
"""

from sqlalchemy import create_engine  # creates the DB engine
from sqlalchemy.orm import sessionmaker, declarative_base  # session factory and ORM base class

from dotenv import load_dotenv  # reads key=value pairs from a .env file into environment variables

import os  # used to read environment variables


load_dotenv()  # load the .env file so os.getenv can see its values

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")  # DB connection string, kept in env to keep secrets out of code

engine = create_engine(SQLALCHEMY_DATABASE_URL)  # manages the actual connection(s) to the database

# autocommit=False: we commit explicitly; autoflush=False: changes reach the DB only when we say so
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # factory creating one DB session per request

Base = declarative_base()  # parent class for all ORM models (e.g. Book in models.py)

def get_db():
    """Provide a database session for one request and always close it afterwards.

    Input: none (used as a FastAPI dependency via Depends(get_db)).
    Output: yields a SQLAlchemy Session object.
    Why: guarantees every request gets its own session and that the connection
    is released even if an error happens, preventing connection leaks.
    """

    db = SessionLocal()  # open a new session for this request

    try:
        yield db  # hand the session to the endpoint that requested it
    finally:
        db.close()  # runs after the request ends (success or error) to free the connection

def create_table():
    """Create all tables defined by our ORM models in the database.

    Input: none.
    Output: none (tables are created as a side effect; existing tables are left untouched).
    Why: sets up the database schema on startup so we don't create tables by hand.
    """
    Base.metadata.create_all(bind=engine)  # creates the table of every model inheriting Base, if missing
