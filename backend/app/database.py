"""
Provides functionality for interacting with the application database.

The module provides a function, `get_db`,
which provides a database session for use in the application.
The function is intended to be used as a dependency in the FastAPI application.

The module also provides a function, `create_db_and_tables`,
which creates the database and tables if they do not exist.
The function should be called when the application starts.
"""

# Standard Libraries
from collections.abc import Generator
from os import environ

# External Libraries
from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv

# Internal Libraries
# Imported to register all nested models for the `create_db_and_tables` function
from app import models

# Load environment variables
load_dotenv()

# Define Constants
DATABASE_URL: str | None = environ.get("DATABASE_URL")
CONNECTION_ARGS: dict = {"check_same_thread": False}
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Create DB connection engine
ENGINE = create_engine(url=DATABASE_URL, connect_args=CONNECTION_ARGS)


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for use in the application.

    Yields:
        Generator[Session, None, None]: A generator that yields a database session.
    """
    with Session(ENGINE) as session:
        yield session


def create_db_and_tables() -> None:
    """
    Creates the database and tables if they don't exist.
    """
    SQLModel.metadata.create_all(bind=ENGINE)
