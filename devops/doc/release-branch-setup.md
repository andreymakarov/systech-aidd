# Настройка ветки release

## Назначение

Ветка `release` используется для:
- Автоматической публикации Docker образов в GitHub Container Registry
- Развертывания стабильных версий на production серверы
- Отделения стабильного кода от активной разработки

## Создание ветки release

### Первоначальная настройка

```bash
# 1. Убедитесь что вы на актуальной ветке
git checkout main  # или devops, в зависимости от вашей основной ветки

# 2. Получите последние изменения
git pull origin main

# 3. Создайте ветку release
git checkout -b release

# 4. Запушьте ветку в удаленный репозиторий
git push -u origin release
```

### Что произойдет после push

GitHub Actions автоматически:
1. ✅ Запустит workflow "Build and Publish Docker Images"
2. ✅ Соберет три Docker образа (bot, backend, frontend) параллельно
3. ✅ Опубликует образы в GitHub Container Registry (GHCR)
4. ✅ Присвоит теги `latest` и `sha-{commit}`

## Workflow для веток

### main (или devops)

**Триггер:** Push в main  
**Действия:**
- ✅ Сборка всех трех образов
- ✅ Проверка успешности сборки
- ❌ Публикация в GHCR (пропускается)

**Назначение:** Проверить что код собирается без ошибок.

### release

**Триггер:** Push в release  
**Действия:**
- ✅ Сборка всех трех образов
- ✅ Проверка успешности сборки
- ✅ Публикация в GHCR с тегами `latest` и `sha-{commit}`

**Назначение:** Собрать и опубликовать стабильные версии для деплоя.

## Работа с веткой release

### Обновление release из main

Когда в `main` накопились изменения, готовые для публикации:

```bash
# 1. Переключиться на release
git checkout release

# 2. Получить последние изменения
git pull origin release

# 3. Смержить изменения из main
git merge main

# 4. Разрешить конфликты (если есть)
# ... редактировать конфликтующие файлы ...
git add .
git commit

# 5. Запушить обновленную ветку
git push origin release
```

GitHub Actions автоматически соберет и опубликует обновленные образы.

### Hotfix в release

Для критических исправлений без ожидания мерджа из main:

```bash
# 1. Создать ветку для hotfix от release
git checkout release
git pull origin release
git checkout -b hotfix/critical-bug-fix

# 2. Внести изменения
# ... редактировать файлы ...

# 3. Закоммитить
git add .
git commit -m "fix: critical bug in production"

# 4. Запушить и создать PR в release
git push origin hotfix/critical-bug-fix

# 5. После ревью - смержить в release
git checkout release
git merge hotfix/critical-bug-fix
git push origin release

# 6. Не забыть смержить hotfix обратно в main
git checkout main
git merge hotfix/critical-bug-fix
git push origin main
```

### Cherry-pick конкретного коммита

Если нужно добавить только один коммит из main:

```bash
# 1. Найти SHA коммита в main
git log main --oneline

# 2. Переключиться на release
git checkout release

# 3. Cherry-pick коммита
git cherry-pick <commit-sha>

# 4. Запушить
git push origin release
```

## Проверка успешности публикации

### GitHub Actions

1. Перейти на страницу Actions:
   ```
   https://github.com/[owner]/systech-aidd/actions
   ```

2. Проверить последний workflow run:
   - ✅ Статус: Success (зеленая галочка)
   - ✅ Все 3 job завершены успешно
   - ✅ Build summary показывает "Published: true"

### GitHub Container Registry

1. Перейти на страницу Packages:
   ```
   https://github.com/[owner]?tab=packages
   ```

2. Проверить наличие пакетов:
   - ✅ systech-aidd-bot
   - ✅ systech-aidd-backend
   - ✅ systech-aidd-frontend

3. Для каждого пакета:
   - Кликнуть на пакет
   - Проверить теги: `latest`, `sha-{commit}`
   - Проверить время обновления (должно совпадать с push)

