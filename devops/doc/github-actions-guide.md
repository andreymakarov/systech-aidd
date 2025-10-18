# Руководство по GitHub Actions для Systech AIDD

## Введение

GitHub Actions - это встроенная в GitHub платформа CI/CD (Continuous Integration/Continuous Deployment), которая позволяет автоматизировать процессы сборки, тестирования и развертывания приложений.

## Основные понятия

### Workflow (Рабочий процесс)

Workflow - это автоматизированный процесс, состоящий из одной или нескольких задач (jobs). Workflows определяются в YAML файлах в директории `.github/workflows/`.

**Структура workflow:**
```yaml
name: Имя workflow
on: [события, которые запускают workflow]
jobs:
  job-id:
    runs-on: ubuntu-latest
    steps:
      - name: Шаг 1
        run: команда
```

### Jobs (Задачи)

Job - это набор шагов (steps), которые выполняются на одном runner (виртуальной машине). Jobs могут выполняться параллельно или последовательно.

### Steps (Шаги)

Step - это отдельная задача в job. Может быть командой shell или action (готовым модулем).

### Actions

Action - это переиспользуемый модуль, который выполняет определенную задачу. Примеры: checkout кода, настройка Docker, публикация в registry.

## Trigger события

Workflow может запускаться различными событиями:

### Push

Запуск при push в определенные ветки:
```yaml
on:
  push:
    branches: [main, release]
```

Запуск только при изменениях в определенных файлах:
```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile'
```

### Pull Request

Запуск при создании или обновлении PR:
```yaml
on:
  pull_request:
    branches: [main]
```

Полезно для проверки кода перед мерджем.

### Workflow Dispatch

Ручной запуск workflow:
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
```

### Комбинация событий

Можно комбинировать несколько триггеров:
```yaml
on:
  push:
    branches: [main, release]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

## Работа с Pull Requests

### Проверка кода в PR

Типичный workflow для проверки PR:
```yaml
name: PR Checks
on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linters
        run: make lint
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make test
```

### Статус проверок

GitHub автоматически показывает статус workflow в PR. Можно настроить required checks в настройках репозитория, чтобы запретить мердж без прохождения проверок.

### Комментарии в PR

Actions могут автоматически оставлять комментарии в PR с результатами (например, coverage report, benchmark results).

## Matrix Strategy

Matrix strategy позволяет запускать один job с разными параметрами параллельно.

### Базовый пример

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, backend, frontend]
    steps:
      - name: Build ${{ matrix.service }}
        run: docker build -f devops/Dockerfile.${{ matrix.service }} .
```

Это создаст 3 параллельных job: для bot, backend и frontend.

### Многомерная матрица

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node-version: [18, 20]
```

Это создаст 4 job (2 OS × 2 версии Node.js).

### Исключения

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node-version: [18, 20]
    exclude:
      - os: windows-latest
        node-version: 18
```

### Включение дополнительных комбинаций

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    node-version: [18, 20]
    include:
      - os: macos-latest
        node-version: 20
```

## Docker Layer Caching

Кэширование Docker layers значительно ускоряет сборку образов.

### GitHub Actions Cache

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: false
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Режимы кэширования:**
- `mode=min` - кэширует только финальные слои (меньше размер, медленнее)
- `mode=max` - кэширует все промежуточные слои (больше размер, быстрее)

### Registry Cache

Использование registry для кэша:
```yaml
cache-from: type=registry,ref=ghcr.io/user/app:buildcache
cache-to: type=registry,ref=ghcr.io/user/app:buildcache,mode=max
```

## Публикация Docker образов

### Аутентификация в GHCR

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

`GITHUB_TOKEN` - автоматически доступен в workflow, не требует настройки secrets.

### Сборка и публикация

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./Dockerfile
    push: true
    tags: |
      ghcr.io/${{ github.repository_owner }}/app:latest
      ghcr.io/${{ github.repository_owner }}/app:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Metadata для тегов и labels

```yaml
- name: Docker metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository_owner }}/app
    tags: |
      type=ref,event=branch
      type=sha,prefix={{branch}}-
      type=raw,value=latest,enable={{is_default_branch}}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

## Публичные vs Приватные образы

### Приватные образы (по умолчанию)

Образы, опубликованные в GHCR, по умолчанию приватные и доступны только владельцу и collaborators.

**Для pull приватных образов:**
```bash
# Нужна аутентификация
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker pull ghcr.io/user/app:latest
```

### Публичные образы

Для публичного доступа нужно изменить visibility пакета:

1. Перейти на GitHub → Ваш профиль/организация → Packages
2. Выбрать пакет (образ)
3. Package settings → Danger Zone
4. Change visibility → Public
5. Подтвердить действие

**После этого pull работает без авторизации:**
```bash
docker pull ghcr.io/user/app:latest
```

### Автоматическая публикация публичных образов

Нельзя автоматически сделать образ публичным при первой публикации. Это нужно сделать вручную после первого push.

Альтернатива: использовать Docker Hub, который поддерживает публичные образы по умолчанию.

## Настройка Permissions для GHCR

### Permissions в workflow

Для публикации в GHCR нужны права на запись:

```yaml
permissions:
  contents: read
  packages: write
