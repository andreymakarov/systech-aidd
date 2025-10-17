# Конфигурации и секреты

Текущее состояние конфигурации и секретов.

## Переменные окружения
- Обязательные:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENROUTER_API_KEY`
- Опциональные (значения по умолчанию):
  - `OPENROUTER_BASE_URL` → `https://openrouter.ai/api/v1`
  - `OPENROUTER_MODEL` → `openai/gpt-4o-mini`
  - `ROLE_PROMPT_FILE` → `prompts/role.txt`

## Загрузка конфигурации
- `.env` загружается в `__main__` через `dotenv.load_dotenv()`.
- Класс `Config` читает переменные и валидирует обязательные.

## Хранение секретов
- Секреты хранятся в переменных окружения.
- Файл `.env` не хранится в репозитории.

