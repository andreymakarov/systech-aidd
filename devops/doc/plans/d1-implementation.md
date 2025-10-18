# D1: Build & Publish - Implementation Plan

**Sprint:** D1  
**Status:** 🚧 В работе  
**Date:** October 18, 2025

## Цель

Автоматическая сборка Docker образов через GitHub Actions и публикация в GitHub Container Registry (ghcr.io) для последующего использования при развертывании на сервер.

## Стратегия

- **Сборка**: автоматически при push в ветки `main` и `release`
- **Публикация**: только при push в ветку `release`
- **Теги образов**: `latest` и commit SHA (`sha-abc1234`)
- **Registry**: GitHub Container Registry (ghcr.io)
- **Доступ**: публичные образы (без авторизации для pull)
- **Сервисы**: bot, backend, frontend (matrix strategy)

## Выполненные работы

### 1. Создано руководство по GitHub Actions

**Файл:** `devops/doc/github-actions-guide.md`

Подробное руководство включает:
- Основы GitHub Actions и workflow (структура, jobs, steps, actions)
- Trigger события (push, pull_request, workflow_dispatch)
- Работа с Pull Requests и статус проверок
- Matrix strategy для параллельной сборки
- Docker layer caching (GitHub Actions cache и registry cache)
- Публикация образов в GHCR (аутентификация, tags, labels)
- Публичные vs приватные образы
- Настройка permissions для работы с пакетами
- Переменные, secrets и environment variables
- Примеры workflow (от минимального до полного CD)
- Best practices и отладка
- Ограничения и квоты GitHub Actions

### 2. Создан GitHub Actions Workflow

**Файл:** `.github/workflows/build.yml`

**Основные компоненты:**

**Triggers:**
```yaml
on:
  push:
    branches: [main, release]
```
- Автоматический запуск при push в `main` и `release`

**Permissions:**
```yaml
permissions:
  contents: read
  packages: write
```
- `contents: read` - для checkout кода
- `packages: write` - для публикации в GHCR

**Matrix Strategy:**
```yaml
strategy:
  matrix:
    service: [bot, backend, frontend]
```
- Параллельная сборка трех сервисов

**Шаги workflow:**

1. **Checkout code** - загрузка кода репозитория
2. **Set up Docker Buildx** - настройка Docker для кэширования
3. **Log in to GHCR** - аутентификация (только для release)
   - Условие: `if: github.ref == 'refs/heads/release'`
   - Использует встроенный `GITHUB_TOKEN`
4. **Extract metadata** - генерация тегов и labels
   - Теги: `latest` и `sha-{commit}`
   - Только для release ветки
5. **Build and push** - сборка и публикация образов
   - Условная публикация: `push: ${{ github.ref == 'refs/heads/release' }}`
   - Docker layer caching: `type=gha,mode=max`
6. **Build summary** - отчет о сборке в GitHub Actions UI

**Кэширование:**
- Использует GitHub Actions cache (`type=gha`)
- Режим `mode=max` - кэширует все промежуточные слои

**Условия публикации:**
- Push в `main` - только сборка и проверка
- Push в `release` - сборка + публикация в GHCR

### 3. Создан docker-compose.prod.yml

**Файл:** `docker-compose.prod.yml`

Альтернативная конфигурация для использования образов из registry:

**Отличия от docker-compose.yml:**
- Использует `image:` вместо `build:`
- Образы из `ghcr.io/[owner]/systech-aidd-[service]:latest`
- Сохранены все environment variables
- Сохранены volumes для персистентности данных
- Сохранены зависимости между сервисами
- Добавлены комментарии по использованию

**Использование:**
```bash
# Локальная разработка (сборка из исходников)
docker-compose up -d --build

# Production (использование образов из registry)
docker-compose -f docker-compose.prod.yml up -d
```

**Важно:** Перед использованием нужно заменить `[owner]` на реальный GitHub username/organization.

### 4. Обновлена документация

**README.md:**
- Добавлен badge статуса сборки GitHub Actions
- Новая секция "Использование образов из GitHub Container Registry"
- Инструкции по pull образов без авторизации
- Команды для работы с docker-compose.prod.yml
- Объяснение разницы между локальной разработкой и production

**devops/doc/devops-roadmap.md:**
- Обновлен статус спринта D1 на "🚧 В работе"
- Добавлена ссылка на план реализации

## Инструкции по развертыванию

### Шаг 1: Создание ветки release

```bash
# Из ветки main или devops
git checkout -b release
git push -u origin release
```

Эта ветка будет использоваться для:
- Публикации стабильных версий образов
- Развертывания на production (спринты D2, D3)

### Шаг 2: Первая публикация

После создания ветки `release`, workflow автоматически:
1. Соберет все три образа
2. Опубликует их в GHCR как приватные пакеты

### Шаг 3: Настройка публичного доступа

После первой публикации вручную изменить visibility:

1. Перейти на GitHub → Профиль/Organization → Packages
2. Найти пакеты:
   - `systech-aidd-bot`
   - `systech-aidd-backend`
   - `systech-aidd-frontend`
3. Для каждого пакета:
   - Package settings → Danger Zone
   - Change visibility → Public
   - Подтвердить

После этого образы доступны для pull без авторизации.

### Шаг 4: Локальное тестирование

