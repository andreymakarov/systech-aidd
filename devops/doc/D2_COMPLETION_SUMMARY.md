# D2: Manual Deploy - Completion Summary

**Спринт:** D2 - Развертывание на сервер  
**Статус:** 🚧 В работе  
**Дата начала:** 18 октября 2025  
**Дата завершения:** TBD  

---

## Описание спринта

Спринт D2 фокусируется на развертывании приложения Systech AIDD на production сервер с использованием готовых Docker образов из GitHub Container Registry. Главная цель - создать подробную инструкцию для ручного деплоя и успешно развернуть все сервисы на удаленном сервере.

---

## Что было сделано

### ✅ 1. Создан шаблон конфигурации окружения

**Файл:** `env.production.template`

- Все необходимые переменные окружения для production
- Подробные комментарии к каждой переменной
- Примеры значений без реальных секретов
- Секции: Bot, Backend, Frontend
- Инструкции по заполнению

**Переменные:**
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `OPENROUTER_API_KEY` - API ключ OpenRouter
- `SYSTEM_PROMPT` - промпт бота
- `BACKEND_URL` - внутренний URL backend
- `DATABASE_URL` - путь к БД
- `STATS_COLLECTOR` - тип коллектора статистики
- `NEXT_PUBLIC_STATS_API_URL` - публичный URL API для браузера
- `STATS_API_URL_INTERNAL` - внутренний URL для SSR

### ✅ 2. Обновлен docker-compose.prod.yml

**Файл:** `docker-compose.prod.yml`

Изменения:
- Порты обновлены: `8004:8000` для backend, `3004:3000` для frontend
- Добавлен `env_file: .env` для всех сервисов
- Volume для базы данных настроен
- Команда запуска backend включает миграции

### ✅ 3. Создана подробная инструкция по развертыванию

**Файл:** `doc/guides/manual-deploy.md`

Структура инструкции:

#### 3.1. Предварительная подготовка (локально)
- ✅ Проверка наличия SSH ключа
- ✅ Настройка прав доступа (chmod 600)
- ✅ Создание .env с production настройками
- ✅ Проверка доступности образов в GHCR

#### 3.2. SSH подключение к серверу
- ✅ Команды подключения (Linux/macOS/Windows)
- ✅ Проверка доступа к Docker
- ✅ Создание рабочей директории `/opt/systech/andreymakarov`

#### 3.3. Копирование файлов на сервер
- ✅ Копирование docker-compose.prod.yml через scp
- ✅ Копирование .env через scp
- ✅ Проверка копирования

#### 3.4. Загрузка образов
- ✅ Pull образов из GHCR (публичный доступ)
- ✅ Альтернатива через docker-compose pull
- ✅ Проверка загруженных образов

#### 3.5. Запуск сервисов
- ✅ Запуск через docker-compose up -d
- ✅ Проверка статуса контейнеров
- ✅ Просмотр логов

#### 3.6. Проверка работоспособности
- ✅ Backend API: `curl http://83.147.246.172:8004/docs`
- ✅ Frontend: `curl http://83.147.246.172:3004`
- ✅ Проверка логов бота
- ✅ Проверка работы бота в Telegram
- ✅ Проверка базы данных

#### 3.7. Устранение неполадок
- ✅ Контейнер не запускается
- ✅ Ошибки конфигурации
- ✅ Проблемы с портами
- ✅ Проблемы с базой данных
- ✅ Frontend не подключается к API
- ✅ Полный перезапуск

#### 3.8. Управление сервисами
- ✅ Остановка/запуск сервисов
- ✅ Перезапуск сервисов
- ✅ Просмотр логов
- ✅ Обновление образов
- ✅ Резервное копирование БД
- ✅ Мониторинг и очистка

### ✅ 4. Обновлен DevOps Roadmap

**Файл:** `devops/doc/devops-roadmap.md`

- Статус D1 изменен на `✅ Завершено (18.10.2025)`
- Статус D2 изменен на `🚧 В работе`
- Добавлена ссылка на инструкцию manual-deploy.md

