"""Unit tests for Config"""

import pytest

from bot.config import Config


def test_config_with_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Успешная загрузка конфигурации с обязательными переменными"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token_123")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_456")
    
    config = Config()
    
    assert config.telegram_bot_token == "test_bot_token_123"
    assert config.openrouter_api_key == "test_api_key_456"


def test_config_missing_telegram_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Падение при отсутствии TELEGRAM_BOT_TOKEN"""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    # TELEGRAM_BOT_TOKEN не устанавливаем
    
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        Config()


def test_config_missing_openrouter_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Падение при отсутствии OPENROUTER_API_KEY"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    # OPENROUTER_API_KEY не устанавливаем
    
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        Config()


def test_config_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Значения по умолчанию для необязательных параметров"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    
    config = Config()
    
    # Проверяем значения по умолчанию
    assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert config.openrouter_model == "openai/gpt-4o-mini"
    assert "AI-ассистент" in config.system_prompt


def test_config_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Переопределение значений по умолчанию через env переменные"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_bot_token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://custom.api.url")
    monkeypatch.setenv("OPENROUTER_MODEL", "custom/model-name")
    monkeypatch.setenv("SYSTEM_PROMPT", "Custom system prompt")
    
    config = Config()
    
    assert config.openrouter_base_url == "https://custom.api.url"
    assert config.openrouter_model == "custom/model-name"
    assert config.system_prompt == "Custom system prompt"


def test_config_empty_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Падение при пустых строках в обязательных переменных"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    
    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        Config()

