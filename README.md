# Telegram Vacancy Bot

Telegram-бот для мониторинга каналов с вакансиями. Сканирует указанные каналы, фильтрует сообщения по настроенным критериям и отправляет уведомления о подходящих вакансиях в целевой канал.

## Возможности

- **Мониторинг каналов** — сбор сообщений из 10-50+ каналов Telegram через Telethon (userbot)
- **Гибкая фильтрация** — поиск по категориям с точными фразами, поддержкаexclude-слов и весов
- **Автоматические уведомления** — отправка найденных вакансий в указанный канал
- **Детекция дубликатов** — повторная обработка одних и тех же сообщений исключена
- **Веб-панель** — FastAPI-интерфейс для управления каналами, фильтрами и просмотра статистики
- **Планировщик** — автоматическая проверка каналов по расписанию (interval через APScheduler)
- **Логирование** — ротация лог-файлов с настраиваемым уровнем детализации
- **Ошибки в БД** — все ошибки сохраняются в SQLite для анализа
- **Docker-деплой** — готовые Dockerfile и docker-compose для быстрого запуска

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+ |
| Telegram API | Telethon 1.34.0 |
| База данных | SQLite |
| Веб-сервер | FastAPI 0.115.0 + Uvicorn 0.30.0 |
| Шаблонизация | Jinja2 3.1.4 |
| Планировщик | APScheduler 3.10.4 |
| Конфигурация | PyYAML 6.0.1 |
| Контейнеризация | Docker |

## Структура проекта

```
TG_bot/
├── main.py                    # Точка входа
├── config.yaml                # Конфигурация
├── requirements.txt           # Зависимости
├── Dockerfile                 # Docker-сборка
├── docker-compose.yml         # Docker-запуск
├── .env.example               # Шаблон переменных окружения
├── database/
│   └── bot.db                 # SQLite БД (создается автоматически)
├── logs/
│   └── bot.log                # Логи (создаются автоматически)
├── collector/
│   └── telegram_collector.py  # Сбор сообщений из каналов
├── filter/
│   └── vacancy_filter.py      # Движок фильтрации
├── notifier/
│   └── telegram_notifier.py   # Отправка уведомлений
├── web/
│   ├── app.py                 # FastAPI приложение
│   ├── routes.py              # API маршруты
│   ├── auth.py                # HTTP Basic Auth
│   └── templates/
│       └── index.html         # Веб-интерфейс
├── utils/
│   ├── database.py            # Работа с БД
│   └── logger.py              # Настройка логирования
└── tests/
    ├── test_database.py
    ├── test_filter.py
    ├── test_collector.py
    ├── test_notifier.py
    ├── test_integration.py
    └── test_web.py
```

## Установка

### Локально

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd TG_bot
```

2. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

3. Скопируйте и настройте конфигурацию:

```bash
cp .env.example .env
```

Отредактируйте `config.yaml` — впишите реальные API-ключи и настройте каналы/фильтры.

4. Запустите бота:

```bash
python main.py
```

### Docker

1. Соберите Docker-образ:

```bash
docker build -t vacancy-bot .
```

2. Запустите контейнер:

```bash
docker-compose up -d
```

3. Проверьте статус:

```bash
docker-compose ps
docker-compose logs -f vacancy-bot
```

Для остановки: `docker-compose down`

## Конфигурация

### config.yaml

Основной файл конфигурации:

```yaml
# Telegram API (получить на my.telegram.org)
telegram:
  api_id: "YOUR_API_ID"
  api_hash: "YOUR_API_HASH"
  bot_token: "YOUR_BOT_TOKEN"
  target_channel: "@your_vacancy_channel"

# Каналы для мониторинга
channels:
  - "@job_channel_1"
  - "@job_channel_2"

# Фильтры вакансий
filters:
  - name: "Junior позиции"
    phrases:
      - "junior media buyer"
      - "младший медиабайер"
    exclude:
      - "senior junior"
    weight: 10

  - name: "Без опыта"
    phrases:
      - "без опыта"
      - "для начинающих"
    weight: 8

# Расписание проверок
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
```

### Параметры фильтра

| Параметр | Тип | Описание |
|----------|-----|----------|
| `name` | string | Название категории |
| `phrases` | list | Фразы для поиска (регистр не важен) |
| `exclude` | list | Фразы, при наличии которых вакансия игнорируется |
| `weight` | int | Вес фильтра (для сортировки по приоритету) |

### Переменные окружения (.env)

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
TARGET_CHANNEL=@your_channel
WEB_USERNAME=admin
WEB_PASSWORD=secure_password
```

