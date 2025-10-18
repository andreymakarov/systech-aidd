# Конфигурации и секреты

Текущее состояние конфигурации и секретов после реорганизации.

## Переменные окружения

### Bot Service (`bot/`)

#### Обязательные
- `TELEGRAM_BOT_TOKEN` — Telegram bot token от @BotFather
- `OPENROUTER_API_KEY` — API ключ OpenRouter для LLM запросов

#### Опциональные (значения по умолчанию)
- `OPENROUTER_BASE_URL` → `https://openrouter.ai/api/v1`
- `OPENROUTER_MODEL` → `openai/gpt-4o-mini`
- `ROLE_PROMPT_FILE` → `prompts/role.txt`
- `SYSTEM_PROMPT` → Дефолтный системный промпт (deprecated, будет удалён)
- **`BACKEND_URL`** → `http://localhost:8000` (для локальной разработки)
  - В Docker Compose: `http://backend:8000` (через service name)

### Backend Service (`backend/`)

#### База данных
- **`DATABASE_URL`** → `sqlite+aiosqlite:///./backend/data/bot.db`
  - SQLAlchemy async connection string
  - Используется ORM и Alembic
  - Формат: `sqlite+aiosqlite:///<path_to_db>`

#### Stats API
- `STATS_COLLECTOR` → `real` (режим работы)
  - `real` — чтение из реальной БД
- `STATS_DB_URL` → `sqlite:///backend/data/bot.db`
  - Путь для RealStatCollector (без async префикса)
  - Используется для прямого sqlite3 доступа в статистике
- `STATS_API_CORS_ORIGINS` → `*`
  - CORS origins для API (разделены запятыми)
  - В продакшене указать конкретные домены

## Примеры конфигурации

### Локальная разработка

Создайте `.env` в корне проекта:

```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o-mini
ROLE_PROMPT_FILE=prompts/role.txt

# Backend URL (local)
BACKEND_URL=http://localhost:8000

# Backend Database
DATABASE_URL=sqlite+aiosqlite:///./backend/data/bot.db

# Stats Configuration
STATS_COLLECTOR=real
STATS_DB_URL=sqlite:///backend/data/bot.db
STATS_API_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Docker Compose

В `docker-compose.yml` переменные настраиваются автоматически:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=sqlite+aiosqlite:////app/backend/data/bot.db
      - STATS_COLLECTOR=${STATS_COLLECTOR:-real}
      - STATS_DB_URL=sqlite:///backend/data/bot.db

  bot:
    env_file: .env  # Загружает TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY
    environment:
      - BACKEND_URL=http://backend:8000  # Overrides .env
```

**Важно:** В Docker Compose `BACKEND_URL` автоматически переопределяется на `http://backend:8000` для использования внутренней сети Docker.

### Production (Kubernetes/Cloud)

Используйте секреты окружения платформы:

```yaml
# Kubernetes Secret example
apiVersion: v1
kind: Secret
metadata:
  name: bot-secrets
type: Opaque
stringData:
  TELEGRAM_BOT_TOKEN: "..."
  OPENROUTER_API_KEY: "..."
  BACKEND_URL: "http://backend-service:8000"
```

## Загрузка конфигурации

### Bot
- `.env` загружается в `bot/__main__.py` через `dotenv.load_dotenv()`
- Класс `Config` (в `bot/config.py`) читает переменные и валидирует обязательные
- `ValueError` выбрасывается при отсутствии обязательных переменных

### Backend
- Переменные читаются напрямую через `os.getenv()` в:
  - `backend/db/session.py` — `DATABASE_URL`
  - `backend/app/routers/stats.py` — `STATS_COLLECTOR`
  - `backend/app/collectors/real.py` — `STATS_DB_URL`
  - `backend/app/main.py` — `STATS_API_CORS_ORIGINS`

## Хранение секретов

### Локальная разработка
- Секреты хранятся в `.env` файле
- **`.env` НЕ хранится в Git** (см. `.gitignore`)
- Используйте `.env.example` как шаблон

### CI/CD
- Используйте секреты GitHub Actions / GitLab CI
- Инжектируйте через environment variables в pipeline

### Production
- Используйте менеджеры секретов:
  - AWS Secrets Manager
  - HashiCorp Vault
  - Kubernetes Secrets
  - Azure Key Vault
- **Никогда не храните секреты в коде или Docker images**

## Приоритет переменных

1. Environment variables (высший приоритет)
2. `.env` файл
3. Значения по умолчанию в коде

Пример:
```bash
# В .env
BACKEND_URL=http://localhost:8000

# В docker-compose.yml (переопределяет .env)
environment:
  - BACKEND_URL=http://backend:8000
```

## Валидация конфигурации

### Bot Config
```python
# bot/config.py
class Config:
    def __init__(self) -> None:
        self.telegram_bot_token = self._get_required("TELEGRAM_BOT_TOKEN")
        self.openrouter_api_key = self._get_required("OPENROUTER_API_KEY")
        # ...
    
    def _get_required(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Обязательная переменная окружения {key} не установлена")
        return value
```

### Backend Database URL
```python
# backend/db/session.py
def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./backend/data/bot.db")
```

## Режимы работы

### Development (локальная разработка)
```bash
STATS_COLLECTOR=real
BACKEND_URL=http://localhost:8000
```
- Real data from database for statistics
- Backend и bot запущены отдельно

### Integration (docker-compose)
```bash
STATS_COLLECTOR=real
BACKEND_URL=http://backend:8000
```
- Backend и bot в контейнерах
- Общая Docker сеть
- Volume mount для БД

### Production
```bash
STATS_COLLECTOR=real
BACKEND_URL=http://backend-service:8000
DATABASE_URL=postgresql://...  # или другая БД
```
- Реальная БД (PostgreSQL рекомендуется)
- Managed secrets
- Health checks и monitoring

## Миграция с SQLite на PostgreSQL

Для продакшена рекомендуется PostgreSQL:

```bash
# Обновите DATABASE_URL
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Установите asyncpg
pip install asyncpg

# Примените миграции
cd backend && alembic upgrade head
```

Alembic автоматически определит диалект по URL.

## Troubleshooting

### Bot не может подключиться к backend
```
Error: Failed to get conversation history: Connection refused
```
**Решение:** Проверьте `BACKEND_URL` и что backend запущен:
```bash
curl http://localhost:8000/api/v1/stats?period=day
```

### Alembic не находит models
```
ImportError: cannot import name 'Base' from 'backend.db.models'
```
**Решение:** Убедитесь что `prepend_sys_path = .` в `alembic.ini` и запускаете из корня проекта.

### CORS ошибки в frontend
```
Access to fetch blocked by CORS policy
```
**Решение:** Добавьте origin фронтенда в `STATS_API_CORS_ORIGINS`:
```bash
STATS_API_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## См. также
- [Architecture Overview](./architecture-overview.md) — Как компоненты используют конфигурацию
- [Getting Started](./getting-started.md) — Настройка окружения для разработки
- [ADR-007: Env-Based Configuration](../adr/ADR-007-env-based-configuration.md)
- [ADR-011: Backend-Owned DB and REST API](../adr/ADR-011-backend-owned-db-and-rest-api.md)