```

- `contents: read` - для checkout кода
- `packages: write` - для публикации в GitHub Packages (GHCR)

### Условная публикация

Публиковать только для определенных веток:

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: ${{ github.ref == 'refs/heads/release' }}
    tags: ghcr.io/${{ github.repository_owner }}/app:latest
```

Или через условие на step:

```yaml
- name: Push to registry
  if: github.ref == 'refs/heads/release'
  run: docker push ghcr.io/user/app:latest
```

## Переменные и Secrets

### Встроенные переменные

GitHub Actions предоставляет множество переменных:

- `${{ github.repository }}` - имя репозитория (owner/repo)
- `${{ github.repository_owner }}` - владелец репозитория
- `${{ github.ref }}` - полная ссылка на ветку (refs/heads/main)
- `${{ github.sha }}` - commit SHA
- `${{ github.actor }}` - пользователь, запустивший workflow
- `${{ github.event_name }}` - событие, запустившее workflow

### Secrets

Чувствительные данные хранятся в GitHub Secrets:

**Настройка:**
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Имя и значение секрета

**Использование:**
```yaml
- name: Deploy
  env:
    SSH_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
    API_TOKEN: ${{ secrets.API_TOKEN }}
  run: ./deploy.sh
```

### Environment Variables

```yaml
env:
  NODE_ENV: production
  
jobs:
  build:
    env:
      BUILD_TYPE: release
    steps:
      - name: Build
        env:
          SPECIFIC_VAR: value
        run: make build
```

## Примеры workflow

### Минимальный CI workflow

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make test
```

### Docker build с matrix

```yaml
name: Build Docker Images
on:
  push:
    branches: [main, release]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, backend, frontend]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: .
          file: devops/Dockerfile.${{ matrix.service }}
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Полный CD workflow с публикацией

```yaml
name: Build and Publish
on:
  push:
    branches: [main, release]

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, backend, frontend]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to GHCR
        if: github.ref == 'refs/heads/release'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: devops/Dockerfile.${{ matrix.service }}
          push: ${{ github.ref == 'refs/heads/release' }}
          tags: |
            ghcr.io/${{ github.repository_owner }}/systech-aidd-${{ matrix.service }}:latest
            ghcr.io/${{ github.repository_owner }}/systech-aidd-${{ matrix.service }}:sha-${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Best Practices

### 1. Используйте конкретные версии actions

❌ Плохо:
```yaml
- uses: actions/checkout@main
```

✅ Хорошо:
```yaml
- uses: actions/checkout@v4
```

### 2. Кэшируйте зависимости

Для Python:
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

Для Node.js:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'pnpm'
```

### 3. Параллелизуйте независимые задачи

Используйте matrix для параллельной сборки:
```yaml
strategy:
  matrix:
    service: [service1, service2, service3]
```

### 4. Используйте concurrency для отмены устаревших runs

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 5. Добавляйте timeout

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

### 6. Минимизируйте использование secrets

Используйте встроенный `GITHUB_TOKEN` где возможно вместо создания Personal Access Token.

### 7. Защищайте production деплои

```yaml
environment:
  name: production
  url: https://prod.example.com
```

Требует ручного подтверждения через GitHub Environment protection rules.

## Отладка

### Включение debug логов

В настройках репозитория добавить secrets:
- `ACTIONS_RUNNER_DEBUG: true` - подробные логи runner
- `ACTIONS_STEP_DEBUG: true` - подробные логи шагов

### Использование tmate для SSH доступа

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
```

Позволяет подключиться по SSH к runner при ошибке.

### Локальное тестирование

Используйте [act](https://github.com/nektos/act) для локального запуска workflows:

```bash
# Установка
brew install act  # macOS
# или
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Запуск workflow
act push
```

## Ограничения и квоты

### GitHub Free tier

- 2000 минут в месяц для приватных репозиториев
- Неограниченно для публичных репозиториев
- Linux runners: 1x
- Одновременно: 20 jobs

### GitHub Pro

- 3000 минут в месяц
- Остальное аналогично Free

### Размер

- Максимальный размер artifacts: 10 GB
- Максимальное время выполнения job: 6 часов
- Максимальное время выполнения workflow: 72 часа

## Полезные ссылки

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Marketplace](https://github.com/marketplace?type=actions) - готовые actions
- [Events that trigger workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## Заключение

GitHub Actions - мощный инструмент для автоматизации CI/CD процессов. Основные преимущества:

- ✅ Встроен в GitHub, не требует внешних сервисов
- ✅ Богатая экосистема готовых actions
- ✅ Бесплатен для публичных репозиториев
- ✅ Гибкая конфигурация через YAML
- ✅ Интеграция с GitHub Packages (GHCR)

Для проекта Systech AIDD мы используем GitHub Actions для автоматической сборки и публикации Docker образов в GitHub Container Registry.

