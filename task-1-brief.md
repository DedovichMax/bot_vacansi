# Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml`
- Create: `.env.example`
- Create: `utils/__init__.py`
- Create: `collector/__init__.py`
- Create: `filter/__init__.py`
- Create: `notifier/__init__.py`
- Create: `web/__init__.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Consumes: None
- Produces: Project structure ready for implementation

## Steps

- [ ] **Step 1: Create requirements.txt**

```
telethon==1.34.0
pyyaml==6.0.1
fastapi==0.115.0
uvicorn==0.30.0
jinja2==3.1.4
apscheduler==3.10.4
python-multipart==0.0.9
aiofiles==24.1.0
```

- [ ] **Step 2: Create config.yaml**

```yaml
# Telegram settings
telegram:
  api_id: "YOUR_API_ID"
  api_hash: "YOUR_API_HASH"
  bot_token: "YOUR_BOT_TOKEN"
  target_channel: "@your_vacancy_channel"

# Channels to monitor
channels:
  - "@job_channel_1"
  - "@job_channel_2"

# Filters
filters:
  - name: "Junior позиции"
    phrases:
      - "junior media buyer"
      - "junior medua buyer"
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

# Schedule settings
schedule:
  check_interval_minutes: 15
  active_hours:
    start: 9
    end: 22

# Web panel
web:
  host: "0.0.0.0"
  port: 8000
  username: "admin"
  password: "your_secure_password"

# Logging
logging:
  level: "INFO"
  file: "logs/bot.log"
  max_size_mb: 10
  backup_count: 5

# Backups
backup:
  enabled: true
  interval_hours: 24
  keep_last: 7
```

- [ ] **Step 3: Create .env.example**

```
# Telegram API credentials (get from my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Bot token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token

# Target channel for notifications
TARGET_CHANNEL=@your_channel

# Web panel credentials
WEB_USERNAME=admin
WEB_PASSWORD=secure_password
```

- [ ] **Step 4: Create __init__.py files**

Create empty `__init__.py` in:
- `utils/`
- `collector/`
- `filter/`
- `notifier/`
- `web/`
- `tests/`

- [ ] **Step 5: Create directory structure**

```bash
mkdir -p database logs web/templates tests
```

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: project setup with config and dependencies"
```
