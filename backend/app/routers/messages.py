"""API router for message persistence and conversation history."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.messages import (
    ConversationHistoryItem,
    MessageCreate,
    MessageOut,
)
from backend.db.models import Message
from backend.db.session import get_db

router = APIRouter(prefix="/api/v1", tags=["messages"])

# Define dependency annotation once to avoid B008
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/messages", response_model=MessageOut, status_code=201)
async def create_message(payload: MessageCreate, db: DbSession) -> MessageOut:
    """Create a new message in the conversation history."""
    created_at = datetime.utcnow().isoformat()
    length = len(payload.content)

    message = Message(
        user_id=payload.user_id,
        role=payload.role,
        content=payload.content,
        length=length,
        created_at=created_at,
        deleted_at=None,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return MessageOut.model_validate(message)


@router.get(
    "/conversations/{user_id}/messages",
    response_model=list[ConversationHistoryItem],
)
async def get_conversation_history(user_id: int, db: DbSession) -> list[ConversationHistoryItem]:
    """Get conversation history for a user (non-deleted messages only)."""
    stmt = (
        select(Message)
        .where(Message.user_id == user_id, Message.deleted_at.is_(None))
        .order_by(Message.id.asc())
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        ConversationHistoryItem(
            role=m.role,
            content=m.content,
            created_at=m.created_at,
            length=m.length,
        )
        for m in messages
    ]


@router.delete("/conversations/{user_id}/messages", status_code=204)
async def clear_conversation_history(user_id: int, db: DbSession) -> None:
    """Clear (soft delete) all messages for a user."""
    deleted_at = datetime.utcnow().isoformat()

    await db.execute(
        update(Message)
        .where(Message.user_id == user_id, Message.deleted_at.is_(None))
        .values(deleted_at=deleted_at)
    )
    await db.commit()
