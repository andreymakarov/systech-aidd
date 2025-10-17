"""Pydantic schemas for message-related API endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    user_id: int = Field(..., description="Telegram user ID")
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content text")


class MessageOut(BaseModel):
    """Schema for message response."""

    id: int
    user_id: int
    role: str
    content: str
    length: int
    created_at: str
    deleted_at: str | None = None

    class Config:
        from_attributes = True


class ConversationHistoryItem(BaseModel):
    """Schema for a single conversation history item (simplified)."""

    role: str
    content: str
    created_at: str
    length: int