### Локальная проверка

```bash
# Pull последних образов
docker pull ghcr.io/[owner]/systech-aidd-bot:latest
docker pull ghcr.io/[owner]/systech-aidd-backend:latest
docker pull ghcr.io/[owner]/systech-aidd-frontend:latest

# Проверить версию по SHA
docker inspect ghcr.io/[owner]/systech-aidd-bot:latest | grep -A 10 Labels
```

## Теги образов

### latest

- Всегда указывает на последний коммит в `release`
- Автоматически обновляется при каждом push
- Удобно для development и автоматических обновлений

```bash
docker pull ghcr.io/[owner]/systech-aidd-bot:latest
```

### sha-{commit}

- Immutable - никогда не изменяется
- Привязан к конкретному коммиту
- Используется для точного воспроизведения версии

```bash
# Формат: sha-{первые 7 символов SHA коммита}
docker pull ghcr.io/[owner]/systech-aidd-bot:sha-abc1234
```

**Преимущества:**
- `latest` - удобно для быстрых обновлений
- `sha-{commit}` - гарантирует воспроизводимость и возможность отката

## Best Practices

### 1. Защита ветки release

Рекомендуется настроить Branch Protection Rules:

1. Settings → Branches → Add rule
2. Branch name pattern: `release`
3. Включить:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass (GitHub Actions)
   - ✅ Require branches to be up to date

### 2. Стратегия мерджа

**Recommended:** Merge main → release периодически
- После завершения спринта
- После релиза новой версии
- После критических багфиксов

**Avoid:** Постоянная синхронизация с main
- release должна содержать только стабильный код
- Не мержить незавершенные фичи

### 3. Версионирование

Для семантического версионирования используйте git tags:

```bash
# После стабильного релиза
git checkout release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

В будущем можно добавить workflow для автоматического тегирования образов по git tags.

### 4. Rollback

При проблемах можно быстро откатиться:

**Вариант 1:** Использовать предыдущий тег
```bash
docker pull ghcr.io/[owner]/systech-aidd-bot:sha-{previous-commit}
```

**Вариант 2:** Откатить ветку
```bash
git checkout release
git reset --hard {previous-commit}
git push --force origin release
```

⚠️ **Внимание:** Force push в release следует использовать осторожно.

## Troubleshooting

### Workflow не запускается

**Проблема:** После push в release workflow не стартует.

**Решения:**
1. Проверить наличие файла `.github/workflows/build.yml`
2. Проверить синтаксис YAML (GitHub покажет ошибку)
3. Проверить права GitHub Actions в Settings → Actions → General

### Образы не публикуются

**Проблема:** Сборка проходит, но образов нет в GHCR.

**Решения:**
1. Проверить что push в ветку `release`, а не `main`
2. Проверить permissions в workflow (packages: write)
3. Проверить логи GitHub Actions на наличие ошибок при push

### Pull образов требует авторизацию

**Проблема:** `docker pull` требует логин.

**Решение:**
1. Перейти в GitHub Packages
2. Package settings → Change visibility → Public
3. Повторить для всех трех образов

## Полезные команды

```bash
# Проверить текущую ветку
git branch

# Посмотреть разницу между main и release
git diff main release

# Посмотреть историю коммитов в release
git log release --oneline

# Проверить какие коммиты есть в main, но нет в release
git log release..main --oneline

# Проверить статус GitHub Actions из CLI (требует gh CLI)
gh workflow list
gh run list --workflow=build.yml
gh run view {run-id}
```

## Заключение

Ветка `release` - ключевой элемент CI/CD pipeline:
- ✅ Автоматическая публикация стабильных версий
- ✅ Отделение production от development
- ✅ Готовность к автоматическому deployment (D3)

Для развертывания на сервер (D2, D3) будут использоваться образы из этой ветки.

