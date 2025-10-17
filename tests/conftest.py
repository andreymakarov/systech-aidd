"""Shared fixtures for tests"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.config import Config
from bot.conversation import ConversationManager
from bot.llm_client import LLMClient


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Очищаем переменные окружения перед каждым тестом для изоляции"""
    # Удаляем потенциально существующие переменные окружения
    env_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "OPENROUTER_MODEL",
        "SYSTEM_PROMPT",
        "ROLE_PROMPT_FILE",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_config(monkeypatch: pytest.MonkeyPatch) -> Config:
    """Фикстура для Config с тестовыми значениями"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    return Config()


@pytest.fixture
def mock_conversation_manager() -> ConversationManager:
    """Фикстура для мока ConversationManager (async методы)."""
    manager = MagicMock(spec=ConversationManager)
    manager.get_history = AsyncMock(return_value=[])
    manager.add_message = AsyncMock(return_value=None)
    manager.clear_history = AsyncMock(return_value=None)
    return manager


@pytest.fixture
def mock_llm_client(mock_config: Config) -> Any:
    """Фикстура для мока LLMClient"""
    client = MagicMock(spec=LLMClient)
    client.config = mock_config
    client.generate_response = AsyncMock(return_value="Test LLM response")
    return client


@pytest.fixture
def mock_role_manager() -> Any:
    """Фикстура для мока RoleManager"""
    from bot.role_manager import RoleManager

    manager = MagicMock(spec=RoleManager)
    manager.load_role.return_value = "Ты - тестовый ассистент."
    manager.get_role_description.return_value = "🎭 **Моя роль:**\n\nТы - тестовый ассистент."
    return manager
