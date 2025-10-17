from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.message import Message


class ConversationManager:
    """Управление историей диалогов с персистентным хранением (SQLite, async ORM).

    Зависимость `session_factory` передаётся через конструктор (DI).
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_history(self, user_id: int) -> list[dict[str, str | int]]:
        """Получить историю диалога пользователя (без удалённых).

        Возвращает список словарей: role, content, created_at, length.
        """
        async with self._session_factory() as session:
            stmt = (
                select(Message)
                .where(Message.user_id == user_id, Message.deleted_at.is_(None))
                .order_by(Message.id.asc())
            )
            result = await session.execute(stmt)
            messages = result.scalars().all()
            return [
                {
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at,
                    "length": m.length,
                }
                for m in messages
            ]

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю диалога с метаданными."""
        created_at = datetime.utcnow().isoformat()
        length = len(content)
        async with self._session_factory() as session:
            session.add(
                Message(
                    user_id=user_id,
                    role=role,
                    content=content,
                    length=length,
                    created_at=created_at,
                    deleted_at=None,
                )
            )
            await session.commit()

    async def clear_history(self, user_id: int) -> None:
        """Soft delete: пометить все сообщения пользователя как удалённые."""
        deleted_at = datetime.utcnow().isoformat()
        async with self._session_factory() as session:
            await session.execute(
                update(Message)
                .where(Message.user_id == user_id, Message.deleted_at.is_(None))
                .values(deleted_at=deleted_at)
            )
            await session.commit()
