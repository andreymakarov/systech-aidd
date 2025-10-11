"""Shared fixtures for tests"""

import os

import pytest


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
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

