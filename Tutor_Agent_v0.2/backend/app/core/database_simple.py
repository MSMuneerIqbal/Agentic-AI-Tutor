"""Simple database setup without aiosqlite dependency."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Use regular SQLite (not async) for simple setup
database_url = "sqlite:///./tutor_gpt.db"

# Create engine
engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
