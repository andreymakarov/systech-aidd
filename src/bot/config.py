import os

from dotenv import load_dotenv


class Config:
    """Конфигурация приложения из переменных окружения"""

    def __init__(self) -> None:
        load_dotenv()

        # Обязательные параметры
        self.telegram_bot_token = self._get_required("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key = self._get_required("OPENROUTER_API_KEY")

        # Параметры с значениями по умолчанию
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "Ты - полезный AI-ассистент. Отвечай на вопросы пользователя четко и по существу.",
        )

    def _get_required(self, key: str) -> str:
        """Получить обязательный параметр или выбросить ошибку"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Обязательная переменная окружения {key} не установлена")
        return value
