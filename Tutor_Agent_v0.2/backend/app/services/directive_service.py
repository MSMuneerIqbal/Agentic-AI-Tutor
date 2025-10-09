"""Service for managing directives and events."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.directive import Directive
from app.models.session import Session

logger = get_logger(__name__)


class DirectiveService:
    """Service for managing directives and session events."""

    async def create_directive(
        self,
        session_id: str,
        directive_type: str,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create a new directive for a session.
        
        Args:
            session_id: Session identifier
            directive_type: Type of directive (orchestrator, agent, etc.)
            payload: Directive payload data
            db: Database session (optional, will create if not provided)
            
        Returns:
            Created directive
        """
        if db is None:
            async for db_session in get_db():
                return await self.create_directive(session_id, directive_type, payload, db_session)
        
        try:
            directive = Directive(
                session_id=uuid.UUID(session_id),
                type=directive_type,
                payload=payload,
            )
            
            db.add(directive)
            await db.commit()
            await db.refresh(directive)
            
            logger.info(
                f"Directive created",
                extra={
                    "directive_id": str(directive.id),
                    "session_id": session_id,
                    "type": directive_type,
                },
            )
            
            return directive
            
        except Exception as e:
            logger.error(
                f"Failed to create directive: {str(e)}",
                extra={
                    "session_id": session_id,
                    "type": directive_type,
                    "error": str(e),
                },
            )
            if db:
                await db.rollback()
            raise

    async def get_session_directives(
        self,
        session_id: str,
        db: AsyncSession | None = None,
    ) -> list[Directive]:
        """
        Get all directives for a session.
        
        Args:
            session_id: Session identifier
            db: Database session (optional)
            
        Returns:
            List of directives
        """
        if db is None:
            async for db_session in get_db():
                return await self.get_session_directives(session_id, db_session)
        
        try:
            result = await db.execute(
                select(Directive)
                .where(Directive.session_id == uuid.UUID(session_id))
                .order_by(Directive.created_at)
            )
            directives = result.scalars().all()
            
            logger.debug(f"Retrieved {len(directives)} directives for session {session_id}")
            return list(directives)
            
        except Exception as e:
            logger.error(f"Failed to get session directives: {str(e)}")
            raise

    async def create_session_start_directive(
        self,
        session_id: str,
        user_id: str,
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create initial session start directive.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            db: Database session (optional)
            
        Returns:
            Created directive
        """
        payload = {
            "event": "session_started",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "initial_state": "greeting",
        }
        
        return await self.create_directive(
            session_id=session_id,
            directive_type="orchestrator",
            payload=payload,
            db=db,
        )

    async def create_greeting_directive(
        self,
        session_id: str,
        greeting_message: str,
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create greeting directive.
        
        Args:
            session_id: Session identifier
            greeting_message: Greeting message sent
            db: Database session (optional)
            
        Returns:
            Created directive
        """
        payload = {
            "event": "greeting_sent",
            "message": greeting_message,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "orchestrator",
        }
        
        return await self.create_directive(
            session_id=session_id,
            directive_type="orchestrator",
            payload=payload,
            db=db,
        )

    async def create_user_input_directive(
        self,
        session_id: str,
        user_input: str,
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create user input directive.
        
        Args:
            session_id: Session identifier
            user_input: User input message
            db: Database session (optional)
            
        Returns:
            Created directive
        """
        payload = {
            "event": "user_input_received",
            "input": user_input,
            "timestamp": datetime.utcnow().isoformat(),
            "input_length": len(user_input),
        }
        
        return await self.create_directive(
            session_id=session_id,
            directive_type="user",
            payload=payload,
            db=db,
        )

    async def create_agent_response_directive(
        self,
        session_id: str,
        agent_name: str,
        response_message: str,
        action: str | None = None,
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create agent response directive.
        
        Args:
            session_id: Session identifier
            agent_name: Name of responding agent
            response_message: Response message
            action: Action taken (optional)
            db: Database session (optional)
            
        Returns:
            Created directive
        """
        payload = {
            "event": "agent_response_sent",
            "agent": agent_name,
            "message": response_message,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "response_length": len(response_message),
        }
        
        return await self.create_directive(
            session_id=session_id,
            directive_type="agent",
            payload=payload,
            db=db,
        )

    async def create_state_transition_directive(
        self,
        session_id: str,
        from_state: str,
        to_state: str,
        reason: str | None = None,
        db: AsyncSession | None = None,
    ) -> Directive:
        """
        Create state transition directive.
        
        Args:
            session_id: Session identifier
            from_state: Previous state
            to_state: New state
            reason: Reason for transition (optional)
            db: Database session (optional)
            
        Returns:
            Created directive
        """
        payload = {
            "event": "state_transition",
            "from_state": from_state,
            "to_state": to_state,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return await self.create_directive(
            session_id=session_id,
            directive_type="orchestrator",
            payload=payload,
            db=db,
        )


# Global directive service instance
directive_service = DirectiveService()
