from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.utils.config import settings

# Handle SQLite specific parameters
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,  # Set to True to output raw SQL statements to console
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """
    SQLAlchemy Declarative Base class.
    All database models will inherit from this Base.
    """
    pass


def get_db() -> Generator:
    """
    FastAPI dependency that provides a database session context manager.
    Ensures that the connection is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
