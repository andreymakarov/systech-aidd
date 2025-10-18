# Systech AIDD - LLM-ассистент для Telegram

[![Docker Build](https://github.com/andreymakarov/systech-aidd/actions/workflows/build.yml/badge.svg)](https://github.com/andreymakarov/systech-aidd/actions/workflows/build.yml)

Минималистичный Telegram-бот с интеграцией LLM и REST API бэкендом. Микросервисная архитектура с разделением на bot и backend.

## Возможности

✅ Ответы на вопросы через LLM (OpenRouter API)  
✅ Поддержка контекста диалога для каждого пользователя  
✅ Настраиваемая роль бота через файл конфигурации  
✅ Очистка истории диалога по команде  
✅ Асинхронная архитектура  
✅ REST API для управления данными  
✅ Персистентное хранение истории (SQLite)  
✅ Покрытие тестами 88%  
✅ Dashboard для статистики (Next.js)

## Требования

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - менеджер зависимостей
- Docker и Docker Compose (для контейнеризации)
- Telegram Bot Token
- OpenRouter API Key

## Быстрый старт

### Локальная разработка

#### 1. Установка зависимостей

```bash
make install
```

Или напрямую через uv:
```bash
uv sync --all-extras
```

#### 2. Получение токенов

**Telegram Bot Token:**
1. Откройте [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

**OpenRouter API Key:**
1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/)
2. Перейдите в [Keys](https://openrouter.ai/keys)
3. Создайте новый API ключ
4. Скопируйте ключ

#### 3. Настройка

Создайте файл `.env` в корне проекта:

```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_api_key_here

# Backend API (локальная разработка)
BACKEND_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./backend/data/bot.db

# Необязательные параметры
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini
ROLE_PROMPT_FILE=prompts/role.txt
STATS_COLLECTOR=real
```

#### 4. Запуск

**Запуск backend API:**
```bash
make run-backend
```
Backend будет доступен на http://localhost:8000

**Запуск бота (в отдельном терминале):**
```bash
make run
```

**Запуск frontend dashboard (опционально):**
```bash
make fe-dev
```
Dashboard будет доступен на http://localhost:3000

Для остановки нажмите `Ctrl+C` в каждом терминале.

### Docker Compose (рекомендуется для продакшена)

#### Требования

- Docker Desktop 4.0+ (для Windows)
- Docker Compose v2.0+
- Минимум 4GB RAM

#### 1. Настройка

Создайте файл `.env` в корне проекта и заполните необходимые переменные:

```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_api_key_here

# Backend API (для Docker используется имя сервиса)
BACKEND_URL=http://backend:8000
DATABASE_URL=sqlite+aiosqlite:///./backend/data/bot.db

# Необязательные параметры
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini
ROLE_PROMPT_FILE=prompts/role.txt
STATS_COLLECTOR=real
```

#### 2. Запуск всех сервисов

```bash
docker-compose up -d --build
```

Это запустит три сервиса:
- **backend** на порту 8000 (REST API + SQLite база данных)
- **bot** (Telegram бот, подключается к backend)
- **frontend** на порту 3000 (Next.js dashboard для статистики)

Первый запуск займет несколько минут для сборки образов.

#### 3. Проверка статуса

```bash
# Проверить статус всех сервисов
docker-compose ps

# Ожидаемый вывод:
# NAME                STATE               PORTS
# backend             running             0.0.0.0:8000->8000/tcp
# bot                 running
# frontend            running             0.0.0.0:3000->3000/tcp
```

#### 4. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только bot
docker-compose logs -f bot

# Только frontend
docker-compose logs -f frontend

# Последние 100 строк с временными метками
docker-compose logs --tail=100 -t
```

#### 5. Доступ к сервисам

После успешного запуска:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:3000

#### 6. Остановка сервисов

```bash
# Остановить без удаления контейнеров
docker-compose stop

# Остановить и удалить контейнеры (база данных сохранится)
docker-compose down

# Удалить всё включая volumes (ВНИМАНИЕ: удалит базу данных!)
docker-compose down -v
```

#### 7. Обновление и перезапуск

```bash
# Пересобрать образы после изменений в коде
docker-compose up -d --build

# Перезапустить конкретный сервис
docker-compose restart backend

# Пересобрать только один сервис
docker-compose up -d --build frontend
```

#### Устранение неполадок

**Порт уже используется:**
```
Error: port is already allocated
```
Решение: Остановите процесс, использующий порт, или измените порт в `docker-compose.yml`.

**Docker Desktop не запущен (Windows):**
```
error connecting to docker daemon
```
Решение: Запустите Docker Desktop и дождитесь полной загрузки.

**База данных не сохраняется:**
Убедитесь, что директория `backend/data` существует и доступна для записи. Volume автоматически сохраняет данные между перезапусками.

**Frontend не подключается к backend:**
Убедитесь, что переменная `NEXT_PUBLIC_STATS_API_URL` указывает на `http://localhost:8000/api/v1` (не на `http://backend:8000`, так как frontend обращается из браузера).

### Использование образов из GitHub Container Registry

Образы автоматически публикуются в GitHub Container Registry (GHCR) при обновлении ветки `release`. Это позволяет запускать приложение без локальной сборки.

#### Доступные образы

Все образы доступны публично без авторизации:

- `ghcr.io/andreymakarov/systech-aidd-bot:latest`
- `ghcr.io/andreymakarov/systech-aidd-backend:latest`
- `ghcr.io/andreymakarov/systech-aidd-frontend:latest`

#### Запуск из registry

```bash
# 1. Pull образов (опционально, docker-compose сделает это автоматически)
docker pull ghcr.io/andreymakarov/systech-aidd-bot:latest
docker pull ghcr.io/andreymakarov/systech-aidd-backend:latest
docker pull ghcr.io/andreymakarov/systech-aidd-frontend:latest

# 2. Запуск всех сервисов из registry
docker-compose -f docker-compose.prod.yml up -d

# 3. Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# 4. Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# 5. Остановка
docker-compose -f docker-compose.prod.yml down
```

#### Различия между режимами

**Локальная разработка** (`docker-compose.yml`):
- Собирает образы из исходного кода
- Подходит для разработки и отладки
- Команда: `docker-compose up -d --build`

**Production** (`docker-compose.prod.yml`):
- Использует готовые образы из registry
- Быстрый запуск без сборки
- Подходит для развертывания на серверах
- Команда: `docker-compose -f docker-compose.prod.yml up -d`

#### Версии образов

Доступны два тега для каждого образа:

- `latest` - последняя стабильная версия из ветки `release`
- `sha-{commit}` - конкретная версия для определенного коммита

Пример использования конкретной версии:
```bash
docker pull ghcr.io/andreymakarov/systech-aidd-bot:sha-abc123def456
```

#### CI/CD Pipeline

Образы автоматически собираются и публикуются через GitHub Actions:

- **Push в `main`**: только сборка и проверка
- **Push в `release`**: сборка + публикация в GHCR

Статус сборки: [![Docker Build](https://github.com/andreymakarov/systech-aidd/actions/workflows/build.yml/badge.svg)](https://github.com/andreymakarov/systech-aidd/actions/workflows/build.yml)

## Использование

### Команды бота

- `/start` - приветствие и справка по командам
- `/role` - показать текущую роль бота
- `/clear` - очистить историю диалога и начать с чистого листа

### Примеры использования

1. **Простой вопрос:**
   ```
   Пользователь: Привет! Как дела?
   Бот: Здравствуйте! У меня всё хорошо, спасибо! Чем могу помочь?
   ```

2. **Контекстный диалог:**
   ```
   Пользователь: Расскажи о Python
   Бот: Python - это высокоуровневый язык программирования...
   
   Пользователь: А для чего он используется?
   Бот: Python используется для веб-разработки, анализа данных...
   ```

3. **Очистка истории:**
   ```
   Пользователь: /clear
   Бот: История диалога очищена
   ```

### Особенности

- **Персистентная история**: история диалогов сохраняется в SQLite БД
- **Изолированные пользователи**: каждый пользователь имеет свою независимую историю
- **REST API**: все данные доступны через HTTP API
- **Только текст**: бот работает только с текстовыми сообщениями (фото, файлы игнорируются)
- **Микросервисная архитектура**: бот и backend - независимые сервисы

## Архитектура

Проект построен на микросервисной архитектуре с разделением ответственности:

```
┌─────────────────┐
│   Telegram      │
│     Users       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      HTTP REST      ┌──────────────────┐
│   Bot Service   │◄────────────────────►│ Backend Service  │
│   (bot/)        │                      │   (backend/)     │
│                 │                      │                  │
│  - Aiogram      │                      │  - FastAPI       │
│  - LLM Client   │                      │  - SQLAlchemy    │
│  - Handlers     │                      │  - SQLite DB     │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ Database Volume │
                                         │ (persisted)     │
                                         └─────────────────┘
```

### Структура проекта

```
systech-aidd/
├── backend/                    # Backend service (FastAPI)
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── routers/
│   │   │   ├── messages.py    # Message CRUD API
│   │   │   └── stats.py       # Statistics API
│   │   ├── schemas/           # Pydantic models
│   │   ├── collectors/        # Stats collectors
│   │   └── models.py          # Domain models
│   ├── db/
│   │   ├── models.py          # SQLAlchemy ORM
│   │   └── session.py         # DB session factory
│   ├── alembic/               # Database migrations
│   ├── data/                  # SQLite database (gitignored)
│   │   └── bot.db
│   └── Dockerfile
│
├── bot/                       # Bot service (Telegram)
│   ├── __main__.py           # Entry point
│   ├── bot.py                # Aiogram setup
│   ├── config.py             # Configuration
│   ├── backend_client.py     # HTTP client for backend API
│   ├── conversation.py       # Conversation manager
│   ├── handlers.py           # Message handlers
│   ├── llm_client.py         # OpenRouter client
│   ├── role_manager.py       # Role management
│   └── Dockerfile
│
├── frontend/                  # Frontend service (Next.js)
│   └── web/
│       ├── app/              # Next.js app
│       ├── components/       # React components
│       └── lib/              # API clients
│
├── tests/                    # Unit and integration tests
├── doc/                      # Documentation
│   ├── guides/              # User guides
│   └── adr/                 # Architecture Decision Records
├── prompts/                 # AI role prompts
├── docker-compose.yml       # Multi-service orchestration
├── Makefile                 # Development commands
└── pyproject.toml           # Python dependencies
```

## API Endpoints

Backend предоставляет REST API на `http://localhost:8000`:

### Messages API

- `POST /api/v1/messages` - создать сообщение
- `GET /api/v1/conversations/{user_id}/messages` - получить историю
- `DELETE /api/v1/conversations/{user_id}/messages` - очистить историю

### Stats API

- `GET /api/v1/stats?period={day|week|month}` - получить статистику

Подробности в [doc/guides/stats-api.md](doc/guides/stats-api.md)

## Команды разработки

### Backend
```bash
make run-backend       # Запустить backend API
make test             # Запустить тесты
make lint             # Проверить код (ruff + mypy)
make format           # Форматировать код
make qa               # Полная проверка (format + lint + test)
```

### Bot
```bash
make run              # Запустить бота
```

### Frontend
```bash
make fe-dev           # Dev server
make fe-build         # Production build
make fe-test          # Запустить тесты
make fe-lint          # ESLint
```

### Docker
```bash
docker-compose up -d --build    # Собрать и запустить
docker-compose logs -f          # Просмотр логов
docker-compose down             # Остановить
```

## Технологии

### Backend
- **FastAPI** - современный асинхронный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с async поддержкой
- **Alembic** - миграции базы данных
- **SQLite** - встроенная БД (легко мигрировать на PostgreSQL)
- **Pydantic v2** - валидация данных

### Bot
- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **OpenAI Python client** - для работы с OpenRouter API
- **httpx** - асинхронный HTTP клиент
- **python-dotenv** - управление переменными окружения

### Frontend
- **Next.js 15** - React фреймворк
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **Recharts** - графики и визуализации
- **shadcn/ui** - UI компоненты

### Dev Tools
- **uv** - быстрый менеджер зависимостей Python
- **ruff** - линтер и форматтер
- **mypy** - статическая типизация
- **pytest** - тестирование
- **Docker Compose** - оркестрация контейнеров

## Настройка роли бота

Роль бота определяется в файле `prompts/role.txt`. Вы можете изменить содержимое этого файла, чтобы кастомизировать поведение бота:

```txt
Ты - профессиональный AI-ассистент, специализирующийся на помощи программистам.

Твои задачи:
- Отвечать на технические вопросы четко и по существу
- Предоставлять примеры кода с пояснениями
- Помогать с отладкой и рефакторингом

Стиль общения: дружелюбный, но профессиональный.
```

Чтобы использовать другой файл с ролью:
```bash
ROLE_PROMPT_FILE=prompts/custom_role.txt
```

## База данных

### Миграции

```bash
cd backend
alembic upgrade head           # Применить миграции
alembic revision --autogenerate -m "description"  # Создать миграцию
alembic current                # Текущая версия
```

### Расположение БД

- **Локально**: `./backend/data/bot.db`
- **Docker**: `/app/backend/data/bot.db` (примонтирован к хосту)

База данных персистентна и сохраняется между перезапусками контейнеров.

## Логирование

### Backend
```
INFO:     Application startup complete.
INFO:     127.0.0.1:54321 - "GET /api/v1/stats?period=day HTTP/1.1" 200 OK
```

### Bot
```
2025-01-17 15:30:45 - root - INFO - Инициализация компонентов...
2025-01-17 15:30:45 - root - INFO - Запуск бота...
2025-01-17 15:30:45 - root - INFO - Бот запущен
2025-01-17 15:30:50 - root - INFO - User 12345 sent message (15 chars)
2025-01-17 15:30:50 - root - INFO - Sending request to LLM (model: openai/gpt-4o-mini)
2025-01-17 15:30:52 - root - INFO - LLM response received (120 chars)
2025-01-17 15:30:52 - root - INFO - Response sent to user 12345
```

## Обработка ошибок

- **Ошибки конфигурации**: сервис не запустится, выведет понятное сообщение
- **Ошибки LLM API**: пользователь получит сообщение об ошибке, бот продолжит работать
- **Ошибки backend API**: бот логирует ошибку и уведомляет пользователя
- **Graceful shutdown**: при `Ctrl+C` или SIGTERM сервисы корректно завершат работу

## Документация

### Guides
- [Architecture Overview](doc/guides/architecture-overview.md) - обзор архитектуры с диаграммами
- [Codebase Tour](doc/guides/codebase-tour.md) - экскурсия по коду
- [Configuration](doc/guides/configuration-and-secrets.md) - конфигурация и секреты
- [Stats API](doc/guides/stats-api.md) - документация API
- [Runbook](doc/guides/runbook.md) - эксплуатация и troubleshooting
- [Getting Started](doc/guides/getting-started.md) - первые шаги
- [Testing](doc/guides/testing.md) - стратегия тестирования

### ADRs (Architecture Decision Records)
- [ADR-011: Backend-Owned DB and REST API](doc/adr/ADR-011-backend-owned-db-and-rest-api.md) - текущая архитектура
- [Все ADRs](doc/adr/) - история архитектурных решений

### Vision & Roadmap
- [Vision](doc/vision.md) - видение проекта
- [Roadmap](doc/roadmap.md) - план развития

## Troubleshooting

### Docker Desktop не запущен
```
error: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```
**Решение:** Запустите Docker Desktop и подождите его полной загрузки.

### Backend недоступен
```
Failed to get conversation history: Connection refused
```
**Решение:** Убедитесь, что backend запущен на порту 8000.

### База данных заблокирована
```
OperationalError: database is locked
```
**Решение:** Остановите все процессы, использующие БД, или используйте PostgreSQL для продакшена.

Подробнее в [doc/guides/runbook.md](doc/guides/runbook.md)

## Миграция с SQLite на PostgreSQL

Для продакшена рекомендуется PostgreSQL:

```bash
# Обновите DATABASE_URL в .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# Установите драйвер
pip install asyncpg

# Примените миграции
cd backend && alembic upgrade head
```

## Лицензия

MIT

## Автор

Systech AIDD - современный Telegram бот с LLM и микросервисной архитектурой
