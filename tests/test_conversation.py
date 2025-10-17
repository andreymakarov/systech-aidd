"""Unit tests for ConversationManager (updated to use BackendClient)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.conversation import ConversationManager
from bot.backend_client import BackendClient


@pytest.mark.asyncio
async def test_get_history_empty() -> None:
    """Пустая история для нового пользователя."""
    backend_client = MagicMock(spec=BackendClient)
    backend_client.get_conversation_history = AsyncMock(return_value=[])

    manager = ConversationManager(backend_client)
    history = await manager.get_history(user_id=123)
    assert history == []
    backend_client.get_conversation_history.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_message_shape_contains_metadata() -> None:
    """Сообщение содержит created_at и length помимо role и content."""
    backend_client = MagicMock(spec=BackendClient)
    sample = {
        "role": "user",
        "content": "Hello",
        "created_at": "2025-01-01T00:00:00",
        "length": 5,
    }
    backend_client.get_conversation_history = AsyncMock(return_value=[sample])

    manager = ConversationManager(backend_client)
    history = await manager.get_history(user_id=1)
    assert len(history) == 1
    msg = history[0]
    assert msg["role"] == "user"
    assert msg["content"] == "Hello"
    assert msg["created_at"] == "2025-01-01T00:00:00"
    assert msg["length"] == 5


@pytest.mark.asyncio
async def test_add_message() -> None:
    """Добавление сообщения вызывает backend API."""
    backend_client = MagicMock(spec=BackendClient)
    backend_client.create_message = AsyncMock(return_value={"id": 1})

    manager = ConversationManager(backend_client)
    await manager.add_message(user_id=100, role="assistant", content="Hi there!")

    backend_client.create_message.assert_awaited_once_with(100, "assistant", "Hi there!")


@pytest.mark.asyncio
async def test_clear_history() -> None:
    """Очистка истории вызывает backend API."""
    backend_client = MagicMock(spec=BackendClient)
    backend_client.clear_conversation_history = AsyncMock(return_value=None)

    manager = ConversationManager(backend_client)
    await manager.clear_history(user_id=200)

    backend_client.clear_conversation_history.assert_awaited_once_with(200)


@pytest.mark.asyncio
async def test_get_history_with_multiple_messages() -> None:
    """История с несколькими сообщениями."""
    backend_client = MagicMock(spec=BackendClient)
    messages = [
        {"role": "user", "content": "Q1", "created_at": "2025-01-01T00:00:00", "length": 2},
        {
            "role": "assistant",
            "content": "A1",
            "created_at": "2025-01-01T00:01:00",
            "length": 2,
        },
        {"role": "user", "content": "Q2", "created_at": "2025-01-01T00:02:00", "length": 2},
    ]
    backend_client.get_conversation_history = AsyncMock(return_value=messages)

    manager = ConversationManager(backend_client)
    history = await manager.get_history(user_id=42)

    assert len(history) == 3
    assert [m["role"] for m in history] == ["user", "assistant", "user"]
    assert [m["content"] for m in history] == ["Q1", "A1", "Q2"]
