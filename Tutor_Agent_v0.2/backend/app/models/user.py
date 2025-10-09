"""User model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.assessment import AssessmentResult
    from app.models.feedback import Feedback
    from app.models.lesson import Lesson
    from app.models.plan import Plan
    from app.models.quiz import QuizAttempt
    from app.models.session import Session


class User(Base):
    """User entity."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        "AssessmentResult", back_populates="user", cascade="all, delete-orphan"
    )
    plans: Mapped[list["Plan"]] = relationship(
        "Plan", back_populates="user", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

