# Модель данных и состояние

Кратко: что хранится и как используется (MVP, текущее состояние).

## История диалога
- Класс: `ConversationManager`.
- Хранение: in-memory `dict[int, list[dict[str, str]]]`.
- Сообщение: `{ "role": "user|assistant|system", "content": str }`.
- Операции: `get_history(user_id)`, `add_message(user_id, role, content)`, `clear_history(user_id)`.
- Особенности: данные теряются при перезапуске.

## Системный промпт / Роль
- Источник по умолчанию: файл `prompts/role.txt` (через `RoleManager`).
- Кэширование: роль читается из файла и кэшируется в памяти.
- Fallback: при отсутствующем `RoleManager` используется `Config.system_prompt`.

## Конфигурация
- Класс: `Config`.
- Обязательные: `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`.
- Опциональные (с дефолтами): `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `ROLE_PROMPT_FILE`.

## Ответ LLM
- Источник: OpenRouter через OpenAI SDK (`chat.completions.create`).
- Формирование входа: `[system] + history + [user]`.
- В ответе используется первый выбор `choices[0].message.content`.

