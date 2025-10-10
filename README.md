# Systech AIDD - LLM-ассистент для Telegram

Минималистичный Telegram-бот с интеграцией LLM для проверки концепции.

## Требования

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - менеджер зависимостей

## Быстрый старт

### 1. Установка зависимостей

```bash
make install
```

### 2. Настройка

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните обязательные параметры:
- `TELEGRAM_BOT_TOKEN` - токен бота от [@BotFather](https://t.me/botfather)
- `OPENROUTER_API_KEY` - API ключ от [OpenRouter](https://openrouter.ai/)

### 3. Запуск

```bash
make run
```

## Доступные команды

- `/start` - приветствие и список команд
- `/clear` - очистить историю диалога

## Структура проекта

```
systech-aidd/
├── src/bot/           # Исходный код бота
│   ├── config.py      # Конфигурация
│   ├── bot.py         # Telegram бот
│   ├── handlers.py    # Обработчики сообщений
│   ├── llm_client.py  # Клиент для LLM
│   └── conversation.py # Управление историей
├── docs/              # Документация
├── .env               # Конфигурация (не в git)
└── pyproject.toml     # Зависимости проекта
```

## Технологии

- **aiogram 3.x** - Telegram Bot API
- **OpenAI client** - для работы с OpenRouter
- **python-dotenv** - управление переменными окружения

## Документация

- [Техническое видение](docs/vision.md)
- [План разработки](docs/tasklist.md)
- [ADR (Architecture Decision Records)](docs/adr/)

