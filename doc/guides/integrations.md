# Интеграции

Кратко о внешних зависимостях и их использовании (текущее состояние).

## Telegram (aiogram 3.x)
- Транспорт: polling (ADR-002). Вебхуки не используются.
- Инициализация: `Bot`, `Dispatcher`, регистрация хендлеров.
- Обработчики: `/start`, `/role`, `/clear`, текст/нетекст.

## OpenRouter (OpenAI SDK)
- Клиент: `AsyncOpenAI`.
- Метод: `chat.completions.create`.
- Модель: берётся из `OPENROUTER_MODEL` (по умолчанию `openai/gpt-4o-mini`).
- Базовый URL: `OPENROUTER_BASE_URL` (по умолчанию `https://openrouter.ai/api/v1`).

## Обработка ошибок
- Ошибки LLM логируются в `LLMClient` и пробрасываются.
- В `MessageHandler` ошибки LLM оборачиваются в понятное сообщение пользователю.

## Схема взаимодействий
```mermaid
%%{init: {"theme":"base","themeVariables": {"background":"#000000","primaryTextColor":"#FFFFFF","lineColor":"#FFFFFF","secondaryColor":"#111111","tertiaryColor":"#222222"}}}%%
flowchart LR
    User((Пользователь)) -->|Telegram| TG[Telegram]
    TG -->|Polling| Bot[TelegramBot (aiogram)]
    Bot --> H[MessageHandler]
    H --> L[LLMClient\n(OpenRouter)]
    L -->|chat.completions| OR[(OpenRouter API)]
    H --> CM[ConversationManager]
    R[RoleManager] --> H
```

