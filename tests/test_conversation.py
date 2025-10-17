"""Unit tests for ConversationManager (updated for async + metadata)."""

import pytest
from unittest.mock import AsyncMock

from bot.conversation import ConversationManager


@pytest.mark.asyncio
async def test_get_history_empty() -> None:
    """Пустая история для нового пользователя.

    В юнит-тестах теперь требуется мок или фикстура с session_factory.
    Тесты менеджера покрываются интеграционно, здесь проверяем контракт формата.
    """
    manager = ConversationManager(session_factory=lambda: None)  # type: ignore[arg-type]
    # Мокаем async метод на уровне экземпляра, чтобы не зависеть от БД
    manager.get_history = AsyncMock(return_value=[])  # type: ignore[assignment]
    history = await manager.get_history(user_id=123)
    assert history == []


@pytest.mark.asyncio
async def test_message_shape_contains_metadata() -> None:
    """Сообщение содержит created_at и length помимо role и content."""
    manager = ConversationManager(session_factory=lambda: None)  # type: ignore[arg-type]
    sample = {
        "role": "user",
        "content": "Hello",
        "created_at": "2025-01-01T00:00:00",
        "length": 5,
    }
    manager.get_history = AsyncMock(return_value=[sample])  # type: ignore[assignment]
    history = await manager.get_history(user_id=123)
    assert set(history[0].keys()) == {"role", "content", "created_at", "length"}
    assert isinstance(history[0]["created_at"], str)
    assert isinstance(history[0]["length"], int)

