# Спринт D2 - Следующие шаги для развертывания

**Статус:** Документация и конфигурация завершены ✅  
**Следующий шаг:** Ручное развертывание на сервер

---

## Что уже сделано ✅

### 1. Шаблон конфигурации
- ✅ Создан `env.production.template` с описанием всех переменных
- ✅ Подробные комментарии к каждому параметру
- ✅ Примеры значений

### 2. Docker Compose обновлен
- ✅ Порты настроены: 8004 (backend), 3004 (frontend)
- ✅ Все сервисы используют `.env` файл
- ✅ Volume для базы данных настроен

### 3. Подробная инструкция
- ✅ Создана `doc/guides/manual-deploy.md` (500+ строк)
- ✅ Пошаговые инструкции для всех этапов
- ✅ Команды для Linux/macOS/Windows
- ✅ Раздел устранения неполадок
- ✅ Команды управления сервисами

### 4. Документация обновлена
- ✅ README.md дополнен секцией "Production Deployment"
- ✅ DevOps roadmap актуализирован
- ✅ Создан план реализации D2
- ✅ Создан completion summary

---

## Что нужно сделать вручную 🔧

### Шаг 1: Подготовка файла .env

```bash
# 1. Скопировать шаблон
cp env.production.template .env

# 2. Открыть .env в редакторе
# Windows: notepad .env
# Linux/macOS: nano .env

# 3. Заполнить обязательные параметры:
# - TELEGRAM_BOT_TOKEN=your_actual_bot_token
# - OPENROUTER_API_KEY=your_actual_api_key

# 4. Проверить, что NEXT_PUBLIC_STATS_API_URL=http://83.147.246.172:8004/api/v1
```

**Где взять токены:**
- Telegram Bot Token: https://t.me/botfather → `/newbot`
- OpenRouter API Key: https://openrouter.ai/keys

### Шаг 2: Подключение к серверу

**Windows PowerShell:**
```powershell
ssh -i devops\systech_admin_key.txt systech@83.147.246.172
```

**Linux/macOS/Git Bash:**
```bash
ssh -i devops/systech_admin_key.txt systech@83.147.246.172
```

### Шаг 3: Создание рабочей директории на сервере

После подключения к серверу:

```bash
# Создать директорию
sudo mkdir -p /opt/systech/andreymakarov

# Установить владельца
sudo chown -R systech:systech /opt/systech/andreymakarov

# Перейти в директорию
cd /opt/systech/andreymakarov

# Создать директорию для базы данных
mkdir -p backend/data
```

### Шаг 4: Копирование файлов (из нового терминала на локальном компьютере)

**Windows PowerShell:**
```powershell
# Не закрывайте SSH сессию! Откройте новый терминал

# Перейти в директорию проекта
cd C:\Dev\systech-aidd\systech-aidd

# Скопировать docker-compose
scp -i devops\systech_admin_key.txt docker-compose.prod.yml systech@83.147.246.172:/opt/systech/andreymakarov/

# Скопировать .env
scp -i devops\systech_admin_key.txt .env systech@83.147.246.172:/opt/systech/andreymakarov/
```

**Linux/macOS/Git Bash:**
```bash
# Скопировать docker-compose
scp -i devops/systech_admin_key.txt docker-compose.prod.yml systech@83.147.246.172:/opt/systech/andreymakarov/

# Скопировать .env
scp -i devops/systech_admin_key.txt .env systech@83.147.246.172:/opt/systech/andreymakarov/
```

### Шаг 5: Запуск на сервере

Вернитесь в окно с SSH подключением:

```bash
cd /opt/systech/andreymakarov

# Загрузить образы
docker-compose -f docker-compose.prod.yml pull

# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус (все должны быть "Up")
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

### Шаг 6: Проверка работоспособности

**На сервере:**
```bash
# Backend
curl http://localhost:8004/

# Frontend
curl -I http://localhost:3004/