## Получение API ключей

### Telegram API (api_id, api_hash)

1. Перейдите на https://my.telegram.org
2. Войдите в аккаунт Telegram
3. Перейдите в "API development tools"
4. Заполните форму создания приложения
5. Скопируйте `api_id` и `api_hash`

### Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

## Веб-панель

После запуска бота веб-панель доступна по адресу:

```
http://localhost:8000
```

Для доступа потребуется HTTP Basic Auth:
- Логин: указанный в `config.yaml` (по умолчанию `admin`)
- Пароль: указанный в `config.yaml`

### Возможности панели

- **Статистика** — общее количество вакансий, найденных сегодня, число каналов и фильтров
- **Управление каналами** — добавление и удаление отслеживаемых каналов
- **Управление фильтрами** — добавление и удаление фильтров поиска вакансий
- **История вакансий** — просмотр найденных вакансий с ссылками на оригинальные сообщения

### API эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работоспособности (без auth) |
| GET | `/api/channels` | Список каналов |
| POST | `/api/channels` | Добавить канал |
| DELETE | `/api/channels/{id}` | Удалить канал |
| GET | `/api/filters` | Список фильтров |
| POST | `/api/filters` | Добавить фильтр |
| DELETE | `/api/filters/{id}` | Удалить фильтр |
| GET | `/api/vacancies` | Список вакансий |
| GET | `/api/stats` | Статистика |

Все эндпоинты (кроме `/health`) требуют HTTP Basic Auth.

## Как это работает

1. **Сборщик** (Telethon userbot) подключается к Telegram и читает последние 10 сообщений из каждого канала
2. **Детекция дубликатов** — каждое обработанное сообщение помечается в БД, повторно не обрабатывается
3. **Фильтр** проверяет текст сообщения на совпадение с настроенными фразами, учитывая exclude-слова
4. **Уведомитель** форматирует и отправляет найденную вакансию в целевой канал
5. **Планировщик** повторяет цикл каждые N минут (настраивается в `config.yaml`)

## Деплой на Oracle Cloud Free

1. Создайте ARM instance (рекомендуется 2 OCPU, 4 GB RAM)

2. Подключитесь по SSH и установите Docker:

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
# Перелогиньтесь для применения группы
```

3. Склонируйте репозиторий и настройте конфигурацию:

```bash
git clone <repository-url>
cd TG_bot
cp .env.example .env
# Отредактируйте config.yaml с реальными API-ключами
```

4. Запустите в фоне:

```bash
docker-compose up -d
```

5. Для обновления:

```bash
docker-compose down
git pull
docker-compose up -d --build
```

## Разработка

### Запуск тестов

```bash
# Все тесты
python -m pytest tests/ -v

# Конкретный модуль
python -m pytest tests/test_filter.py -v

# С выводом coverage
python -m pytest tests/ -v --tb=short
```

### Добавление нового фильтра

Добавьте запись в `config.yaml`:

```yaml
filters:
  - name: "Название категории"
    phrases:
      - "ключевая фраза 1"
      - "ключевая фраза 2"
    exclude:
      - "нежелательная фраза"
    weight: 5
```

### Добавление нового канала

Добавьте канал в `config.yaml`:

```yaml
channels:
  - "@new_job_channel"
```

Или через веб-панель: `POST /api/channels` с телом `{"channel_name": "@new_channel"}`

## Решение проблем

### Бот не запускается

- Проверьте, что `config.yaml` существует и содержит корректный YAML
- Убедитесь, что API-ключи заполнены (без кавычек или с кавычками — оба варианта работают)
- Проверьте логи: `cat logs/bot.log` или `docker-compose logs vacancy-bot`

### Ошибки подключения к Telegram

- Убедитесь, что `api_id` и `api_hash` получены на my.telegram.org
- Проверьте правильность `bot_token` от @BotFather
- Telegram может блокировать при частых переподключениях. Подождите несколько минут

### Веб-панель не открывается

- Порт 8000 должен быть свободен
- Проверьте, что бот запущен: `docker-compose ps`
- Убедитесь, что firewall не блокирует порт

### База данных повреждена

SQLite-база создается автоматически. Если файл поврежден:

```bash
rm database/bot.db
# Бот пересоздаст базу при следующем запуске
```

### Логи слишком подробные / недостаточно подробные

Настройте уровень логирования в `config.yaml`:

```yaml
logging:
  level: "DEBUG"    # для отладки
  level: "WARNING"  # только предупреждения и ошибки
```

## Лицензия

MIT
