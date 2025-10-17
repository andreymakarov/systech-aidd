# Эксплуатация и трейблшутинг

Краткие инструкции по запуску/остановке и диагностике после реорганизации на backend + bot.

## Запуск сервисов

### Локальная разработка

#### Запуск backend
```bash
make run-backend
# или
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend будет доступен на http://localhost:8000

#### Запуск bot (в отдельном терминале)
```bash
make run
# или
uv run python -m bot
```

#### Запуск frontend dashboard (опционально)
```bash
make fe-dev
# или
cd frontend/web && pnpm dev
```
Dashboard будет доступен на http://localhost:3000

### Docker Compose (рекомендуется)

#### Запуск всех сервисов
```bash
docker-compose up -d
```
- `backend` на порту 8000
- `bot` подключается к backend

#### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Только bot
docker-compose logs -f bot
```

#### Остановка
```bash
docker-compose down
```

#### Пересборка после изменений кода
```bash
docker-compose up -d --build
```

## Миграции базы данных

### Проверка текущей версии
```bash
cd backend
alembic current
```

### Применение миграций
```bash
cd backend
alembic upgrade head
```

### Откат миграции
```bash
cd backend
alembic downgrade -1  # на одну версию назад
```

### Создание новой миграции
```bash
cd backend
alembic revision --autogenerate -m "описание изменений"
# Проверьте сгенерированный файл в backend/alembic/versions/
alembic upgrade head
```

## Логи

### Backend
- **Уровень:** INFO по умолчанию
- **Формат:** uvicorn access logs + application logs
- **Вывод:** stdout/stderr (видно в docker-compose logs)
- **Важные события:**
  - Startup: "Application startup complete"
  - Requests: "POST /api/v1/messages"
  - Errors: HTTP exceptions, database errors

### Bot
- **Уровень:** INFO
- **Формат:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Вывод:** stdout/stderr
- **Важные события:**
  - Startup: "Бот запущен"
  - User actions: "User {id} sent message ({len} chars)"
  - LLM calls: "Sending request to LLM (model: ...)"
  - Errors: "Error processing message", "Failed to create message"

## Health Checks

### Backend Health
```bash
curl http://localhost:8000/api/v1/stats?period=day
```
Должен вернуть JSON со статистикой (200 OK)

### Bot Health
Отправьте `/start` боту в Telegram - должен ответить приветственным сообщением

### Frontend Health
```bash
curl http://localhost:3000
```
Должен вернуть HTML страницу (200 OK)

## Типовые проблемы

### 1. Bot не может подключиться к backend

**Симптомы:**
```
Failed to get conversation history: Connection refused
Failed to create message: Connection refused
```

**Причины:**
- Backend не запущен
- Неверный `BACKEND_URL`
- Порт 8000 занят

**Решение:**
```bash
# Проверьте, что backend запущен
curl http://localhost:8000/api/v1/stats?period=day

# Проверьте BACKEND_URL в .env
echo $BACKEND_URL  # должно быть http://localhost:8000 (локально)

# В Docker проверьте логи backend
docker-compose logs backend
```

### 2. Database migration errors

**Симптомы:**
```
alembic.util.exc.CommandError: Can't locate revision identified by '...'
```

**Причины:**
- Несоответствие версии БД и миграций
- БД создана вручную без alembic

**Решение:**
```bash
cd backend

# Посмотрите текущую версию
alembic current

# Если БД пустая, примените все миграции
alembic upgrade head

# Если несоответствие, сбросьте и пересоздайте
rm -f data/bot.db
alembic upgrade head
```

### 3. CORS errors в frontend

**Симптомы:**
```
Access to fetch at 'http://localhost:8000/api/v1/stats' blocked by CORS policy
```

**Решение:**
```bash
# Добавьте origin фронтенда в .env
STATS_API_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Перезапустите backend
```

### 4. Отсутствуют обязательные переменные окружения

