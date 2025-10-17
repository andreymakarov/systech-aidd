# Тур по репозиторию

Мини-гид по ключевым файлам и папкам.

## Каталоги
- `src/bot/`
  - `__main__.py` — точка входа, загрузка `.env`, запуск.
  - `bot.py` — инициализация aiogram `Bot`/`Dispatcher`, регистрация хендлеров.
  - `handlers.py` — обработчики `/start`, `/role`, `/clear`, текст/нетекст.
  - `llm_client.py` — клиент OpenRouter (OpenAI SDK).
  - `conversation.py` — in-memory история диалогов.
  - `config.py` — конфигурация из env.
  - `role_manager.py` — роль из файла и кэш.
- `tests/` — тесты unit/integration, фикстуры.
- `docs/` — README/vision/ADR/планы.
- `prompts/` — `role.txt` (дефолтная роль), примеры.

## Метаданные
- `pyproject.toml` — зависимости, ruff/mypy/pytest/coverage настройки.
- `Makefile` — `install`, `run`, `format`, `lint`, `test`, `qa`.

