"""Integration tests for MessageHandler with mocked dependencies"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

from bot.conversation import ConversationManager
from bot.handlers import (
    ERROR_MESSAGE,
    HISTORY_CLEARED_MESSAGE,
    NON_TEXT_MESSAGE,
    WELCOME_TEXT,
    MessageHandler,
)
from bot.llm_client import LLMClient


async def test_handle_start_command(
    mock_llm_client: LLMClient, mock_conversation_manager: ConversationManager
) -> None:
    """Проверка отправки welcome text при команде /start"""
    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler с моками
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем команду
    await handler.handle_start_command(message)

    # Проверяем, что был отправлен WELCOME_TEXT
    message.answer.assert_called_once_with(WELCOME_TEXT)


async def test_handle_text_message(
    mock_llm_client: Any, mock_conversation_manager: ConversationManager
) -> None:
    """Обработка текстового сообщения - полный цикл"""
    # Настраиваем моки
    mock_llm_client.generate_response.return_value = "LLM response text"
    mock_conversation_manager.get_history.return_value = []

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.text = "Hello, bot!"
    message.chat.id = 67890
    message.bot = None  # Упрощаем - не проверяем typing action
    message.answer = AsyncMock()

    # Создаем handler
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем обработку
    await handler.handle_text_message(message)

    # Проверяем вызов get_history
    mock_conversation_manager.get_history.assert_called_once_with(12345)

    # Проверяем вызов generate_response с правильными параметрами
    mock_llm_client.generate_response.assert_called_once()
    call_args = mock_llm_client.generate_response.call_args[0][0]
    assert call_args[0]["role"] == "system"
    assert call_args[-1]["role"] == "user"
    assert call_args[-1]["content"] == "Hello, bot!"

    # Проверяем, что сообщения добавлены в историю
    assert mock_conversation_manager.add_message.call_count == 2
    # Первый вызов - сообщение пользователя
    mock_conversation_manager.add_message.assert_any_call(12345, "user", "Hello, bot!")
    # Второй вызов - ответ LLM
    mock_conversation_manager.add_message.assert_any_call(12345, "assistant", "LLM response text")

    # Проверяем, что ответ отправлен пользователю
    message.answer.assert_called_once_with("LLM response text")


async def test_handle_text_message_with_history(
    mock_llm_client: Any, mock_conversation_manager: ConversationManager
) -> None:
    """Обработка текстового сообщения с существующей историей"""
    # Настраиваем историю
    existing_history = [
        {"role": "user", "content": "Previous message"},
        {"role": "assistant", "content": "Previous response"},
    ]
    mock_conversation_manager.get_history.return_value = existing_history
    mock_llm_client.generate_response.return_value = "New response"

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.text = "New message"
    message.bot = None
    message.answer = AsyncMock()

    # Создаем handler
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем обработку
    await handler.handle_text_message(message)

    # Проверяем, что в запрос включена история
    call_args = mock_llm_client.generate_response.call_args[0][0]
    assert len(call_args) == 4  # system + 2 history + new message
    assert call_args[1] == {"role": "user", "content": "Previous message"}
    assert call_args[2] == {"role": "assistant", "content": "Previous response"}


async def test_handle_text_message_llm_error(
    mock_llm_client: Any, mock_conversation_manager: ConversationManager
) -> None:
    """Обработка ошибки при вызове LLM"""
    # Настраиваем мок для ошибки
    mock_llm_client.generate_response.side_effect = Exception("LLM API error")
    mock_conversation_manager.get_history.return_value = []

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.text = "Hello"
    message.bot = None
    message.answer = AsyncMock()

    # Создаем handler
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем обработку
    await handler.handle_text_message(message)

    # Проверяем, что пользователю отправлено сообщение об ошибке
    message.answer.assert_called_once_with(ERROR_MESSAGE)

    # Проверяем, что история НЕ была обновлена (т.к. ошибка)
    mock_conversation_manager.add_message.assert_not_called()


async def test_handle_clear_command(
    mock_llm_client: LLMClient, mock_conversation_manager: ConversationManager
) -> None:
    """Проверка очистки истории при команде /clear"""
    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем команду
    await handler.handle_clear_command(message)

    # Проверяем, что clear_history был вызван
    mock_conversation_manager.clear_history.assert_called_once_with(12345)

    # Проверяем, что отправлено подтверждение
    message.answer.assert_called_once_with(HISTORY_CLEARED_MESSAGE)


async def test_handle_non_text_message(
    mock_llm_client: LLMClient, mock_conversation_manager: ConversationManager
) -> None:
    """Обработка нетекстового сообщения (фото, стикер и т.д.)"""
    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем обработку
    await handler.handle_non_text_message(message)

    # Проверяем, что отправлено сообщение о работе только с текстом
    message.answer.assert_called_once_with(NON_TEXT_MESSAGE)


async def test_handle_role_command_success(
    mock_llm_client: LLMClient,
    mock_conversation_manager: ConversationManager,
    mock_role_manager: Any,
) -> None:
    """Успешное отображение роли при команде /role"""
    # Настраиваем мок RoleManager
    mock_role_manager.get_role_description.return_value = (
        "🎭 **Моя роль:**\n\nТы - тестовый ассистент."
    )

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler с RoleManager
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)
    handler.role_manager = mock_role_manager

    # Выполняем команду
    await handler.handle_role_command(message)

    # Проверяем, что get_role_description был вызван
    mock_role_manager.get_role_description.assert_called_once()

    # Проверяем, что описание роли отправлено с Markdown форматированием
    message.answer.assert_called_once()
    call_args = message.answer.call_args
    assert "🎭 **Моя роль:**" in call_args[0][0]
    assert call_args[1]["parse_mode"] == "Markdown"


async def test_handle_role_command_formats_nicely(
    mock_llm_client: LLMClient,
    mock_conversation_manager: ConversationManager,
    mock_role_manager: Any,
) -> None:
    """Красивое форматирование описания роли с эмодзи"""
    # Настраиваем мок с многострочной ролью
    role_description = """🎭 **Моя роль:**

