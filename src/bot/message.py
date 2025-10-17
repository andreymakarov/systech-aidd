from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for ORM models."""


class Message(Base):
    """ORM model representing a chat message stored persistently.

    Soft-delete is implemented via nullable deleted_at column.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int]
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    length: Mapped[int]
    created_at: Mapped[str]
    deleted_at: Mapped[str | None] = mapped_column(nullable=True)


