"""Database initialization utilities."""

import asyncio

from app.core.database import Base, engine
from app.models import (
    AgentLog,
    AssessmentResult,
    Directive,
    Feedback,
    Lesson,
    Plan,
    QuizAttempt,
    Session,
    User,
)


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should be called once during application setup.
    In production, use proper migration tools like Alembic.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Database tables created successfully")


async def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data. Use with caution.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("✓ Database tables dropped")


if __name__ == "__main__":
    # Run init_db when executed directly
    asyncio.run(init_db())

