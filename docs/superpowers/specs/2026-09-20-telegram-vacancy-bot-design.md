# Telegram Vacancy Bot — Design Specification

**Дата:** 2026-09-20
**Статус:** Approved
**Версия:** 1.0

---

## Описание проекта

Telegram бот для мониторинга каналов с вакансиями. Бот автоматически проверяет указанные каналы на наличие вакансий, соответствующих заданным критериям, и отправляет уведомления в указанный канал.

**Ключевые особенности:**
- Мониторинг 10-50+ каналов Telegram
- Фильтрация по категориям с точными фразами
- Веб-панель для управления
- Бесплатный стек технологий
- Деплой на Oracle Cloud Free

---

## Цели и критерии успеха

### Цели
1. Автоматический сбор вакансий из Telegram каналов
2. Фильтрация по ключевым словам и фразам
3. Уведомления в отдельный канал Telegram
4. Веб-панель для управления фильтрами и каналами
5. Бесплатное размещение на Oracle Cloud Free

### Критерии успеха
- Бот работает 24/7 на Oracle Cloud Free
- Не пропускает вакансии, соответствующие фильтрам
- Не отправляет дубликаты
- Веб-панель доступна с авторизацией
- Все логи записываются

---

## Архитектура

### Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│              Telegram Channels (из списка в конфиге)         │
│  @channel1, @channel2, ... @channel50                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Collector (Telethon)                      │
│  • Читает новые сообщения ТОЛЬКО из указанных каналов       │
│  • Работает как userbot (аккаунт Telegram)                  │
│  • Проверяет каждые 15-30 минут                             │
│  • Retry при ошибках (5, 10, 30 мин)                        │
│  • Детекция дубликатов (message_id + channel_id)            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Filter Engine                            │
│  • Сверяет сообщения с фильтрами из конфига                 │
│  • Категории + точные фразы + исключения                    │
│  • Присваивает вес/приоритет                                │
│  • Игнорирует уже обработанные сообщения                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Notifier (Bot API)                       │
│  • Отправляет совпадения в указанный канал                  │
│  • Форматирует сообщение (категория, фраза, ссылка)         │
│  • Не отправляет дубликаты                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                          │
│  • Каналы для мониторинга                                   │
│  • Фильтры (категории, фразы, исключения)                  │
│  • История найденных вакансий                               │
│  • Обработанные сообщения (для детекции дубликатов)          │
│  • Лог работы и ошибок                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Web Panel (FastAPI)                      │
│  • Просмотр найденных вакансий                              │
│  • Управление каналами (добавить/удалить)                   │
│  • Управление фильтрами (категории, фразы)                  │
│  • Статистика (сколько проверок, совпадений)                │
│  • Логи работы                                              │
│  • Авторизация (логин/пароль)                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Logging & Monitoring                     │
│  • Файл logs/bot.log с ротацией                             │
│  • Уведомление в Telegram при критических ошибках           │
│  • Health check endpoint (/health)                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Deployment                               │
│  • Dockerfile + docker-compose.yml                          │
│  • Автозапуск через systemd                                 │
│  • Резервное копирование БД раз в день                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Технологии

| Компонент | Технология | Зачем |
|-----------|-----------|-------|
| Язык | Python 3.11+ | Простота, экосистема |
| Чтение каналов | Telethon | Userbot, читает любые публичные каналы |
| База данных | SQLite | Бесплатно, файловая, без сервера |
| Веб-панель | FastAPI + Jinja2 | Простой интерфейс в браузере |
| Планировщик | APScheduler | Расписание проверок |
| Хостинг | Oracle Cloud Free | Всегда бесплатно, 24/7 |
| Контейнеризация | Docker | Упрощённый деплой |

---

## Файловая структура

```
TG_bot/
├── main.py                    # Точка входа
├── config.yaml                # Конфигурация
├── requirements.txt           # Зависимости
├── Dockerfile                 # Для деплоя
├── docker-compose.yml         # Для запуска
├── .env.example               # Пример переменных окружения
├── database/
│   └── bot.db                 # SQLite база данных
├── logs/
│   └── bot.log                # Логи
├── collector/
│   ├── __init__.py
│   └── telegram_collector.py  # Сбор сообщений
├── filter/
│   ├── __init__.py
│   └── vacancy_filter.py      # Движок фильтрации
├── notifier/
│   ├── __init__.py
│   └── telegram_notifier.py   # Отправка уведомлений
├── web/
│   ├── __init__.py
│   ├── app.py                 # FastAPI приложение
│   ├── routes.py              # Маршруты API
│   ├── auth.py                # Авторизация
│   └── templates/
│       └── index.html         # Веб-интерфейс
└── utils/
    ├── __init__.py
    ├── database.py            # Работа с БД
    └── logger.py              # Настройка логирования
```