Ты - профессиональный AI-ассистент.

Твои задачи:
- Помогать пользователю
- Быть вежливым"""

    mock_role_manager.get_role_description.return_value = role_description

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler с RoleManager
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)
    handler.role_manager = mock_role_manager

    # Выполняем команду
    await handler.handle_role_command(message)

    # Проверяем форматирование
    call_args = message.answer.call_args[0][0]
    assert "🎭" in call_args  # Эмодзи маски
    assert "**Моя роль:**" in call_args  # Жирный текст
    assert "задачи:" in call_args  # Многострочный контент
    assert call_args == role_description


async def test_handle_role_command_with_role_manager_error(
    mock_llm_client: LLMClient,
    mock_conversation_manager: ConversationManager,
    mock_role_manager: Any,
) -> None:
    """Обработка ошибки RoleManager при команде /role"""
    # Настраиваем мок для ошибки
    mock_role_manager.get_role_description.side_effect = FileNotFoundError("Role file not found")

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    # Создаем handler с RoleManager
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)
    handler.role_manager = mock_role_manager

    # Выполняем команду
    await handler.handle_role_command(message)

    # Проверяем, что пользователю отправлено сообщение об ошибке
    message.answer.assert_called_once()
    error_message = message.answer.call_args[0][0]
    assert "не удалось" in error_message.lower() or "ошибка" in error_message.lower()


async def test_handle_text_message_uses_role_from_manager(
    mock_llm_client: Any,
    mock_conversation_manager: ConversationManager,
    mock_role_manager: Any,
) -> None:
    """LLM использует роль из RoleManager вместо хардкода в Config"""
    # Настраиваем моки
    custom_role = "Ты - специализированный ассистент для тестирования."
    mock_role_manager.load_role.return_value = custom_role
    mock_conversation_manager.get_history.return_value = []
    mock_llm_client.generate_response.return_value = "Response"

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.text = "Test message"
    message.bot = None
    message.answer = AsyncMock()

    # Создаем handler с RoleManager
    handler = MessageHandler(mock_llm_client, mock_conversation_manager, mock_role_manager)

    # Выполняем обработку
    await handler.handle_text_message(message)

    # Проверяем, что load_role был вызван
    mock_role_manager.load_role.assert_called_once()

    # Проверяем, что системный промпт содержит роль из RoleManager
    call_args = mock_llm_client.generate_response.call_args[0][0]
    system_message = call_args[0]
    assert system_message["role"] == "system"
    assert system_message["content"] == custom_role


async def test_handle_text_message_without_role_manager_uses_config(
    mock_llm_client: Any,
    mock_conversation_manager: ConversationManager,
) -> None:
    """При отсутствии RoleManager используется system_prompt из Config"""
    # Настраиваем моки
    mock_conversation_manager.get_history.return_value = []
    mock_llm_client.generate_response.return_value = "Response"

    # Создаем мок для Message
    message = AsyncMock()
    message.from_user.id = 12345
    message.text = "Test message"
    message.bot = None
    message.answer = AsyncMock()

    # Создаем handler БЕЗ RoleManager
    handler = MessageHandler(mock_llm_client, mock_conversation_manager)

    # Выполняем обработку
    await handler.handle_text_message(message)

    # Проверяем, что системный промпт взят из Config
    call_args = mock_llm_client.generate_response.call_args[0][0]
    system_message = call_args[0]
    assert system_message["role"] == "system"
    # Должен использовать system_prompt из config (хардкод/fallback)
    assert "AI-ассистент" in system_message["content"]