# Статистика
curl http://localhost:8004/api/v1/stats?period=day
```

**С вашего компьютера (в браузере):**
- Backend API: http://83.147.246.172:8004/docs
- Frontend: http://83.147.246.172:3004
- Stats API: http://83.147.246.172:8004/api/v1/stats?period=day

**В Telegram:**
1. Найдите вашего бота
2. Отправьте `/start`
3. Отправьте любое сообщение
4. Бот должен ответить в течение 1-5 секунд

---

## Подробная инструкция

Полная пошаговая инструкция со всеми деталями:

📖 **[doc/guides/manual-deploy.md](doc/guides/manual-deploy.md)**

В инструкции описаны:
- Подробные команды для каждого шага
- Ожидаемые результаты
- 8 типичных проблем и их решения
- Команды управления сервисами
- Мониторинг и backup

---

## Быстрая проверка (чек-лист)

После выполнения всех шагов проверьте:

- [ ] SSH подключение к серверу работает
- [ ] Файл .env создан и содержит реальные токены
- [ ] docker-compose.prod.yml скопирован на сервер
- [ ] .env скопирован на сервер
- [ ] Образы загружены на сервер
- [ ] Все 3 контейнера в статусе "Up"
- [ ] Backend API отвечает: http://83.147.246.172:8004/docs
- [ ] Frontend загружается: http://83.147.246.172:3004
- [ ] Бот отвечает в Telegram
- [ ] База данных создана (есть файл backend/data/bot.db)

---

## Если что-то пошло не так

### Контейнер не запускается

```bash
# Посмотреть логи проблемного сервиса
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs bot
docker-compose -f docker-compose.prod.yml logs frontend
```

### Порт занят

```bash
# Найти процесс
sudo lsof -i :8004
sudo lsof -i :3004

# Остановить
sudo kill -9 <PID>
```

### Полный перезапуск

```bash
# Остановить все
docker-compose -f docker-compose.prod.yml down

# Запустить заново
docker-compose -f docker-compose.prod.yml up -d
```

**Больше решений:** см. раздел "7. Устранение неполадок" в `doc/guides/manual-deploy.md`

---

## Управление сервисами

```bash
# Остановить
docker-compose -f docker-compose.prod.yml stop

# Запустить
docker-compose -f docker-compose.prod.yml start

# Перезапустить
docker-compose -f docker-compose.prod.yml restart

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f

# Статус
docker-compose -f docker-compose.prod.yml ps

# Обновить образы
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## После успешного деплоя

### 1. Сделать коммит

После успешной проверки работоспособности:

```bash
git add .
git commit -m "docs: complete D2 sprint - Manual Deploy"
git push
```

### 2. Обновить статус

В файле `devops/doc/devops-roadmap.md` изменить:
```
| D2 | Развертывание на сервер | ✅ Завершено (18.10.2025) | [План D2](plans/d2-manual-deploy.md) |
```

### 3. Отметить чекбоксы

В файле `devops/doc/D2_COMPLETION_SUMMARY.md` отметить все выполненные пункты.

---

## Следующий спринт: D3

После завершения D2 можно переходить к **D3: Auto Deploy**

Цель D3:
- Автоматизировать деплой через GitHub Actions
- Настроить SSH в GitHub Secrets
- Автоматическое обновление при push в release
- Уведомления о статусе

---

## Полезные ссылки

- 📖 [Подробная инструкция](doc/guides/manual-deploy.md)
- 📊 [D2 Completion Summary](devops/doc/D2_COMPLETION_SUMMARY.md)
- 📋 [План реализации D2](devops/doc/plans/d2-manual-deploy.md)
- 🗺️ [DevOps Roadmap](devops/doc/devops-roadmap.md)
- 🏗️ [Architecture Overview](doc/guides/architecture-overview.md)

---

**Успешного развертывания! 🚀**

Если возникнут вопросы или проблемы, обращайтесь к подробной инструкции в `doc/guides/manual-deploy.md`.