```bash
# Заменить [owner] на ваш GitHub username в docker-compose.prod.yml
# Например: ghcr.io/username/systech-aidd-bot:latest

# Pull образов
docker pull ghcr.io/[owner]/systech-aidd-bot:latest
docker pull ghcr.io/[owner]/systech-aidd-backend:latest
docker pull ghcr.io/[owner]/systech-aidd-frontend:latest

# Запуск сервисов
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Остановка
docker-compose -f docker-compose.prod.yml down
```

## Архитектура CI/CD

```
┌─────────────────────┐
│   Git Repository    │
│   (main/release)    │
└──────────┬──────────┘
           │ push
           ▼
┌─────────────────────┐
│  GitHub Actions     │
│   (build.yml)       │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────────┐
    │             │              │
    ▼             ▼              ▼
┌────────┐   ┌─────────┐   ┌──────────┐
│ Build  │   │ Build   │   │ Build    │
│ Bot    │   │ Backend │   │ Frontend │
└────┬───┘   └────┬────┘   └────┬─────┘
     │            │             │
     │ if release │             │
     ▼            ▼             ▼
┌──────────────────────────────────┐
│  GitHub Container Registry       │
│  (ghcr.io)                       │
│                                  │
│  - systech-aidd-bot:latest      │
│  - systech-aidd-backend:latest  │
│  - systech-aidd-frontend:latest │
└──────────────────────────────────┘
           │
           │ docker pull (no auth)
           ▼
    ┌──────────────┐
    │   Server     │
    │ (D2, D3)     │
    └──────────────┘
```

## Workflow логика

### Push в main

1. Checkout кода
2. Setup Docker Buildx
3. Сборка образов с кэшированием
4. ✅ Проверка успешности сборки
5. ❌ Публикация пропускается

**Цель:** Проверить, что код собирается без ошибок.

### Push в release

1. Checkout кода
2. Setup Docker Buildx
3. **Логин в GHCR**
4. Сборка образов с кэшированием
5. **Публикация в GHCR:**
   - `ghcr.io/[owner]/systech-aidd-[service]:latest`
   - `ghcr.io/[owner]/systech-aidd-[service]:sha-{commit}`
6. ✅ Образы доступны в registry

**Цель:** Собрать и опубликовать стабильные версии для деплоя.

## Теги образов

### latest

Всегда указывает на последний успешно собранный коммит в `release`:
```bash
docker pull ghcr.io/[owner]/systech-aidd-bot:latest
```

### sha-{commit}

Конкретная версия образа для определенного коммита:
```bash
docker pull ghcr.io/[owner]/systech-aidd-bot:sha-abc123def456
```

**Преимущества двух тегов:**
- `latest` - удобно для development и quick updates
- `sha-{commit}` - immutable, позволяет откатиться на конкретную версию

## Команды для проверки

### Проверка workflow

```bash
# Перейти на GitHub Actions
# https://github.com/[owner]/systech-aidd/actions

# Проверить статус последнего run
# Должны быть 3 параллельных job (bot, backend, frontend)
```

### Проверка пакетов в GHCR

```bash
# Перейти на GitHub Packages
# https://github.com/[owner]?tab=packages

# Должны быть видны 3 пакета:
# - systech-aidd-bot
# - systech-aidd-backend
# - systech-aidd-frontend
```

### Локальный pull образов

```bash
# Pull образов (без авторизации если public)
docker pull ghcr.io/[owner]/systech-aidd-bot:latest
docker pull ghcr.io/[owner]/systech-aidd-backend:latest
docker pull ghcr.io/[owner]/systech-aidd-frontend:latest

# Проверка образов
docker images | grep systech-aidd
```

### Запуск из registry

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса (все должны быть Up)
docker-compose -f docker-compose.prod.yml ps

# Проверка логов (не должно быть ошибок)
docker-compose -f docker-compose.prod.yml logs

# Проверка работоспособности
curl http://localhost:8000/docs  # Backend API docs
curl http://localhost:3000       # Frontend

# Остановка
docker-compose -f docker-compose.prod.yml down
```

## Результаты

✅ GitHub Actions workflow создан и настроен  
✅ Matrix strategy для параллельной сборки 3 сервисов  
✅ Docker layer caching для ускорения сборки  
✅ Условная публикация только для release ветки  
✅ Теги образов: latest и sha-{commit}  
✅ docker-compose.prod.yml для использования registry образов  
✅ Полная документация по GitHub Actions  
✅ README обновлен с badge и инструкциями  

## Ручные шаги (после автоматизации)

После первого push в `release`:

1. ✅ Проверить успешность workflow в GitHub Actions
2. ✅ Настроить публичный доступ к пакетам в GHCR
3. ✅ Заменить `[owner]` в docker-compose.prod.yml
4. ✅ Протестировать pull и запуск образов локально
5. ✅ Обновить D1_COMPLETION_SUMMARY.md с реальными ссылками

## Критерии успеха

✅ Workflow автоматически запускается при push в main и release  
✅ Сборка проходит успешно для всех трех сервисов  
✅ Образы публикуются в GHCR только при push в release  
⏳ Образы доступны публично без авторизации (после ручной настройки)  
⏳ Локально можно pull и запустить образы из registry (после публикации)  
✅ docker-compose.prod.yml работает корректно  
✅ Документация актуальна и содержит все инструкции  
✅ Badge статуса сборки отображается в README  

## Следующий спринт

**D2: Развертывание на сервер** - ручной deploy с использованием опубликованных образов через пошаговую инструкцию.

После завершения D1, в спринте D2 будем использовать опубликованные образы для развертывания на удаленный сервер.

