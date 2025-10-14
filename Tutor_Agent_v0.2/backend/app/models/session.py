"""Session model."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.agent_log import AgentLog
    from app.models.directive import Directive
    from app.models.quiz import QuizAttempt
    from app.models.user import User


class SessionState(str, Enum):
    """Session state enum."""

    GREETING = "greeting"
    ASSESSING = "assessing"
    PLANNING = "planning"
    TUTORING = "tutoring"
    QUIZZING = "quizzing"
    REMEDIATING = "remediating"
    TOPIC_SKIP_ASSESSMENT = "topic_skip_assessment"
    COLLABORATING = "collaborating"
    ADVANCING = "advancing"
    COMPLETING = "completing"
    DONE = "done"


class Session(Base):
    """Session entity."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    state: Mapped[SessionState] = mapped_column(
        String(50),
        default=SessionState.GREETING,
    )
    last_checkpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="session", cascade="all, delete-orphan"
    )
    directives: Mapped[list["Directive"]] = relationship(
        "Directive", back_populates="session", cascade="all, delete-orphan"
    )
    agent_logs: Mapped[list["AgentLog"]] = relationship(
        "AgentLog", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, state={self.state})>"

