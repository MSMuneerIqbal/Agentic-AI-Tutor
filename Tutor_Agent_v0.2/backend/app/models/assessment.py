"""Assessment result model."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class LearningStyle(str, Enum):
    """VARK learning style enum."""

    VISUAL = "V"
    AUDITORY = "A"
    READING = "R"
    KINESTHETIC = "K"


class AssessmentResult(Base):
    """Assessment result entity."""

    __tablename__ = "assessment_results"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    style: Mapped[LearningStyle] = mapped_column(String(1))
    answers: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="assessment_results")

    def __repr__(self) -> str:
        return f"<AssessmentResult(id={self.id}, style={self.style})>"

