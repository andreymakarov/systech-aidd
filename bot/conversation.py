"""Conversation manager that interacts with backend API instead of direct DB access."""

from __future__ import annotations

from bot.backend_client import BackendClient


class ConversationManager:
    """Управление историей диалогов через backend API.

    Вместо прямого доступа к БД использует REST API бэкенда.
    """

    def __init__(self, backend_client: BackendClient) -> None:
        self.backend = backend_client

    async def get_history(self, user_id: int) -> list[dict[str, str | int]]:
        """Получить историю диалога пользователя (без удалённых).

        Возвращает список словарей: role, content, created_at, length.
        """
        return await self.backend.get_conversation_history(user_id)

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю диалога с метаданными."""
        await self.backend.create_message(user_id, role, content)

    async def clear_history(self, user_id: int) -> None:
        """Soft delete: пометить все сообщения пользователя как удалённые."""
        await self.backend.clear_conversation_history(user_id)