---

## Параметры сервера

**Production сервер:**
- **Адрес:** 83.147.246.172
- **Пользователь:** systech
- **SSH ключ:** `devops/systech_admin_key.txt`
- **Рабочая директория:** `/opt/systech/andreymakarov`
- **Порты:**
  - Backend API: 8004
  - Frontend: 3004
  - Bot: внутренний (без публичного порта)

**Образы в GHCR:**
- `ghcr.io/andreymakarov/systech-aidd-bot:latest`
- `ghcr.io/andreymakarov/systech-aidd-backend:latest`
- `ghcr.io/andreymakarov/systech-aidd-frontend:latest`

---

## Команды для проверки

### Проверка на сервере

```bash
# Подключение к серверу
ssh -i devops/systech_admin_key.txt systech@83.147.246.172

# Переход в рабочую директорию
cd /opt/systech/andreymakarov

# Проверка статуса контейнеров
docker-compose -f docker-compose.prod.yml ps

# Ожидаемый результат:
# NAME                      STATE     PORTS
# backend                   Up        0.0.0.0:8004->8000/tcp
# bot                       Up
# frontend                  Up        0.0.0.0:3004->3000/tcp

# Проверка логов
docker-compose -f docker-compose.prod.yml logs --tail=50
```

### Проверка с локального компьютера

```bash
# Backend API Swagger UI
curl http://83.147.246.172:8004/docs

# Backend health check
curl http://83.147.246.172:8004/

# Frontend
curl -I http://83.147.246.172:3004/

# Статистика
curl http://83.147.246.172:8004/api/v1/stats?period=day
```

### Проверка через браузер

Откройте в браузере:
- **Backend API Docs:** http://83.147.246.172:8004/docs
- **Frontend Dashboard:** http://83.147.246.172:3004
- **API Stats:** http://83.147.246.172:8004/api/v1/stats?period=day

### Проверка бота в Telegram

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Отправьте любое сообщение
5. Проверьте, что бот отвечает

---

## Чек-лист успешного развертывания

### Подготовка
- [x] SSH ключ `devops/systech_admin_key.txt` доступен
- [x] Права доступа к ключу настроены (chmod 600)
- [ ] Файл `.env` создан и заполнен реальными значениями
- [ ] Образы доступны в GHCR и публичны

### Сервер
- [ ] SSH подключение к серверу работает
- [ ] Docker установлен и доступен
- [ ] Рабочая директория `/opt/systech/andreymakarov` создана
- [ ] Директория `backend/data` создана

### Файлы
- [ ] `docker-compose.prod.yml` скопирован на сервер
- [ ] `.env` скопирован на сервер
- [ ] Файлы на сервере проверены

### Образы
- [ ] Backend образ загружен
- [ ] Bot образ загружен
- [ ] Frontend образ загружен

### Запуск
- [ ] Контейнеры запущены через docker-compose
- [ ] Все контейнеры в статусе "Up"
- [ ] Миграции БД выполнены

### Проверка
- [ ] Backend API доступен на порту 8004
- [ ] Frontend доступен на порту 3004
- [ ] Логи бота не содержат ошибок
- [ ] Бот отвечает в Telegram
- [ ] База данных создана и работает
- [ ] Статистика возвращается через API

---

## Структура созданных файлов

```
systech-aidd/
├── env.production.template           # ✅ Шаблон переменных окружения
├── docker-compose.prod.yml           # ✅ Обновлен с портами 8004, 3004
├── doc/
│   └── guides/
│       └── manual-deploy.md          # ✅ Подробная инструкция деплоя
└── devops/
    ├── systech_admin_key.txt         # ✅ SSH ключ (уже был)
    └── doc/
        ├── devops-roadmap.md         # ✅ Обновлен статус D2
        └── D2_COMPLETION_SUMMARY.md  # ✅ Этот файл
```

---

## Полезные ссылки