**Симптомы:**
```
ValueError: Обязательная переменная окружения TELEGRAM_BOT_TOKEN не установлена
```

**Решение:**
```bash
# Создайте .env из шаблона
cp .env.example .env

# Заполните обязательные переменные
TELEGRAM_BOT_TOKEN=your_token_here
OPENROUTER_API_KEY=your_api_key_here
```

### 5. LLM API errors

**Симптомы:**
```
Error calling LLM API: HTTPError: 401 Unauthorized
```

**Причины:**
- Неверный `OPENROUTER_API_KEY`
- Истёк баланс на OpenRouter
- Сетевая недоступность

**Решение:**
```bash
# Проверьте API key
echo $OPENROUTER_API_KEY

# Проверьте баланс на OpenRouter.ai

# Проверьте сетевую доступность
curl https://openrouter.ai/api/v1/models
```

### 6. Docker volume permissions

**Симптомы:**
```
PermissionError: [Errno 13] Permission denied: '/app/backend/data/bot.db'
```

**Решение:**
```bash
# Создайте директорию data с правильными правами
mkdir -p backend/data
chmod 777 backend/data  # или настройте user/group в Docker

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d
```

### 7. Port already in use

**Симптомы:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Решение:**
```bash
# Найдите процесс на порту 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Остановите процесс или измените порт в docker-compose.yml
ports:
  - "8001:8000"  # host:container
```

## Мониторинг

### Ключевые метрики

#### Backend
- HTTP request rate
- HTTP error rate (4xx, 5xx)
- Database query time
- Active connections

#### Bot
- Messages processed per minute
- LLM call latency
- Backend API call latency
- Error rate

### Простой мониторинг через логи

```bash
# Количество обработанных сообщений (bot)
docker-compose logs bot | grep "sent message" | wc -l

# HTTP ошибки (backend)
docker-compose logs backend | grep "ERROR"

# LLM вызовы (bot)
docker-compose logs bot | grep "LLM"
```

## Резервное копирование

### База данных

```bash
# Остановите backend для консистентности
docker-compose stop backend

# Создайте резервную копию
cp backend/data/bot.db backend/data/bot.db.backup.$(date +%Y%m%d_%H%M%S)

# Или сделайте dump
sqlite3 backend/data/bot.db .dump > backup.sql

# Запустите backend обратно
docker-compose start backend
```

### Восстановление

```bash
# Из файла
cp backend/data/bot.db.backup.20250117_120000 backend/data/bot.db

# Или из dump
sqlite3 backend/data/bot.db < backup.sql

# Перезапустите backend
docker-compose restart backend
```

## Обновление зависимостей

### Python packages
```bash
# Обновите pyproject.toml
# Затем пересоберите контейнеры
docker-compose up -d --build

# Или локально
uv sync --all-extras
```

### Frontend packages
```bash
cd frontend/web
pnpm update
pnpm install
```

## Graceful Shutdown

### Локальный процесс
```bash
# Отправьте SIGINT (Ctrl+C)
# Bot обработает KeyboardInterrupt и выполнит bot.stop()
```

### Docker Compose
```bash
# Graceful stop (10s timeout)
docker-compose stop

# Force stop
docker-compose kill
```

## Отладка

### Backend Debug Mode
```bash
# Запустите с debug логами
cd backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### Bot Debug Mode
```python
# В bot/__main__.py измените уровень логирования
logging.basicConfig(level=logging.DEBUG, ...)
```

### Проверка SQL запросов
```bash
# Включите SQL echo в backend/db/session.py
engine = create_async_engine(get_database_url(), echo=True, future=True)
```

## См. также
- [Architecture Overview](./architecture-overview.md) — Архитектура сервисов
- [Configuration Guide](./configuration-and-secrets.md) — Настройка окружения
- [Getting Started](./getting-started.md) — Первый запуск
- [Development Process](./development-process.md) — Процесс разработки