---

## Конфигурация

### config.yaml

```yaml
# Telegram настройки
telegram:
  api_id: "YOUR_API_ID"        # my.telegram.org
  api_hash: "YOUR_API_HASH"    # my.telegram.org
  bot_token: "YOUR_BOT_TOKEN"  # @BotFather
  target_channel: "@your_vacancy_channel"  # Куда слать уведомления

# Каналы для мониторинга (только из этого списка)
channels:
  - "@job_channel_1"
  - "@job_channel_2"
  - "@job_channel_3"

# Фильтры
filters:
  - name: "Junior позиции"
    phrases:
      - "junior media buyer"
      - "junior medua buyer"    # опечатка
      - "младший медиабайер"
      - "начинающий медиабайер"
    exclude:
      - "senior junior"
    weight: 10

  - name: "Без опыта"
    phrases:
      - "без опыта"
      - "для начинающих"
      - "обучим с нуля"
      - "обучение с нуля"
    weight: 8

  - name: "Farmer"
    phrases:
      - "farmer"
      - "фармер"
      - "accounts farmer"
      - "аккаунт фармер"
    weight: 7

  - name: "Ассистент"
    phrases:
      - "assistant media buyer"
      - "assistent media buyer"
      - "ассистент медиабайер"
      - "помощник медиабайера"
    weight: 8

# Настройки проверки
schedule:
  check_interval_minutes: 15
  active_hours:
    start: 9
    end: 22

# Веб-панель
web:
  host: "0.0.0.0"
  port: 8000
  username: "admin"
  password: "your_secure_password"

# Логирование
logging:
  level: "INFO"
  file: "logs/bot.log"
  max_size_mb: 10
  backup_count: 5

# Бэкапы
backup:
  enabled: true
  interval_hours: 24
  keep_last: 7
```

---

## Компоненты системы

### 1. Collector (telegram_collector.py)

**Ответственность:** Чтение сообщений из Telegram каналов

**Функции:**
- Подключение к Telegram через Telethon (userbot)
- Чтение последних N сообщений из каждого канала
- Проверка на дубликаты (message_id + channel_id)
- Retry логика при ошибках
- Логирование действий

**Интерфейс:**
```python
class TelegramCollector:
    def __init__(self, config: dict)
    async def start(self) -> None
    async def stop(self) -> None
    async def check_channels(self) -> List[Message]
    async def get_new_messages(self, channel: str) -> List[Message]
```

**Обработка ошибок:**
- Retry: 5, 10, 30 минут при ошибках Telegram API
- Логирование ошибок в файл
- Уведомление в Telegram при критических ошибках

---

### 2. Filter Engine (vacancy_filter.py)

**Ответственность:** Фильтрация сообщений по критериям

**Функции:**
- Загрузка фильтров из config.yaml
- Проверка сообщений на соответствие фильтрам
- Точное совпадение фраз (не отдельные слова)
- Исключение нежелательных фраз
- Присвоение веса/приоритета

**Интерфейс:**
```python
class VacancyFilter:
    def __init__(self, config: dict)
    def load_filters(self) -> None
    def check_message(self, message: Message) -> List[FilterResult]
    def get_filter_stats(self) -> dict
```

**Логика фильтрации:**
1. Загрузить все фильтры из конфига
2. Для каждого сообщения проверить каждый фильтр
3. Искать ТОЧНЫЕ фразы (не отдельные слова)
4. Проверять исключения
5. Если есть совпадение — вернуть результат с весом

---

### 3. Notifier (telegram_notifier.py)

**Ответственность:** Отправка уведомлений в Telegram канал

**Функции:**
- Отправка совпадений в указанный канал
- Форматирование сообщений
- Проверка на дубликаты перед отправкой
- Обработка ошибок отправки

**Интерфейс:**
```python
class TelegramNotifier:
    def __init__(self, config: dict)
    async def send_vacancy(self, vacancy: FilterResult) -> bool
    async def send_error(self, error: str) -> bool
    def format_message(self, vacancy: FilterResult) -> str
```