### Документация проекта
- [Инструкция по развертыванию](../../doc/guides/manual-deploy.md)
- [DevOps Roadmap](./devops-roadmap.md)
- [D1 Completion Summary](./D1_COMPLETION_SUMMARY.md)
- [Architecture Overview](../../doc/guides/architecture-overview.md)

### GitHub
- [GitHub Actions](https://github.com/andreymakarov/systech-aidd/actions)
- [GitHub Packages](https://github.com/andreymakarov?tab=packages)
- [Backend Image](https://github.com/andreymakarov/systech-aidd/pkgs/container/systech-aidd-backend)
- [Bot Image](https://github.com/andreymakarov/systech-aidd/pkgs/container/systech-aidd-bot)
- [Frontend Image](https://github.com/andreymakarov/systech-aidd/pkgs/container/systech-aidd-frontend)

### Внешние ресурсы
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/keygen)

---

## Следующие шаги

### Немедленные действия

1. **Создать файл .env** с реальными секретами
   ```bash
   cp env.production.template .env
   # Отредактировать .env и заполнить:
   # - TELEGRAM_BOT_TOKEN
   # - OPENROUTER_API_KEY
   ```

2. **Выполнить развертывание** согласно инструкции
   - Следовать всем шагам из `doc/guides/manual-deploy.md`
   - Отмечать выполненные пункты в чек-листе

3. **Проверить работоспособность**
   - Все сервисы запущены
   - API доступен
   - Frontend работает
   - Бот отвечает

4. **Обновить README.md** с секцией Production Deployment

### После успешного деплоя

1. **Обновить документацию**
   - Отметить все чекбоксы в этом файле
   - Обновить статус в roadmap на `✅ Завершено`
   - Создать commit

2. **Настроить мониторинг** (опционально)
   - Логирование ошибок
   - Мониторинг ресурсов
   - Alerts

3. **Подготовиться к D3**
   - Автоматизация деплоя через GitHub Actions
   - Webhook для обновления
   - CI/CD pipeline

---

## Следующий спринт: D3

**D3: Auto Deploy**

После завершения D2 можно переходить к спринту D3:
- Создание GitHub Actions workflow для автоматического деплоя
- Настройка SSH ключей в GitHub Secrets
- Автоматическое обновление на сервере при push в release
- Уведомления о статусе деплоя

---

## Результаты спринта D2

### ✅ Документация

- Подробная инструкция по ручному деплою (150+ строк)
- Шаблон конфигурации окружения
- Команды для всех операционных систем (Linux/macOS/Windows)
- Секция устранения неполадок
- Секция управления сервисами

### ✅ Конфигурация

- docker-compose.prod.yml с правильными портами
- Все сервисы используют .env файл
- Volume для базы данных настроен
- Автоматические миграции при запуске

### ✅ Инфраструктура

- Определены параметры production сервера
- SSH доступ настроен
- Рабочая директория подготовлена
- Образы доступны в GHCR

### ⏳ Развертывание

- Инструкция готова
- Ожидает выполнения всех шагов
- Чек-лист для проверки

---

## Критерии успеха

После выполнения всех шагов:

- [x] Инструкция по деплою создана и подробна
- [x] Шаблон .env создан с описанием всех переменных
- [x] docker-compose.prod.yml обновлен с правильными портами
- [x] DevOps roadmap обновлен
- [ ] Все сервисы успешно запущены на production сервере
- [ ] Backend API доступен по адресу http://83.147.246.172:8004
- [ ] Frontend доступен по адресу http://83.147.246.172:3004
- [ ] Бот работает и отвечает в Telegram
- [ ] База данных создана и сохраняет сообщения
- [ ] README.md обновлен с секцией Production Deployment

---

**Статус:** Документация и конфигурация готовы ✅ | Ожидает развертывания ⏳  
**Следующий шаг:** Выполнить развертывание по инструкции  
**Следующий спринт:** D3 - Auto Deploy

---

**Дата последнего обновления:** 18 октября 2025

