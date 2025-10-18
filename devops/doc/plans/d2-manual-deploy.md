# План реализации D2: Развертывание на сервер

**Спринт:** D2 - Manual Deploy  
**Дата создания:** 18 октября 2025  
**Статус:** 🚧 В работе

---

## Цель спринта

Развернуть приложение Systech AIDD на production сервер с использованием готовых Docker образов из GitHub Container Registry. Создать подробную инструкцию для ручного деплоя и выполнить развертывание.

---

## Контекст

### Предыдущие спринты

- **D0 (Basic Docker Setup):** ✅ Завершен - все сервисы запускаются локально через docker-compose
- **D1 (Build & Publish):** ✅ Завершен - образы автоматически публикуются в GHCR

### Доступные ресурсы

**Production сервер:**
- Адрес: 83.147.246.172
- Пользователь: systech
- SSH ключ: `devops/systech_admin_key.txt`
- Рабочая директория: `/opt/systech/andreymakarov`
- Порты: 8004 (backend), 3004 (frontend)
- Docker и Docker Compose установлены

**Образы в GHCR:**
- `ghcr.io/andreymakarov/systech-aidd-bot:latest`
- `ghcr.io/andreymakarov/systech-aidd-backend:latest`
- `ghcr.io/andreymakarov/systech-aidd-frontend:latest`

---

## Задачи

### ✅ Задача 1: Создать шаблон .env.production

**Статус:** Завершено

**Файл:** `env.production.template`

**Содержание:**
- Все обязательные переменные окружения
- Подробные комментарии к каждой переменной
- Примеры значений без реальных секретов
- Секции: Bot, Backend, Frontend
- Инструкции по заполнению

**Результат:** Шаблон создан с 11 основными переменными и подробными комментариями.

---

### ✅ Задача 2: Обновить docker-compose.prod.yml

**Статус:** Завершено

**Файл:** `docker-compose.prod.yml`

**Изменения:**
- Порты обновлены: `8004:8000` для backend, `3004:3000` для frontend
- Добавлен `env_file: .env` для всех сервисов (backend, bot, frontend)
- Volume для базы данных настроен
- Переменная `NEXT_PUBLIC_STATS_API_URL` использует значение из .env с fallback

**Результат:** Конфигурация готова для production развертывания.

---

### ✅ Задача 3: Создать инструкцию manual-deploy.md

**Статус:** Завершено

**Файл:** `doc/guides/manual-deploy.md`

**Структура (8 разделов, 500+ строк):**

1. **Предварительная подготовка** - проверка SSH ключа, создание .env, проверка образов
2. **SSH подключение** - команды для Linux/macOS/Windows, проверка Docker
3. **Копирование файлов** - scp команды для docker-compose.prod.yml и .env
4. **Загрузка образов** - pull из GHCR, проверка загруженных образов
5. **Запуск сервисов** - docker-compose up, проверка статуса
6. **Проверка работоспособности** - тесты API, Frontend, Bot, БД
7. **Устранение неполадок** - 8 типичных проблем и решения
8. **Управление сервисами** - остановка, запуск, логи, backup

**Особенности:**
- Команды для всех ОС (Linux, macOS, Windows PowerShell)
- Пошаговые инструкции с ожидаемыми результатами
- Готовые команды для копирования
- Раздел troubleshooting
- Команды для мониторинга и управления

**Результат:** Подробная инструкция готова для использования.

---

### ✅ Задача 4: Обновить devops-roadmap.md

**Статус:** Завершено

**Файл:** `devops/doc/devops-roadmap.md`

**Изменения:**
- Статус D1: `✅ Завершено (18.10.2025)`
- Статус D2: `🚧 В работе`
- Ссылка на инструкцию: `[Инструкция](../../doc/guides/manual-deploy.md)`

**Результат:** Roadmap актуализирован.

---

### ✅ Задача 5: Создать D2_COMPLETION_SUMMARY.md

**Статус:** Завершено

**Файл:** `devops/doc/D2_COMPLETION_SUMMARY.md`

**Содержание:**
- Описание выполненных работ
- Параметры сервера
- Команды для проверки
- Чек-лист успешного развертывания (24 пункта)
- Структура созданных файлов
- Полезные ссылки
- Следующие шаги

**Результат:** Summary документ создан.

---

### ⏳ Задача 6: Выполнить развертывание

**Статус:** Готово к выполнению

**План действий:**

1. **Подготовка (локально):**
   - Создать .env из шаблона
   - Заполнить TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY
   - Настроить права SSH ключа

2. **Подключение к серверу:**
   - SSH подключение с использованием ключа
   - Проверка Docker и Docker Compose
   - Создание рабочей директории

3. **Копирование файлов:**
   - docker-compose.prod.yml
   - .env

4. **Запуск:**
   - docker-compose pull
   - docker-compose up -d
   - Проверка статуса

5. **Проверка:**
   - Backend API: http://83.147.246.172:8004/docs
   - Frontend: http://83.147.246.172:3004
   - Telegram бот

**Инструкция:** Следовать всем шагам из `doc/guides/manual-deploy.md`

**Результат:** Ожидает выполнения пользователем.

---

### ✅ Задача 7: Обновить README.md

**Статус:** Завершено

**Файл:** `README.md`

