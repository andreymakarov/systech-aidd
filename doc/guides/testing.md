# Тестирование

Текущее состояние тестовой инфраструктуры.

## Запуск
```bash
make test
```
Отчёт о покрытии: терминал + HTML в `htmlcov/`.

## Технологии
- `pytest`, `pytest-asyncio`, `pytest-cov`.
- Async-тесты: режим `asyncio_mode = auto`.

## Покрытие
- В README указано покрытие ~97%.
- В `pyproject.toml` настроен `--cov=src` и HTML отчёт.

## Что покрыто
- `ConversationManager`, `Config`, `LLMClient` (с моками), `MessageHandler`, `RoleManager`.

## Исключения покрытия
- `src/bot/__main__.py` и `src/bot/bot.py` исключены из покрытия (инициализационный код).

