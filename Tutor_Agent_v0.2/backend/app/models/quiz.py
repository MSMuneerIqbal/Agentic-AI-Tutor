"""Quiz attempt model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class QuizAttempt(Base):
    """Quiz attempt entity."""

    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        index=True,
    )
    score: Mapped[int] = mapped_column(Integer)  # 0-100
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    total_questions: Mapped[int] = mapped_column(Integer)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    session: Mapped["Session"] = relationship("Session", back_populates="quiz_attempts")

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, score={self.score}, passed={self.passed})>"