**Добавленная секция:** "Production Deployment"

**Содержание:**
- Требования к серверу
- Быстрый старт (3 шага)
- Ссылка на подробную инструкцию
- Список того, что описано в инструкции

**Местоположение:** После секции "CI/CD Pipeline", перед "Использование"

**Результат:** README обновлен.

---

### ⏳ Задача 8: Финализация

**Статус:** Ожидает завершения развертывания

**Действия после успешного деплоя:**

1. Обновить чек-лист в D2_COMPLETION_SUMMARY.md
2. Обновить статус D2 в roadmap: `✅ Завершено`
3. Создать commit: `docs: complete D2 sprint - Manual Deploy`
4. Обновить summary с финальным статусом

**Результат:** Ожидает выполнения.

---

## Структура созданных файлов

```
systech-aidd/
├── env.production.template              # ✅ Шаблон переменных окружения
├── docker-compose.prod.yml              # ✅ Обновлен (порты 8004, 3004)
├── README.md                            # ✅ Добавлена секция Production Deployment
├── doc/
│   └── guides/
│       └── manual-deploy.md             # ✅ Подробная инструкция (500+ строк)
└── devops/
    ├── systech_admin_key.txt            # ✅ SSH ключ (уже был)
    └── doc/
        ├── devops-roadmap.md            # ✅ Обновлен статус D2
        ├── D2_COMPLETION_SUMMARY.md     # ✅ Summary файл
        └── plans/
            └── d2-manual-deploy.md      # ✅ Этот файл
```

---

## Принципы реализации

### MVP подход

- Минимальная конфигурация для работы
- Без избыточной автоматизации (будет в D3)
- Фокус на понятных инструкциях
- Готовность к ручному выполнению

### Документирование

- Подробные пошаговые инструкции
- Примеры для разных ОС
- Ожидаемые результаты для каждого шага
- Раздел устранения неполадок

### Безопасность

- SSH ключи вместо паролей
- .env файл с секретами не коммитится
- Шаблон без реальных секретов
- Инструкции по настройке прав доступа

---

## Команды для проверки

### Локально

```bash
# Проверить наличие файлов
ls -la env.production.template
ls -la docker-compose.prod.yml
ls -la doc/guides/manual-deploy.md
ls -la devops/systech_admin_key.txt

# Проверить доступность образов
docker pull ghcr.io/andreymakarov/systech-aidd-bot:latest
docker pull ghcr.io/andreymakarov/systech-aidd-backend:latest
docker pull ghcr.io/andreymakarov/systech-aidd-frontend:latest
```

### На сервере (после деплоя)

```bash
# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Проверить логи
docker-compose -f docker-compose.prod.yml logs --tail=50

# Проверить API
curl http://localhost:8004/docs
curl http://localhost:3004/
```

### Из браузера (после деплоя)

- Backend API: http://83.147.246.172:8004/docs
- Frontend: http://83.147.246.172:3004
- Stats API: http://83.147.246.172:8004/api/v1/stats?period=day

---

## Критерии успеха

### Документация

- [x] Инструкция по деплою создана (500+ строк)
- [x] Шаблон .env создан с описанием переменных
- [x] README.md обновлен с секцией Production
- [x] DevOps roadmap актуализирован
- [x] Summary файл создан

### Конфигурация

- [x] docker-compose.prod.yml обновлен
- [x] Порты настроены (8004, 3004)
- [x] env_file добавлен для всех сервисов
- [x] Volume для БД настроен

### Развертывание

- [ ] Все сервисы запущены на production
- [ ] Backend API доступен (http://83.147.246.172:8004)
- [ ] Frontend доступен (http://83.147.246.172:3004)
- [ ] Бот работает в Telegram
- [ ] База данных создана и работает

---

## Известные ограничения

1. **Ручное развертывание** - требует выполнения команд вручную (будет автоматизировано в D3)
2. **SQLite БД** - для простоты, в production лучше PostgreSQL
3. **HTTP (не HTTPS)** - SSL будет настроен позже с nginx reverse proxy
4. **Без мониторинга** - метрики и alerts будут добавлены позже
5. **Без автоматических backup'ов** - нужно настроить cron job

---

## Следующие шаги

### Немедленные (после завершения D2)

1. Выполнить развертывание по инструкции
2. Проверить работоспособность всех сервисов
3. Отметить чекбоксы в summary
4. Создать commit

### Следующий спринт (D3)

**D3: Auto Deploy**

Цель: Автоматизировать деплой через GitHub Actions

Задачи:
- Создать workflow `.github/workflows/deploy.yml`
- Настроить SSH ключи в GitHub Secrets
- Автоматическое обновление при push в release
- Webhook или manual trigger
- Уведомления о статусе деплоя

---

## Полезные ссылки

### Проект

- [DevOps Roadmap](../devops-roadmap.md)
- [D1 Summary](./D1_COMPLETION_SUMMARY.md)
- [D2 Summary](./D2_COMPLETION_SUMMARY.md)
- [Manual Deploy Guide](../../../doc/guides/manual-deploy.md)

### Внешние

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/packages)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/keygen)

---

**Дата создания:** 18 октября 2025  
**Статус:** Документация завершена ✅ | Развертывание ожидает выполнения ⏳  
**Следующий спринт:** D3 - Auto Deploy