**Формат сообщения:**
```
🔍 Найдена вакансия!

📁 Категория: {category}
🔑 Фраза: {phrase}
📡 Канал: {channel}
📅 Дата: {date}
🔗 Ссылка: {link}

---
{text}
```

---

### 4. Database (utils/database.py)

**Ответственность:** Хранение данных

**Таблицы:**
```sql
-- Каналы для мониторинга
CREATE TABLE channels (
    id INTEGER PRIMARY KEY,
    channel_name TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Фильтры
CREATE TABLE filters (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phrases JSON NOT NULL,
    exclude JSON,
    weight INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Найденные вакансии
CREATE TABLE vacancies (
    id INTEGER PRIMARY KEY,
    channel_name TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    category TEXT,
    matched_phrase TEXT,
    weight INTEGER,
    text TEXT,
    link TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(channel_name, message_id)
);

-- Обработанные сообщения (для детекции дубликатов)
CREATE TABLE processed_messages (
    id INTEGER PRIMARY KEY,
    channel_name TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(channel_name, message_id)
);

-- Лог ошибок
CREATE TABLE error_log (
    id INTEGER PRIMARY KEY,
    error_type TEXT NOT NULL,
    error_message TEXT,
    channel_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 5. Web Panel (web/app.py)

**Ответственность:** Веб-интерфейс для управления

**Маршруты:**
```python
GET  /                    # Главная страница
GET  /api/vacancies       # Список вакансий
GET  /api/channels        # Список каналов
POST /api/channels        # Добавить канал
DELETE /api/channels/{id} # Удалить канал
GET  /api/filters         # Список фильтров
POST /api/filters         # Добавить фильтр
PUT  /api/filters/{id}    # Редактировать фильтр
DELETE /api/filters/{id}  # Удалить фильтр
GET  /api/stats           # Статистика
GET  /api/logs            # Логи
GET  /health              # Health check
```

**Авторизация:**
- Basic Auth (логин/пароль из конфига)
- Сессия через cookie

---

### 6. Scheduler (APScheduler)

**Ответственность:** Расписание проверок

**Задачи:**
- `check_channels` — каждые 15-30 минут
- `backup_database` — раз в 24 часа
- `cleanup_old_logs` — раз в неделю

---

## Деплой

### Oracle Cloud Free Setup

1. Создать ARM instance (4 OCPU, 24 GB RAM — бесплатно)
2. Установить Docker и Docker Compose
3. Склонировать репозиторий
4. Настроить config.yaml
5. Запустить через docker-compose

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs database

CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  vacancy-bot:
    build: .
    container_name: vacancy-bot
    restart: always
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./database:/app/database
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    environment:
      - TZ=Europe/Moscow
```

---

## Безопасность

1. **API ключи** — хранить в config.yaml (не в коде)
2. **Веб-панель** — авторизация (логин/пароль)
3. **Бот токен** — не публиковать, хранить в конфиге
4. **SQLite файл** — доступ только для приложения

---

## Требования к Oracle Cloud Free

- **OCPU:** 2 (достаточно для Python бота)
- **RAM:** 4 GB (достаточно)
- **Storage:** 50 GB (достаточно для БД и логов)
- **Стоимость:** Бесплатно навсегда

---

## Этапы реализации

### Этап 1: Базовый каркас
- Настройка проекта
- Реализация Collector
- Реализация Filter Engine
- Реализация Notifier

### Этап 2: База данных
- Создание таблиц
- Реализация CRUD операций
- Детекция дубликатов

### Этап 3: Веб-панель
- FastAPI приложение
- Маршруты API
- Веб-интерфейс
- Авторизация

### Этап 4: Деплой
- Dockerfile
- docker-compose.yml
- Инструкция по деплою на Oracle Cloud

### Этап 5: Тестирование
- Unit тесты
- Интеграционные тесты
- Тестирование на реальных каналах

---

## Открытые вопросы

1. Нужен ли веб-интерфейс для мобильных устройств?
2. Нужна ли интеграция с другими мессенджерами?
3. Нужна ли аналитика (сколько вакансий по категориям)?

---

## Приемочный критерий

Бот считается готовым, когда:
1. ✅ Работает 24/7 на Oracle Cloud Free
2. ✅ Мониторит 10-50+ каналов
3. ✅ Не пропускает вакансии, соответствующие фильтрам
4. ✅ Не отправляет дубликаты
5. ✅ Веб-панель доступна с авторизацией
6. ✅ Все логи записываются
7. ✅ Retry логика работает при ошибках
