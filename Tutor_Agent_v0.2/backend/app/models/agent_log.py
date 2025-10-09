"""Agent log model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.session import Session


class AgentLog(Base):
    """Agent log entity."""

    __tablename__ = "agent_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100), index=True
    )  # guardrail_trigger, tool_error, etc.
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="agent_logs")

    def __repr__(self) -> str:
        return f"<AgentLog(id={self.id}, event_type={self.event_type})>"

