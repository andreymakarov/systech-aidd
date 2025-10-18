# D0: Basic Docker Setup - Implementation Plan

**Sprint:** D0  
**Status:** ✅ Completed  
**Date:** October 18, 2025

## Цель

Запустить все сервисы (Bot, Backend, Frontend) локально через docker-compose одной командой.

## Выполненные работы

### 1. Создан Dockerfile для Frontend

**Файл:** `devops/Dockerfile.frontend`

- Multi-stage build (deps → builder → runner)
- Node.js 20 Alpine base image
- pnpm package manager
- Next.js standalone output для оптимального размера образа
- Non-root user для безопасности
- Порт 3000

**Изменения в Next.js:**
- Добавлена опция `output: 'standalone'` в `next.config.mjs`

### 2. Перемещены существующие Dockerfile

Dockerfiles перемещены в единую директорию `devops/`:
- `bot/Dockerfile` → `devops/Dockerfile.bot`
- `backend/Dockerfile` → `devops/Dockerfile.backend`

Содержимое файлов осталось без изменений.

### 3. Созданы .dockerignore файлы

Для каждого сервиса созданы специфичные ignore-файлы:

**devops/.dockerignore.bot:**
- Python artifacts (__pycache__, *.pyc, .venv)
- Testing/coverage (pytest_cache, htmlcov)
- IDE files (.vscode, .idea)
- Other services (backend/, frontend/)
- Environment files (.env*)

**devops/.dockerignore.backend:**
- Python artifacts
- Testing/coverage
- IDE files
- Other services (bot/, frontend/)
- Database directory (backend/data/)
- Environment files

**devops/.dockerignore.frontend:**
- Node artifacts (node_modules, .next)
- Testing files
- IDE files
- Other services (bot/, backend/)
- Environment files

### 4. Обновлен docker-compose.yml

Конфигурация включает все три сервиса:

**Backend:**
- Использует `devops/Dockerfile.backend`
- Порт 8000
- Volume для персистентности БД: `./backend/data:/app/backend/data`
- Автоматический запуск миграций при старте
- Environment variables для DB и stats

**Bot:**
- Использует `devops/Dockerfile.bot`
- Читает `.env` файл
- Зависит от backend
- Подключается к backend через Docker network

**Frontend (новый):**
- Использует `devops/Dockerfile.frontend`
- Порт 3000
- Environment: `NEXT_PUBLIC_STATS_API_URL=http://localhost:8000/api/v1`
- Зависит от backend
- Restart policy: unless-stopped

Все сервисы используют BuildKit для ускорения сборки.

### 5. Обновлена документация README.md

Добавлен расширенный раздел "Docker Compose" с:
- Требованиями (Docker Desktop 4.0+, Docker Compose v2.0+)
- Пошаговой инструкцией по настройке .env файла
- Командами для запуска всех сервисов
- Проверкой статуса сервисов
- Просмотром логов (общих и по сервисам)
- Доступом к сервисам (порты и URL)
- Командами остановки и перезапуска
- Секцией "Устранение неполадок" с типичными проблемами

## Архитектура

```
┌─────────────────────┐
│  docker-compose.yml │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────────┐
    │             │              │
    ▼             ▼              ▼
┌────────┐   ┌─────────┐   ┌──────────┐
│ Bot    │   │ Backend │   │ Frontend │
│ :---   │──▶│ :8000   │◀──│ :3000    │
└────────┘   └────┬────┘   └──────────┘
                  │
                  ▼
           ┌─────────────┐
           │ SQLite DB   │
           │ (volume)    │
           └─────────────┘
```

## Результаты

✅ Все сервисы успешно упакованы в Docker контейнеры  
✅ Запуск одной командой: `docker-compose up -d --build`  
✅ Персистентность данных через volume для БД  
✅ Изолированные .dockerignore для каждого сервиса  
✅ Полная документация в README.md  

## Команды для проверки

```bash
# Запуск всех сервисов
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Доступ к сервисам

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend Dashboard: http://localhost:3000

## Следующий спринт

D1: Build & Publish - автоматическая сборка и публикация образов в GitHub Container Registry.


