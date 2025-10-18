# Инструкция по ручному развертыванию на production сервер

## Оглавление

1. [Предварительная подготовка](#1-предварительная-подготовка-локально)
2. [SSH подключение к серверу](#2-ssh-подключение-к-серверу)
3. [Копирование файлов на сервер](#3-копирование-файлов-на-сервер)
4. [Загрузка образов](#4-загрузка-образов)
5. [Запуск сервисов](#5-запуск-сервисов)
6. [Проверка работоспособности](#6-проверка-работоспособности)
7. [Устранение неполадок](#7-устранение-неполадок)
8. [Управление сервисами](#8-управление-сервисами)

---

## Информация о сервере

**Параметры production сервера:**

- **Адрес:** 83.147.246.172
- **Пользователь:** systech
- **SSH ключ:** `devops/systech_admin_key.txt`
- **Рабочая директория:** `/opt/systech/andreymakarov`
- **Порты:**
  - Backend API: 8004
  - Frontend: 3004
  - Bot: без внешнего порта (работает внутри)

---

## 1. Предварительная подготовка (локально)

### 1.1. Проверка наличия SSH ключа

Убедитесь, что SSH ключ находится в директории проекта:

```bash
# Проверить наличие ключа
ls -la devops/systech_admin_key.txt
```

**Ожидаемый результат:**
```
-rw-r--r-- 1 user user 411 Oct 18 12:00 devops/systech_admin_key.txt
```

### 1.2. Настройка прав доступа к ключу

SSH требует строгих прав доступа к приватным ключам:

**Linux/macOS:**
```bash
chmod 600 devops/systech_admin_key.txt
```

**Windows (PowerShell):**
```powershell
# Удалить все разрешения кроме текущего пользователя
icacls devops\systech_admin_key.txt /inheritance:r
icacls devops\systech_admin_key.txt /grant:r "$($env:USERNAME):(R)"
```

**Windows (Git Bash):**
```bash
chmod 600 devops/systech_admin_key.txt
```

### 1.3. Создание файла .env с production настройками

Создайте файл `.env` на основе шаблона:

```bash
# Скопировать шаблон
cp env.production.template .env
```

Откройте файл `.env` в редакторе и заполните **обязательные** параметры:

```bash
# Обязательные параметры
TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token
OPENROUTER_API_KEY=your_actual_openrouter_api_key

# Остальные параметры можно оставить по умолчанию
```

**Важно:**
- Получите Telegram Bot Token: https://t.me/botfather
- Получите OpenRouter API Key: https://openrouter.ai/keys
- Убедитесь, что `NEXT_PUBLIC_STATS_API_URL=http://83.147.246.172:8004/api/v1`

### 1.4. Проверка доступности образов в GHCR

Убедитесь, что Docker образы доступны публично:

```bash
# Попробовать pull образы (без авторизации)
docker pull ghcr.io/andreymakarov/systech-aidd-bot:latest
docker pull ghcr.io/andreymakarov/systech-aidd-backend:latest
docker pull ghcr.io/andreymakarov/systech-aidd-frontend:latest
```

**Если pull не работает:**
- Проверьте, что образы опубликованы: https://github.com/andreymakarov?tab=packages
- Убедитесь, что visibility установлен в "Public" для всех трех пакетов

---

## 2. SSH подключение к серверу

### 2.1. Подключение к серверу

**Linux/macOS/Git Bash:**
```bash
ssh -i devops/systech_admin_key.txt systech@83.147.246.172
```

**Windows PowerShell:**
```powershell
ssh -i devops\systech_admin_key.txt systech@83.147.246.172
```

**При первом подключении** система спросит о добавлении fingerprint:
```
The authenticity of host '83.147.246.172' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
Введите `yes` и нажмите Enter.

**Ожидаемый результат:**
```
Welcome to Ubuntu 22.04 LTS
...
systech@server:~$
```

### 2.2. Проверка доступа к Docker

После подключения проверьте, что Docker установлен и доступен:

```bash
# Проверить версию Docker
docker --version

# Проверить статус Docker
docker ps

# Проверить Docker Compose
docker-compose --version
# или для новых версий
docker compose version
```

**Ожидаемые версии:**
- Docker: 20.10+
- Docker Compose: 1.29+ или 2.0+

### 2.3. Создание рабочей директории

Создайте личную рабочую директорию:

```bash
# Создать директорию
sudo mkdir -p /opt/systech/andreymakarov

# Установить владельца
sudo chown -R systech:systech /opt/systech/andreymakarov

# Перейти в рабочую директорию
cd /opt/systech/andreymakarov

# Проверить текущую директорию
pwd
```

**Ожидаемый результат:**
```
/opt/systech/andreymakarov
```

### 2.4. Создание директории для базы данных

```bash
# Создать директорию для данных backend
mkdir -p backend/data

# Проверить структуру
tree -L 2
# или просто
ls -la
```

**Важно:** Директория `backend/data` будет использоваться для SQLite базы данных.

---

## 3. Копирование файлов на сервер

### 3.1. Открыть новый терминал (локально)

**Не закрывайте SSH сессию!** Откройте новый терминал на вашем локальном компьютере.

Перейдите в директорию проекта:

```bash
cd /path/to/systech-aidd
```

### 3.2. Копирование docker-compose.prod.yml

**Linux/macOS/Git Bash:**
```bash
scp -i devops/systech_admin_key.txt docker-compose.prod.yml systech@83.147.246.172:/opt/systech/andreymakarov/
```

**Windows PowerShell:**
```powershell
scp -i devops\systech_admin_key.txt docker-compose.prod.yml systech@83.147.246.172:/opt/systech/andreymakarov/
```

**Ожидаемый результат:**
```
docker-compose.prod.yml    100%  1234    45.6KB/s   00:00
```

### 3.3. Копирование .env файла

**⚠️ ВАЖНО:** Файл `.env` содержит секреты. Убедитесь, что передаете его безопасно!

**Linux/macOS/Git Bash:**
```bash
scp -i devops/systech_admin_key.txt .env systech@83.147.246.172:/opt/systech/andreymakarov/
```

**Windows PowerShell:**
```powershell
scp -i devops\systech_admin_key.txt .env systech@83.147.246.172:/opt/systech/andreymakarov/
```

**Ожидаемый результат:**
```
.env    100%  1523    67.8KB/s   00:00
```

### 3.4. Проверка копирования (в SSH сессии)

Вернитесь в окно с SSH подключением и проверьте файлы:

```bash
# Перейти в рабочую директорию
cd /opt/systech/andreymakarov

# Проверить наличие файлов
ls -lah

# Проверить содержимое docker-compose (первые 20 строк)
head -20 docker-compose.prod.yml

# Проверить переменные окружения (без секретов)
grep -v "TOKEN\|KEY" .env | head -10
```

**Ожидаемый результат:**
```
total 12K
drwxr-xr-x 3 systech systech 4.0K Oct 18 12:00 .
drwxr-xr-x 3 root    root    4.0K Oct 18 11:50 ..
drwxr-xr-x 2 systech systech 4.0K Oct 18 11:55 backend
-rw-r--r-- 1 systech systech 1.5K Oct 18 12:00 .env
-rw-r--r-- 1 systech systech 1.2K Oct 18 12:00 docker-compose.prod.yml
```

---

## 4. Загрузка образов

### 4.1. Pull образов из GHCR

Загрузите Docker образы с GitHub Container Registry:

```bash
cd /opt/systech/andreymakarov

# Загрузить образы (публичные, авторизация не нужна)
docker pull ghcr.io/andreymakarov/systech-aidd-bot:latest
docker pull ghcr.io/andreymakarov/systech-aidd-backend:latest
docker pull ghcr.io/andreymakarov/systech-aidd-frontend:latest
```

**Процесс загрузки займет 2-5 минут:**
```
latest: Pulling from andreymakarov/systech-aidd-bot
abc123def456: Pull complete
...
Status: Downloaded newer image for ghcr.io/andreymakarov/systech-aidd-bot:latest
```

### 4.2. Альтернатива: загрузка через docker-compose

Вместо ручного pull можно использовать docker-compose:

```bash
docker-compose -f docker-compose.prod.yml pull
```

Эта команда загрузит все три образа за один раз.

### 4.3. Проверка загруженных образов

```bash
# Проверить список образов
docker images | grep systech-aidd

# Детальная информация
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep systech-aidd
```

**Ожидаемый результат:**
```
ghcr.io/andreymakarov/systech-aidd-bot        latest    abc123def456   2 minutes ago   345MB
ghcr.io/andreymakarov/systech-aidd-backend    latest    def456abc789   2 minutes ago   678MB
ghcr.io/andreymakarov/systech-aidd-frontend   latest    789abc123def   2 minutes ago   234MB
```

---

## 5. Запуск сервисов

### 5.1. Запуск через docker-compose

Запустите все сервисы в фоновом режиме:

```bash
cd /opt/systech/andreymakarov

# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d
```

**Процесс запуска:**
```
Creating network "andreymakarov_default" with the default driver
Creating andreymakarov_backend_1 ... done
Creating andreymakarov_bot_1     ... done
Creating andreymakarov_frontend_1 ... done
```

**Флаг `-d`** запускает контейнеры в detached режиме (в фоне).

### 5.2. Проверка статуса контейнеров

```bash
# Проверить статус всех контейнеров
docker-compose -f docker-compose.prod.yml ps
```

**Ожидаемый результат (все контейнеры в состоянии "Up"):**
```
           Name                         Command               State           Ports
--------------------------------------------------------------------------------------------
andreymakarov_backend_1    sh -c alembic -c backend/a ...   Up      0.0.0.0:8004->8000/tcp
andreymakarov_bot_1        python -m bot                     Up
andreymakarov_frontend_1   docker-entrypoint.sh node  ...   Up      0.0.0.0:3004->3000/tcp
```

**Важно:** Все контейнеры должны быть в состоянии `Up`. Если какой-то контейнер в состоянии `Exit` или `Restarting`, см. раздел [Устранение неполадок](#7-устранение-неполадок).

### 5.3. Просмотр логов запуска

```bash
# Посмотреть логи всех сервисов
docker-compose -f docker-compose.prod.yml logs

# Посмотреть логи в real-time режиме
docker-compose -f docker-compose.prod.yml logs -f

# Остановить просмотр логов: Ctrl+C
```

**Посмотреть логи отдельных сервисов:**
```bash
# Backend
docker-compose -f docker-compose.prod.yml logs backend

# Bot
docker-compose -f docker-compose.prod.yml logs bot

# Frontend
docker-compose -f docker-compose.prod.yml logs frontend
```

**Последние 50 строк с timestamps:**
```bash
docker-compose -f docker-compose.prod.yml logs --tail=50 -t
```

---

## 6. Проверка работоспособности

### 6.1. Проверка Backend API

#### 6.1.1. Проверка с сервера

```bash
# Проверить health endpoint
curl http://localhost:8004/

# Проверить API docs
curl -I http://localhost:8004/docs

# Проверить stats endpoint
curl http://localhost:8004/api/v1/stats?period=day
```

**Ожидаемый результат:**
```json
{"detail":"OK"}
```

#### 6.1.2. Проверка с локального компьютера

Откройте браузер на вашем локальном компьютере:

```
http://83.147.246.172:8004/docs
```

Должна открыться **Swagger UI документация** с списком endpoints.

### 6.2. Проверка Frontend

#### 6.2.1. Проверка с сервера

```bash
curl -I http://localhost:3004/
```

**Ожидаемый результат:**
```
HTTP/1.1 200 OK
Content-Type: text/html
...
```

#### 6.2.2. Проверка с локального компьютера

Откройте браузер:

```
http://83.147.246.172:3004
```

Должна открыться **страница дашборда** со статистикой.

### 6.3. Проверка логов бота

```bash
# Посмотреть последние 100 строк логов бота
docker-compose -f docker-compose.prod.yml logs --tail=100 bot
```

**Что искать в логах:**
```
Инициализация компонентов...
Загружена конфигурация
Role loaded successfully
Запуск бота...
Бот запущен
```

**Не должно быть:**
- Ошибок подключения к Backend
- Ошибок авторизации Telegram
- Ошибок OpenRouter API

### 6.4. Проверка работы бота в Telegram

1. Откройте Telegram
2. Найдите вашего бота (используйте username из BotFather)
3. Отправьте команду `/start`

**Ожидаемый ответ:**
```
Привет! Я AI-ассистент.
Отправьте мне сообщение, и я постараюсь помочь.

Доступные команды:
/start - показать это сообщение
/role - показать мою текущую роль
/clear - очистить историю диалога
```

4. Отправьте любое сообщение, например: "Привет!"

**Ожидаемый результат:** Бот должен ответить в течение 1-5 секунд.

### 6.5. Проверка базы данных

```bash
# Проверить наличие файла БД
ls -lh /opt/systech/andreymakarov/backend/data/bot.db

# Проверить размер БД
du -h /opt/systech/andreymakarov/backend/data/bot.db

# Подключиться к БД (если установлен sqlite3)
sqlite3 backend/data/bot.db "SELECT COUNT(*) FROM messages;"
```

**После отправки нескольких сообщений боту:**
```bash
# Должны появиться записи
sqlite3 backend/data/bot.db "SELECT user_id, role, LENGTH(content) as len FROM messages ORDER BY created_at DESC LIMIT 5;"
```

### 6.6. Проверка сетевого взаимодействия

```bash
# Проверить, что порты открыты
sudo netstat -tlnp | grep -E ':(8004|3004)'

# Альтернатива (если netstat не установлен)
sudo ss -tlnp | grep -E ':(8004|3004)'
```

**Ожидаемый результат:**
```
tcp6  0  0 :::8004   :::*   LISTEN   12345/docker-proxy
tcp6  0  0 :::3004   :::*   LISTEN   12346/docker-proxy
```

---

## 7. Устранение неполадок

### 7.1. Контейнер не запускается

**Проблема:** `docker-compose ps` показывает статус `Exit` или `Restarting`.

**Решение:**
```bash
# Посмотреть логи проблемного контейнера
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs bot
docker-compose -f docker-compose.prod.yml logs frontend

# Попробовать запустить контейнер вручную
docker-compose -f docker-compose.prod.yml up backend

# Проверить переменные окружения
docker-compose -f docker-compose.prod.yml config
```

### 7.2. Ошибка: "TELEGRAM_BOT_TOKEN не установлена"

**Проблема:** В логах бота:
```
ValueError: Обязательная переменная окружения TELEGRAM_BOT_TOKEN не установлена
```

**Решение:**
```bash
# Проверить содержимое .env (без показа секретов)
cat .env | grep TELEGRAM_BOT_TOKEN | cut -d'=' -f1

# Должно быть: TELEGRAM_BOT_TOKEN

# Если переменной нет, отредактировать .env
nano .env
# Добавить: TELEGRAM_BOT_TOKEN=your_actual_token

# Перезапустить бота
docker-compose -f docker-compose.prod.yml restart bot
```

### 7.3. Ошибка: "Failed to connect to backend"

**Проблема:** Бот не может подключиться к Backend.

**Решение:**
```bash
# Проверить, что backend запущен
docker-compose -f docker-compose.prod.yml ps backend

# Проверить логи backend
docker-compose -f docker-compose.prod.yml logs backend | tail -50

# Проверить сеть Docker
docker network ls
docker network inspect andreymakarov_default

# Перезапустить оба сервиса
docker-compose -f docker-compose.prod.yml restart backend bot
```

### 7.4. Порты уже заняты

**Проблема:**
```
Error: Bind for 0.0.0.0:8004 failed: port is already allocated
```

**Решение:**
```bash
# Найти процесс, использующий порт
sudo lsof -i :8004
# или
sudo netstat -tlnp | grep 8004

# Остановить процесс
sudo kill -9 <PID>

# Или использовать другие порты в docker-compose.prod.yml
nano docker-compose.prod.yml
# Изменить: "8005:8000" вместо "8004:8000"
```

### 7.5. База данных не создается

**Проблема:** Ошибка "unable to open database file".

**Решение:**
```bash
# Проверить права доступа
ls -la backend/data/

# Создать директорию если не существует
mkdir -p backend/data
chmod 755 backend/data

# Перезапустить backend
docker-compose -f docker-compose.prod.yml restart backend
```

### 7.6. Frontend не подключается к API

**Проблема:** Frontend загружается, но не показывает данные.

**Решение:**
```bash
# Проверить логи frontend
docker-compose -f docker-compose.prod.yml logs frontend | tail -50

# Проверить переменную NEXT_PUBLIC_STATS_API_URL в .env
cat .env | grep NEXT_PUBLIC_STATS_API_URL

# Должно быть: http://83.147.246.172:8004/api/v1

# Если неверно, исправить и пересоздать контейнер
nano .env
docker-compose -f docker-compose.prod.yml up -d --force-recreate frontend
```

### 7.7. Образы не загружаются

**Проблема:** `docker pull` возвращает ошибку "unauthorized" или "not found".

**Решение:**
```bash
# Проверить, что образы публичные
# Откройте в браузере:
# https://github.com/andreymakarov?tab=packages

# Для каждого пакета проверьте:
# Package settings -> Danger Zone -> Change visibility -> Public

# После изменения повторить pull
docker pull ghcr.io/andreymakarov/systech-aidd-bot:latest
```

### 7.8. Полный перезапуск

Если ничего не помогает:

```bash
# Остановить и удалить все контейнеры
docker-compose -f docker-compose.prod.yml down

# Удалить volumes (ВНИМАНИЕ: удалит БД!)
docker-compose -f docker-compose.prod.yml down -v

# Очистить неиспользуемые образы
docker system prune -f

# Загрузить образы заново
docker-compose -f docker-compose.prod.yml pull

# Запустить снова
docker-compose -f docker-compose.prod.yml up -d

# Проверить логи
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 8. Управление сервисами

### 8.1. Остановка сервисов

```bash
# Остановить все сервисы (контейнеры останутся)
docker-compose -f docker-compose.prod.yml stop

# Остановить конкретный сервис
docker-compose -f docker-compose.prod.yml stop bot

# Остановить и удалить контейнеры (БД сохранится)
docker-compose -f docker-compose.prod.yml down

# Остановить и удалить контейнеры + volumes (УДАЛИТ БД!)
docker-compose -f docker-compose.prod.yml down -v
```

### 8.2. Запуск сервисов

```bash
# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d

# Запустить конкретный сервис
docker-compose -f docker-compose.prod.yml up -d bot

# Запустить без detach (с выводом логов)
docker-compose -f docker-compose.prod.yml up
```

### 8.3. Перезапуск сервисов

```bash
# Перезапустить все сервисы
docker-compose -f docker-compose.prod.yml restart

# Перезапустить конкретный сервис
docker-compose -f docker-compose.prod.yml restart backend

# Пересоздать контейнеры (например, после изменения .env)
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### 8.4. Просмотр логов

```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs

# В real-time режиме
docker-compose -f docker-compose.prod.yml logs -f

# Последние N строк
docker-compose -f docker-compose.prod.yml logs --tail=100

# С временными метками
docker-compose -f docker-compose.prod.yml logs -t

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f bot

# Сохранить логи в файл
docker-compose -f docker-compose.prod.yml logs > deployment.log
```

### 8.5. Обновление образов

Когда выйдет новая версия:

```bash
cd /opt/systech/andreymakarov

# Загрузить новые версии образов
docker-compose -f docker-compose.prod.yml pull

# Пересоздать и запустить контейнеры
docker-compose -f docker-compose.prod.yml up -d

# Проверить, что используются новые образы
docker-compose -f docker-compose.prod.yml images
```

### 8.6. Просмотр статистики

```bash
# Использование ресурсов всеми контейнерами
docker stats

# Детальная информация о контейнере
docker inspect andreymakarov_backend_1

# Выполнить команду внутри контейнера
docker-compose -f docker-compose.prod.yml exec backend bash
docker-compose -f docker-compose.prod.yml exec backend ls -la backend/data
```

### 8.7. Резервное копирование базы данных

```bash
# Создать backup директории
cp -r backend/data backend/data.backup.$(date +%Y%m%d_%H%M%S)

# Или tar архив
tar -czf backend-data-backup-$(date +%Y%m%d).tar.gz backend/data

# Список backup'ов
ls -lh backend-data-backup-*.tar.gz
```

### 8.8. Восстановление из backup

```bash
# Остановить сервисы
docker-compose -f docker-compose.prod.yml stop

# Восстановить из tar архива
tar -xzf backend-data-backup-20251018.tar.gz

# Запустить сервисы
docker-compose -f docker-compose.prod.yml start
```

---

## Полезные команды

### Мониторинг

```bash
# Проверить статус всех контейнеров
docker ps

# Использование ресурсов
docker stats --no-stream

# Проверить место на диске
df -h
docker system df

# Логи systemd (если Docker запущен через systemd)
sudo journalctl -u docker -f
```

### Очистка

```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

### Проверка безопасности

```bash
# Проверить открытые порты
sudo netstat -tlnp

# Проверить правила firewall
sudo ufw status

# Логи авторизации
sudo tail -f /var/log/auth.log
```

---

## Следующие шаги

После успешного развертывания:

1. **Настроить мониторинг** (опционально)
   - Установить Grafana + Prometheus
   - Настроить alerts на email/Telegram

2. **Настроить резервное копирование** (рекомендуется)
   - Создать cron job для автоматического backup БД
   - Настроить отправку backup'ов на внешнее хранилище

3. **Настроить домен и SSL** (для production)
   - Настроить nginx reverse proxy
   - Получить SSL сертификат (Let's Encrypt)
   - Настроить автоматическое обновление сертификата

4. **Автоматизация деплоя** (Спринт D3)
   - Настроить GitHub Actions для автоматического деплоя
   - Webhook для обновления при push в ветку release

---

## Дополнительные ресурсы

- [Docker Compose документация](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [DevOps Roadmap проекта](../../devops/doc/devops-roadmap.md)
- [Architecture Overview](./architecture-overview.md)

---

**Успешного развертывания! 🚀**

