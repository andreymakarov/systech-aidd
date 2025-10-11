"""Integration tests for LLMClient with HTTP mocking"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.config import Config
from bot.llm_client import LLMClient


async def test_generate_response_success(mock_config: Config) -> None:
    """Успешный ответ от LLM API"""
    # Создаем мок для AsyncOpenAI client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a test response from LLM"
    mock_client.chat.completions.create.return_value = mock_response

    # Создаем LLMClient и подменяем реальный клиент на мок
    llm_client = LLMClient(mock_config)
    llm_client.client = mock_client

    # Выполняем запрос
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    result = await llm_client.generate_response(messages)

    # Проверяем результат
    assert result == "This is a test response from LLM"
    
    # Проверяем, что метод был вызван один раз с правильными параметрами
    mock_client.chat.completions.create.assert_called_once_with(
        model=mock_config.openrouter_model,
        messages=messages,
    )


async def test_generate_response_api_error(mock_config: Config) -> None:
    """Ошибка при вызове LLM API"""
    # Создаем мок, который выбрасывает исключение
    mock_client = AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("API connection error")

    # Создаем LLMClient и подменяем клиент
    llm_client = LLMClient(mock_config)
    llm_client.client = mock_client

    # Проверяем, что исключение пробрасывается
    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(Exception, match="API connection error"):
        await llm_client.generate_response(messages)


async def test_generate_response_empty_content(mock_config: Config) -> None:
    """LLM возвращает пустой ответ (None)"""
    # Создаем мок с пустым content
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = None
    mock_client.chat.completions.create.return_value = mock_response

    # Создаем LLMClient и подменяем клиент
    llm_client = LLMClient(mock_config)
    llm_client.client = mock_client

    # Проверяем, что выбрасывается ValueError
    messages = [{"role": "user", "content": "Hello"}]
    with pytest.raises(ValueError, match="LLM returned empty response"):
        await llm_client.generate_response(messages)

