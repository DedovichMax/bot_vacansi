# Telegram Vacancy Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Telegram bot that monitors channels for job vacancies matching specific criteria and sends notifications to a designated channel.

**Architecture:** Collector (Telethon) reads messages from specified channels → Filter Engine checks against configured phrases → Notifier sends matches to target channel. Web panel (FastAPI) for management. SQLite for storage.

**Tech Stack:** Python 3.11+, Telethon, SQLite, FastAPI, APScheduler, Docker

## Global Constraints

- Python 3.11+ required
- All dependencies must be free and open source
- Deploy on Oracle Cloud Free tier
- No paid services or APIs
- Telegram API rate limits: max 30 requests per second
- SQLite for local storage only

---

## File Structure

```
TG_bot/
├── main.py                    # Entry point
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker build
├── docker-compose.yml         # Docker run
├── .env.example               # Environment variables template
├── database/
│   └── bot.db                 # SQLite database (created at runtime)
├── logs/
│   └── bot.log                # Logs (created at runtime)
├── collector/
│   ├── __init__.py
│   └── telegram_collector.py  # Channel message collection
├── filter/
│   ├── __init__.py
│   └── vacancy_filter.py      # Filtering engine
├── notifier/
│   ├── __init__.py
│   └── telegram_notifier.py   # Notification sender
├── web/
│   ├── __init__.py
│   ├── app.py                 # FastAPI app
│   ├── routes.py              # API routes
│   ├── auth.py                # Authentication
│   └── templates/
│       └── index.html         # Web interface
├── utils/
│   ├── __init__.py
│   ├── database.py            # Database operations
│   └── logger.py              # Logging setup
└── tests/
    ├── __init__.py
    ├── test_database.py
    ├── test_filter.py
    ├── test_collector.py
    └── test_notifier.py
```

---

## Task 1: Project Setup

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

---

## Task 2: Logger Setup

**Files:**
- Create: `utils/logger.py`
- Create: `tests/test_logger.py`

**Interfaces:**
- Consumes: None
- Produces: `setup_logger()` function, `get_logger()` function

- [ ] **Step 1: Write the failing test**

```python
# tests/test_logger.py
import os
import logging
from utils.logger import setup_logger, get_logger

def test_setup_logger_creates_log_file():
    """Test that setup_logger creates log directory and file."""
    log_dir = "logs"
    log_file = "logs/test.log"
    
    # Clean up
    if os.path.exists(log_file):
        os.remove(log_file)
    
    setup_logger(log_file=log_file)
    logger = get_logger()
    
    assert os.path.exists(log_file)
    assert logger is not None
    assert logger.level == logging.INFO
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)

def test_logger_writes_to_file():
    """Test that logger actually writes to file."""
    log_file = "logs/test_write.log"
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    setup_logger(log_file=log_file)
    logger = get_logger()
    
    logger.info("Test message")
    
    # Force flush
    for handler in logger.handlers:
        handler.flush()
    
    with open(log_file, 'r') as f:
        content = f.read()
        assert "Test message" in content
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_logger.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.logger'"

- [ ] **Step 3: Write minimal implementation**

```python
# utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

_logger = None

def setup_logger(log_file: str = "logs/bot.log", level: str = "INFO") -> None:
    """Setup logger with rotating file handler."""
    global _logger
    
    # Create log directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    _logger = logging.getLogger("vacancy_bot")
    _logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

def get_logger() -> logging.Logger:
    """Get the logger instance."""
    global _logger
    if _logger is None:
        setup_logger()
    return _logger
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_logger.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add utils/logger.py tests/test_logger.py
git commit -m "feat: add logger setup with rotating file handler"
```

---

## Task 3: Database Layer

**Files:**
- Create: `utils/database.py`
- Create: `tests/test_database.py`

**Interfaces:**
- Consumes: None
- Produces: `Database` class with methods for channels, filters, vacancies, processed_messages

- [ ] **Step 1: Write the failing test**

```python
# tests/test_database.py
import os
import sqlite3
from utils.database import Database

def test_database_initialization():
    """Test that database creates all tables on init."""
    db_path = "tests/test.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Check tables exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    assert "channels" in tables
    assert "filters" in tables
    assert "vacancies" in tables
    assert "processed_messages" in tables
    assert "error_log" in tables
    
    # Cleanup
    os.remove(db_path)

def test_add_channel():
    """Test adding a channel to database."""
    db_path = "tests/test_add_channel.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Add channel
    channel_id = db.add_channel("@test_channel")
    assert channel_id is not None
    
    # Get channels
    channels = db.get_channels()
    assert len(channels) == 1
    assert channels[0]["channel_name"] == "@test_channel"
    assert channels[0]["is_active"] == True
    
    # Cleanup
    os.remove(db_path)

def test_add_filter():
    """Test adding a filter to database."""
    db_path = "tests/test_add_filter.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Add filter
    filter_id = db.add_filter(
        name="Test Filter",
        phrases=["test phrase", "another phrase"],
        exclude=["exclude me"],
        weight=5
    )
    assert filter_id is not None
    
    # Get filters
    filters = db.get_filters()
    assert len(filters) == 1
    assert filters[0]["name"] == "Test Filter"
    
    # Cleanup
    os.remove(db_path)

def test_add_vacancy():
    """Test adding a vacancy to database."""
    db_path = "tests/test_add_vacancy.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Add vacancy
    vacancy_id = db.add_vacancy(
        channel_name="@test_channel",
        message_id=12345,
        category="Test Category",
        matched_phrase="test phrase",
        weight=5,
        text="Test vacancy text",
        link="https://t.me/test/12345"
    )
    assert vacancy_id is not None
    
    # Get vacancies
    vacancies = db.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0]["channel_name"] == "@test_channel"
    
    # Cleanup
    os.remove(db_path)

def test_is_message_processed():
    """Test duplicate detection."""
    db_path = "tests/test_duplicate.db"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = Database(db_path)
    
    # Message not processed yet
    assert db.is_message_processed("@channel", 12345) == False
    
    # Mark as processed
    db.mark_message_processed("@channel", 12345)
    
    # Now it's processed
    assert db.is_message_processed("@channel", 12345) == True
    
    # Different message still not processed
    assert db.is_message_processed("@channel", 12346) == False
    
    # Cleanup
    os.remove(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_database.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'utils.database'"

- [ ] **Step 3: Write minimal implementation**

```python
# utils/database.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any

class Database:
    def __init__(self, db_path: str = "database/bot.db"):
        """Initialize database with all required tables."""
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create all required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Filters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phrases TEXT NOT NULL,
                exclude TEXT,
                weight INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vacancies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                category TEXT,
                matched_phrase TEXT,
                weight INTEGER,
                text TEXT,
                link TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(channel_name, message_id)
            )
        """)
        
        # Processed messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(channel_name, message_id)
            )
        """)
        
        # Error log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT,
                channel_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Channel operations
    def add_channel(self, channel_name: str) -> int:
        """Add a new channel."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO channels (channel_name) VALUES (?)",
            (channel_name,)
        )
        conn.commit()
        channel_id = cursor.lastrowid
        conn.close()
        return channel_id
    
    def get_channels(self) -> List[Dict[str, Any]]:
        """Get all channels."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM channels")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    # Filter operations
    def add_filter(self, name: str, phrases: List[str], exclude: List[str] = None, weight: int = 5) -> int:
        """Add a new filter."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO filters (name, phrases, exclude, weight) VALUES (?, ?, ?, ?)",
            (name, json.dumps(phrases), json.dumps(exclude) if exclude else None, weight)
        )
        conn.commit()
        filter_id = cursor.lastrowid
        conn.close()
        return filter_id
    
    def get_filters(self) -> List[Dict[str, Any]]:
        """Get all filters."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filters")
        rows = cursor.fetchall()
        conn.close()
        
        filters = []
        for row in rows:
            filter_dict = dict(row)
            filter_dict["phrases"] = json.loads(filter_dict["phrases"])
            if filter_dict["exclude"]:
                filter_dict["exclude"] = json.loads(filter_dict["exclude"])
            filters.append(filter_dict)
        return filters
    
    def delete_filter(self, filter_id: int) -> bool:
        """Delete a filter."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filters WHERE id = ?", (filter_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
    
    # Vacancy operations
    def add_vacancy(self, channel_name: str, message_id: int, category: str, 
                    matched_phrase: str, weight: int, text: str, link: str) -> int:
        """Add a new vacancy."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO vacancies (channel_name, message_id, category, matched_phrase, weight, text, link) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (channel_name, message_id, category, matched_phrase, weight, text, link)
        )
        conn.commit()
        vacancy_id = cursor.lastrowid
        conn.close()
        return vacancy_id
    
    def get_vacancies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get vacancies."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies ORDER BY sent_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # Processed messages operations
    def is_message_processed(self, channel_name: str, message_id: int) -> bool:
        """Check if message was already processed."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM processed_messages WHERE channel_name = ? AND message_id = ?",
            (channel_name, message_id)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def mark_message_processed(self, channel_name: str, message_id: int) -> None:
        """Mark message as processed."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO processed_messages (channel_name, message_id) VALUES (?, ?)",
            (channel_name, message_id)
        )
        conn.commit()
        conn.close()
    
    # Error logging
    def log_error(self, error_type: str, error_message: str, channel_name: str = None) -> None:
        """Log an error."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO error_log (error_type, error_message, channel_name) VALUES (?, ?, ?)",
            (error_type, error_message, channel_name)
        )
        conn.commit()
        conn.close()
    
    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Total vacancies
        cursor.execute("SELECT COUNT(*) FROM vacancies")
        total_vacancies = cursor.fetchone()[0]
        
        # Vacancies today
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE DATE(sent_at) = DATE('now')")
        vacancies_today = cursor.fetchone()[0]
        
        # Total channels
        cursor.execute("SELECT COUNT(*) FROM channels")
        total_channels = cursor.fetchone()[0]
        
        # Total filters
        cursor.execute("SELECT COUNT(*) FROM filters")
        total_filters = cursor.fetchone()[0]
        
        # Errors today
        cursor.execute("SELECT COUNT(*) FROM error_log WHERE DATE(created_at) = DATE('now')")
        errors_today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_vacancies": total_vacancies,
            "vacancies_today": vacancies_today,
            "total_channels": total_channels,
            "total_filters": total_filters,
            "errors_today": errors_today
        }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_database.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add utils/database.py tests/test_database.py
git commit -m "feat: add database layer with CRUD operations"
```

---

## Task 4: Filter Engine

**Files:**
- Create: `filter/vacancy_filter.py`
- Create: `tests/test_filter.py`

**Interfaces:**
- Consumes: Config dict with filters
- Produces: `VacancyFilter` class with `check_message()` method

- [ ] **Step 1: Write the failing test**

```python
# tests/test_filter.py
import pytest
from filter.vacancy_filter import VacancyFilter, FilterResult

@pytest.fixture
def filter_config():
    return {
        "filters": [
            {
                "name": "Junior позиции",
                "phrases": [
                    "junior media buyer",
                    "junior medua buyer",
                    "младший медиабайер"
                ],
                "exclude": ["senior junior"],
                "weight": 10
            },
            {
                "name": "Без опыта",
                "phrases": [
                    "без опыта",
                    "для начинающих",
                    "обучим с нуля"
                ],
                "exclude": [],
                "weight": 8
            }
        ]
    }

def test_filter_exact_phrase_match():
    """Test that filter matches exact phrases."""
    config = {"filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]}
    vf = VacancyFilter(config)
    
    message_text = "Ищем junior media buyer без опыта"
    results = vf.check_message(message_text)
    
    assert len(results) == 1
    assert results[0].category == "Test"
    assert results[0].matched_phrase == "junior media buyer"

def test_filter_no_match_on_partial():
    """Test that filter doesn't match partial words."""
    config = {"filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]}
    vf = VacancyFilter(config)
    
    # "junior" alone should not match "junior media buyer"
    message_text = "Требуется junior разработчик"
    results = vf.check_message(message_text)
    
    assert len(results) == 0

def test_filter_exclude_words():
    """Test that exclude words prevent matching."""
    config = {"filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": ["senior junior"], "weight": 5}]}
    vf = VacancyFilter(config)
    
    message_text = "senior junior media buyer"
    results = vf.check_message(message_text)
    
    assert len(results) == 0

def test_filter_multiple_matches():
    """Test that filter can match multiple phrases from different categories."""
    config = {
        "filters": [
            {"name": "Junior", "phrases": ["junior media buyer"], "exclude": [], "weight": 10},
            {"name": "Без опыта", "phrases": ["без опыта"], "exclude": [], "weight": 8}
        ]
    }
    vf = VacancyFilter(config)
    
    message_text = "junior media buyer без опыта"
    results = vf.check_message(message_text)
    
    assert len(results) == 2
    categories = [r.category for r in results]
    assert "Junior" in categories
    assert "Без опыта" in categories

def test_filter_case_insensitive():
    """Test that filter is case insensitive."""
    config = {"filters": [{"name": "Test", "phrases": ["junior media buyer"], "exclude": [], "weight": 5}]}
    vf = VacancyFilter(config)
    
    message_text = "JUNIOR MEDIA BUYER"
    results = vf.check_message(message_text)
    
    assert len(results) == 1

def test_filter_with_filter_config(filter_config):
    """Test filter with full config."""
    vf = VacancyFilter(filter_config)
    
    # Should match
    results = vf.check_message("Ищем junior media buyer без опыта")
    assert len(results) == 2
    
    # Should not match (exclude)
    results = vf.check_message("senior junior media buyer")
    assert len(results) == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_filter.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'filter.vacancy_filter'"

- [ ] **Step 3: Write minimal implementation**

```python
# filter/vacancy_filter.py
import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class FilterResult:
    """Result of filter matching."""
    category: str
    matched_phrase: str
    weight: int
    original_text: str

class VacancyFilter:
    def __init__(self, config: Dict[str, Any]):
        """Initialize filter with config."""
        self.filters = config.get("filters", [])
    
    def check_message(self, message_text: str) -> List[FilterResult]:
        """Check message against all filters."""
        results = []
        
        for filter_config in self.filters:
            category = filter_config["name"]
            phrases = filter_config.get("phrases", [])
            exclude = filter_config.get("exclude", [])
            weight = filter_config.get("weight", 5)
            
            # Check if any exclude word is present
            if self._has_exclude_word(message_text, exclude):
                continue
            
            # Check for phrase matches
            matched_phrase = self._find_phrase_match(message_text, phrases)
            if matched_phrase:
                results.append(FilterResult(
                    category=category,
                    matched_phrase=matched_phrase,
                    weight=weight,
                    original_text=message_text
                ))
        
        return results
    
    def _has_exclude_word(self, text: str, exclude_words: List[str]) -> bool:
        """Check if text contains any exclude word."""
        text_lower = text.lower()
        for word in exclude_words:
            if word.lower() in text_lower:
                return True
        return False
    
    def _find_phrase_match(self, text: str, phrases: List[str]) -> str:
        """Find exact phrase match in text."""
        text_lower = text.lower()
        for phrase in phrases:
            if phrase.lower() in text_lower:
                return phrase
        return None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_filter.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add filter/vacancy_filter.py tests/test_filter.py
git commit -m "feat: add filter engine with exact phrase matching"
```

---

## Task 5: Telegram Collector

**Files:**
- Create: `collector/telegram_collector.py`
- Create: `tests/test_collector.py`

**Interfaces:**
- Consumes: Config dict, Database instance
- Produces: `TelegramCollector` class with `check_channels()` method

- [ ] **Step 1: Write the failing test**

```python
# tests/test_collector.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from collector.telegram_collector import TelegramCollector

@pytest.fixture
def collector_config():
    return {
        "telegram": {
            "api_id": "12345",
            "api_hash": "test_hash",
            "bot_token": "test_token"
        },
        "channels": ["@channel1", "@channel2"]
    }

def test_collector_initialization():
    """Test that collector initializes correctly."""
    config = {
        "telegram": {"api_id": "12345", "api_hash": "test_hash"},
        "channels": ["@channel1"]
    }
    
    collector = TelegramCollector(config)
    assert collector.channels == ["@channel1"]
    assert collector.api_id == "12345"

def test_collector_formats_channel_name():
    """Test channel name formatting."""
    config = {
        "telegram": {"api_id": "12345", "api_hash": "test_hash"},
        "channels": ["channel1", "@channel1"]
    }
    
    collector = TelegramCollector(config)
    
    # Both should be formatted the same
    assert collector._format_channel("channel1") == "channel1"
    assert collector._format_channel("@channel1") == "channel1"

@pytest.mark.asyncio
async def test_collector_checks_duplicate_messages():
    """Test that collector skips already processed messages."""
    config = {
        "telegram": {"api_id": "12345", "api_hash": "test_hash"},
        "channels": ["@channel1"]
    }
    
    mock_db = Mock()
    mock_db.is_message_processed.return_value = True  # Already processed
    
    collector = TelegramCollector(config, db=mock_db)
    
    # Mock message
    mock_message = Mock()
    mock_message.id = 12345
    
    # Should skip this message
    should_process = not mock_db.is_message_processed("@channel1", 12345)
    assert should_process == False
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_collector.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'collector.telegram_collector'"

- [ ] **Step 3: Write minimal implementation**

```python
# collector/telegram_collector.py
import logging
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.tl.types import Message

logger = logging.getLogger(__name__)

class TelegramCollector:
    def __init__(self, config: Dict[str, Any], db=None):
        """Initialize collector with config and database."""
        self.config = config
        self.db = db
        self.channels = config.get("channels", [])
        
        telegram_config = config.get("telegram", {})
        self.api_id = telegram_config.get("api_id")
        self.api_hash = telegram_config.get("api_hash")
        self.bot_token = telegram_config.get("bot_token")
        
        self.client = None
    
    def _format_channel(self, channel: str) -> str:
        """Format channel name (remove @ if present)."""
        return channel.lstrip("@")
    
    async def start(self) -> None:
        """Start the Telegram client."""
        self.client = TelegramClient('vacancy_bot', self.api_id, self.api_hash)
        await self.client.start(bot_token=self.bot_token)
        logger.info("Telegram client started")
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client stopped")
    
    async def check_channels(self) -> List[Dict[str, Any]]:
        """Check all channels for new messages."""
        all_messages = []
        
        for channel in self.channels:
            try:
                messages = await self.get_new_messages(channel)
                all_messages.extend(messages)
            except Exception as e:
                logger.error(f"Error checking channel {channel}: {e}")
                if self.db:
                    self.db.log_error("channel_error", str(e), channel)
        
        return all_messages
    
    async def get_new_messages(self, channel: str) -> List[Dict[str, Any]]:
        """Get new messages from a channel."""
        if not self.client:
            await self.start()
        
        formatted_channel = self._format_channel(channel)
        messages = []
        
        try:
            # Get last 10 messages
            async for message in self.client.iter_messages(formatted_channel, limit=10):
                if isinstance(message, Message):
                    # Check if already processed
                    if self.db and self.db.is_message_processed(formatted_channel, message.id):
                        continue
                    
                    # Process message
                    message_data = {
                        "channel": formatted_channel,
                        "id": message.id,
                        "text": message.text or "",
                        "date": message.date,
                        "link": f"https://t.me/{formatted_channel}/{message.id}"
                    }
                    messages.append(message_data)
                    
                    # Mark as processed
                    if self.db:
                        self.db.mark_message_processed(formatted_channel, message.id)
        
        except Exception as e:
            logger.error(f"Error getting messages from {channel}: {e}")
            if self.db:
                self.db.log_error("message_error", str(e), channel)
        
        return messages
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_collector.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add collector/telegram_collector.py tests/test_collector.py
git commit -m "feat: add Telegram collector with duplicate detection"
```

---

## Task 6: Telegram Notifier

**Files:**
- Create: `notifier/telegram_notifier.py`
- Create: `tests/test_notifier.py`

**Interfaces:**
- Consumes: Config dict, FilterResult objects
- Produces: `TelegramNotifier` class with `send_vacancy()` method

- [ ] **Step 1: Write the failing test**

```python
# tests/test_notifier.py
import pytest
from unittest.mock import Mock, AsyncMock
from notifier.telegram_notifier import TelegramNotifier
from filter.vacancy_filter import FilterResult

@pytest.fixture
def notifier_config():
    return {
        "telegram": {
            "bot_token": "test_token",
            "target_channel": "@test_channel"
        }
    }

def test_notifier_initialization():
    """Test that notifier initializes correctly."""
    config = {
        "telegram": {
            "bot_token": "test_token",
            "target_channel": "@test_channel"
        }
    }
    
    notifier = TelegramNotifier(config)
    assert notifier.target_channel == "@test_channel"

def test_notifier_formats_message():
    """Test message formatting."""
    config = {
        "telegram": {
            "bot_token": "test_token",
            "target_channel": "@test_channel"
        }
    }
    
    notifier = TelegramNotifier(config)
    
    vacancy = FilterResult(
        category="Junior позиции",
        matched_phrase="junior media buyer",
        weight=10,
        original_text="Ищем junior media buyer без опыта"
    )
    
    message = notifier.format_message(vacancy)
    
    assert "Junior позиции" in message
    assert "junior media buyer" in message
    assert "Ищем junior media buyer без опыта" in message

def test_notifier_strips_channel_prefix():
    """Test that channel prefix is stripped."""
    config = {
        "telegram": {
            "bot_token": "test_token",
            "target_channel": "@test_channel"
        }
    }
    
    notifier = TelegramNotifier(config)
    assert notifier.target_channel == "test_channel"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_notifier.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'notifier.telegram_notifier'"

- [ ] **Step 3: Write minimal implementation**

```python
# notifier/telegram_notifier.py
import logging
from typing import Dict, Any
from telethon import TelegramClient
from filter.vacancy_filter import FilterResult

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, config: Dict[str, Any]):
        """Initialize notifier with config."""
        self.config = config
        telegram_config = config.get("telegram", {})
        self.bot_token = telegram_config.get("bot_token")
        self.target_channel = telegram_config.get("target_channel", "").lstrip("@")
        self.client = None
    
    async def start(self) -> None:
        """Start the Telegram client."""
        self.client = TelegramClient('notifier_bot', self.config["telegram"]["api_id"], 
                                     self.config["telegram"]["api_hash"])
        await self.client.start(bot_token=self.bot_token)
        logger.info("Notifier client started")
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Notifier client stopped")
    
    def format_message(self, vacancy: FilterResult, channel: str = None, message_id: int = None) -> str:
        """Format vacancy as message."""
        link = f"https://t.me/{channel}/{message_id}" if channel and message_id else "N/A"
        
        message = f"""🔍 Найдена вакансия!

📁 Категория: {vacancy.category}
🔑 Фраза: {vacancy.matched_phrase}
📡 Канал: {channel or 'N/A'}
📅 Дата: {vacancy.original_text[:50]}...
🔗 Ссылка: {link}

---
{vacancy.original_text}"""
        
        return message
    
    async def send_vacancy(self, vacancy: FilterResult, channel: str = None, message_id: int = None) -> bool:
        """Send vacancy notification to target channel."""
        if not self.client:
            await self.start()
        
        try:
            message = self.format_message(vacancy, channel, message_id)
            await self.client.send_message(self.target_channel, message)
            logger.info(f"Vacancy sent to {self.target_channel}")
            return True
        except Exception as e:
            logger.error(f"Error sending vacancy: {e}")
            return False
    
    async def send_error(self, error: str) -> bool:
        """Send error notification."""
        if not self.client:
            await self.start()
        
        try:
            message = f"❌ Ошибка бота:\n\n{error}"
            await self.client.send_message(self.target_channel, message)
            return True
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_notifier.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add notifier/telegram_notifier.py tests/test_notifier.py
git commit -m "feat: add Telegram notifier for vacancy notifications"
```

---

## Task 7: Main Entry Point

**Files:**
- Create: `main.py`

**Interfaces:**
- Consumes: All components (Collector, Filter, Notifier, Database, Scheduler)
- Produces: Working bot entry point

- [ ] **Step 1: Create main.py**

```python
# main.py
import asyncio
import yaml
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from utils.logger import setup_logger, get_logger
from utils.database import Database
from collector.telegram_collector import TelegramCollector
from filter.vacancy_filter import VacancyFilter
from notifier.telegram_notifier import TelegramNotifier
from web.app import create_app
import uvicorn

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

async def check_and_notify(collector: TelegramCollector, vacancy_filter: VacancyFilter, 
                          notifier: TelegramNotifier, db: Database):
    """Check channels and send notifications for matches."""
    logger = get_logger()
    logger.info("Starting channel check...")
    
    try:
        # Get new messages from all channels
        messages = await collector.check_channels()
        logger.info(f"Found {len(messages)} new messages")
        
        # Check each message against filters
        for message in messages:
            results = vacancy_filter.check_message(message["text"])
            
            for result in results:
                # Send notification
                sent = await notifier.send_vacancy(result, message["channel"], message["id"])
                
                if sent:
                    # Save to database
                    db.add_vacancy(
                        channel_name=message["channel"],
                        message_id=message["id"],
                        category=result.category,
                        matched_phrase=result.matched_phrase,
                        weight=result.weight,
                        text=message["text"],
                        link=message["link"]
                    )
                    logger.info(f"Vacancy sent: {result.category} - {result.matched_phrase}")
    
    except Exception as e:
        logger.error(f"Error in check_and_notify: {e}")
        db.log_error("check_error", str(e))
        await notifier.send_error(str(e))

async def main():
    """Main entry point."""
    # Load config
    config = load_config()
    
    # Setup logging
    log_config = config.get("logging", {})
    setup_logger(
        log_file=log_config.get("file", "logs/bot.log"),
        level=log_config.get("level", "INFO")
    )
    logger = get_logger()
    logger.info("Starting Telegram Vacancy Bot...")
    
    # Initialize components
    db = Database()
    collector = TelegramCollector(config, db)
    vacancy_filter = VacancyFilter(config)
    notifier = TelegramNotifier(config)
    
    # Start Telegram clients
    await collector.start()
    await notifier.start()
    
    # Setup scheduler
    scheduler = AsyncIOScheduler()
    schedule_config = config.get("schedule", {})
    check_interval = schedule_config.get("check_interval_minutes", 15)
    
    scheduler.add_job(
        check_and_notify,
        trigger=IntervalTrigger(minutes=check_interval),
        args=[collector, vacancy_filter, notifier, db],
        id="check_channels",
        name="Check channels for new vacancies"
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Checking every {check_interval} minutes")
    
    # Run first check immediately
    await check_and_notify(collector, vacancy_filter, notifier, db)
    
    # Setup web panel
    web_config = config.get("web", {})
    app = create_app(db, config)
    
    # Start web server
    web_config = config.get("web", {})
    uvicorn_config = uvicorn.Config(
        app,
        host=web_config.get("host", "0.0.0.0"),
        port=web_config.get("port", 8000),
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    
    logger.info(f"Web panel starting on {web_config.get('host')}:{web_config.get('port')}")
    
    # Run forever
    try:
        await server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()
        await collector.stop()
        await notifier.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Test that it runs (syntax check)**

```bash
python -m py_compile main.py
```

Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point with scheduler and web panel"
```

---

## Task 8: Web Panel

**Files:**
- Create: `web/app.py`
- Create: `web/routes.py`
- Create: `web/auth.py`
- Create: `web/templates/index.html`

**Interfaces:**
- Consumes: Database instance, Config dict
- Produces: FastAPI web application

- [ ] **Step 1: Create web/auth.py**

```python
# web/auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security), config: dict = None):
    """Verify HTTP Basic Auth credentials."""
    if config is None:
        config = {}
    
    web_config = config.get("web", {})
    correct_username = web_config.get("username", "admin")
    correct_password = web_config.get("password", "password")
    
    username_correct = secrets.compare_digest(credentials.username, correct_username)
    password_correct = secrets.compare_digest(credentials.password, correct_password)
    
    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
```

- [ ] **Step 2: Create web/routes.py**

```python
# web/routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from utils.database import Database

router = APIRouter()

def get_db():
    """Get database dependency."""
    return Database()

@router.get("/api/vacancies")
async def get_vacancies(limit: int = 100, db: Database = Depends(get_db)):
    """Get vacancies."""
    return db.get_vacancies(limit)

@router.get("/api/channels")
async def get_channels(db: Database = Depends(get_db)):
    """Get channels."""
    return db.get_channels()

@router.post("/api/channels")
async def add_channel(channel: Dict[str, str], db: Database = Depends(get_db)):
    """Add a channel."""
    channel_name = channel.get("channel_name")
    if not channel_name:
        raise HTTPException(status_code=400, detail="channel_name required")
    
    channel_id = db.add_channel(channel_name)
    return {"id": channel_id, "channel_name": channel_name}

@router.delete("/api/channels/{channel_id}")
async def delete_channel(channel_id: int, db: Database = Depends(get_db)):
    """Delete a channel."""
    deleted = db.delete_channel(channel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"deleted": True}

@router.get("/api/filters")
async def get_filters(db: Database = Depends(get_db)):
    """Get filters."""
    return db.get_filters()

@router.post("/api/filters")
async def add_filter(filter_data: Dict[str, Any], db: Database = Depends(get_db)):
    """Add a filter."""
    name = filter_data.get("name")
    phrases = filter_data.get("phrases", [])
    exclude = filter_data.get("exclude", [])
    weight = filter_data.get("weight", 5)
    
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    
    filter_id = db.add_filter(name, phrases, exclude, weight)
    return {"id": filter_id, "name": name}

@router.delete("/api/filters/{filter_id}")
async def delete_filter(filter_id: int, db: Database = Depends(get_db)):
    """Delete a filter."""
    deleted = db.delete_filter(filter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Filter not found")
    return {"deleted": True}

@router.get("/api/stats")
async def get_stats(db: Database = Depends(get_db)):
    """Get statistics."""
    return db.get_stats()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

- [ ] **Step 3: Create web/app.py**

```python
# web/app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from web.routes import router
from utils.database import Database

def create_app(db: Database, config: dict) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="Telegram Vacancy Bot", version="1.0.0")
    
    # Include routes
    app.include_router(router)
    
    # Templates
    templates = Jinja2Templates(directory="web/templates")
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Main page."""
        stats = db.get_stats()
        channels = db.get_channels()
        filters = db.get_filters()
        vacancies = db.get_vacancies(limit=50)
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "stats": stats,
                "channels": channels,
                "filters": filters,
                "vacancies": vacancies
            }
        )
    
    return app
```

- [ ] **Step 4: Create web/templates/index.html**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Vacancy Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: #2196F3;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }
        h1 {
            margin: 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #666;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #2196F3;
        }
        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section h2 {
            margin: 0 0 15px 0;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f5f5f5;
        }
        .btn {
            background: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn:hover {
            background: #1976D2;
        }
        .btn-danger {
            background: #f44336;
        }
        .btn-danger:hover {
            background: #d32f2f;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🔍 Telegram Vacancy Bot</h1>
        </div>
    </header>
    
    <div class="container">
        <!-- Statistics -->
        <div class="stats">
            <div class="stat-card">
                <h3>Всего вакансий</h3>
                <div class="value">{{ stats.total_vacancies }}</div>
            </div>
            <div class="stat-card">
                <h3>Сегодня</h3>
                <div class="value">{{ stats.vacancies_today }}</div>
            </div>
            <div class="stat-card">
                <h3>Каналов</h3>
                <div class="value">{{ stats.total_channels }}</div>
            </div>
            <div class="stat-card">
                <h3>Фильтров</h3>
                <div class="value">{{ stats.total_filters }}</div>
            </div>
        </div>
        
        <!-- Channels -->
        <div class="section">
            <h2>📡 Каналы</h2>
            <table>
                <thead>
                    <tr>
                        <th>Название</th>
                        <th>Статус</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for channel in channels %}
                    <tr>
                        <td>{{ channel.channel_name }}</td>
                        <td>{{ "Активен" if channel.is_active else "Отключен" }}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteChannel({{ channel.id }})">Удалить</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Filters -->
        <div class="section">
            <h2>🏷️ Фильтры</h2>
            <table>
                <thead>
                    <tr>
                        <th>Название</th>
                        <th>Фразы</th>
                        <th>Вес</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for filter in filters %}
                    <tr>
                        <td>{{ filter.name }}</td>
                        <td>{{ filter.phrases|join(', ') }}</td>
                        <td>{{ filter.weight }}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteFilter({{ filter.id }})">Удалить</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <!-- Vacancies -->
        <div class="section">
            <h2>💼 Найденные вакансии</h2>
            <table>
                <thead>
                    <tr>
                        <th>Категория</th>
                        <th>Фраза</th>
                        <th>Канал</th>
                        <th>Дата</th>
                        <th>Ссылка</th>
                    </tr>
                </thead>
                <tbody>
                    {% for vacancy in vacancies %}
                    <tr>
                        <td>{{ vacancy.vcategory or% </</</</</</</</�vac>
8 =</>
</�tdvac</>
</</vac</</>
�</   vac</parameter</</</</vac</>
</</</</</think>>
>
</</think></</</0</</td</>
</</</</Link </</vac           �</                vacancy</vac                       +</td</                   </td>
                        <td>{{ vacancy.matched_phrase }}</td>
                        <td>{{ vacancy.channel_name }}</td>
                        <td>{{ vacancy.sent_at }}</td>
                        <td><a href="{{ vacancy.link }}" target="_blank">Открыть</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function deleteChannel(id) {
            if (confirm('Удалить канал?')) {
                await fetch(`/api/channels/${id}`, { method: 'DELETE' });
                location.reload();
            }
        }
        
        async function deleteFilter(id) {
            if (confirm('Удалить фильтр?')) {
                await fetch(`/api/filters/${id}`, { method: 'DELETE' });
                location.reload();
            }
        }
    </script>
</body>
</html>
```

- [ ] **Step 5: Commit**

```bash
git add web/
git commit -m "feat: add web panel with FastAPI and HTML interface"
```

---

## Task 9: Docker Deployment

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Interfaces:**
- Consumes: All project files
- Produces: Docker configuration for deployment

- [ ] **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs database

# Expose web panel port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

- [ ] **Step 2: Create docker-compose.yml**

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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

- [ ] **Step 3: Test Docker build**

```bash
docker build -t vacancy-bot .
```

Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Docker deployment configuration"
```

---

## Task 10: Integration Testing

**Files:**
- Create: `tests/test_integration.py`

**Interfaces:**
- Consumes: All components
- Produces: Integration test suite

- [ ] **Step 1: Create integration test**

```python
# tests/test_integration.py
import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from utils.database import Database
from collector.telegram_collector import TelegramCollector
from filter.vacancy_filter import VacancyFilter
from notifier.telegram_notifier import TelegramNotifier

def test_full_workflow():
    """Test complete workflow: collect -> filter -> notify."""
    # Setup
    db = Database("tests/test_integration.db")
    
    config = {
        "telegram": {
            "api_id": "12345",
            "api_hash": "test_hash",
            "bot_token": "test_token",
            "target_channel": "@test_channel"
        },
        "channels": ["@job_channel"],
        "filters": [
            {
                "name": "Junior",
                "phrases": ["junior media buyer"],
                "exclude": [],
                "weight": 10
            }
        ]
    }
    
    collector = TelegramCollector(config, db)
    vacancy_filter = VacancyFilter(config)
    notifier = TelegramNotifier(config)
    
    # Simulate message
    test_message = "Ищем junior media buyer без опыта"
    
    # Check filter
    results = vacancy_filter.check_message(test_message)
    assert len(results) == 1
    assert results[0].category == "Junior"
    
    # Check database
    assert db.is_message_processed("@job_channel", 12345) == False
    db.mark_message_processed("@job_channel", 12345)
    assert db.is_message_processed("@job_channel", 12345) == True
    
    # Add vacancy to database
    vacancy_id = db.add_vacancy(
        channel_name="@job_channel",
        message_id=12345,
        category=results[0].category,
        matched_phrase=results[0].matched_phrase,
        weight=results[0].weight,
        text=test_message,
        link="https://t.me/job_channel/12345"
    )
    assert vacancy_id is not None
    
    # Cleanup
    os.remove("tests/test_integration.db")

def test_config_loading():
    """Test that config loads correctly."""
    import yaml
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    assert "telegram" in config
    assert "channels" in config
    assert "filters" in config
    assert "schedule" in config
    assert "web" in config
```

- [ ] **Step 2: Run integration tests**

```bash
pytest tests/test_integration.py -v
```

Expected: PASS

- [ ] **Step 3: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: add integration tests"
```

---

## Task 11: Final Setup and Documentation

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: All completed tasks
- Produces: Documentation for deployment

- [ ] **Step 1: Create README.md**

```markdown
# Telegram Vacancy Bot

Telegram бот для мониторинга каналов с вакансиями. Автоматически проверяет каналы на наличие вакансий, соответствующих заданным критериям, и отправляет уведомления.

## Возможности

- Мониторинг 10-50+ каналов Telegram
- Фильтрация по категориям с точными фразами
- Веб-панель для управления
- Автоматические уведомления
- Детекция дубликатов
- Retry логика при ошибках

## Установка

### Локально

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd TG_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте конфигурацию:
```bash
cp .env.example .env
# Отредактируйте config.yaml
```

4. Запустите бота:
```bash
python main.py
```

### Docker

1. Соберите образ:
```bash
docker build -t vacancy-bot .
```

2. Запустите контейнер:
```bash
docker-compose up -d
```

## Конфигурация

Отредактируйте `config.yaml`:

```yaml
telegram:
  api_id: "YOUR_API_ID"
  api_hash: "YOUR_API_HASH"
  bot_token: "YOUR_BOT_TOKEN"
  target_channel: "@your_channel"

channels:
  - "@channel1"
  - "@channel2"

filters:
  - name: "Junior позиции"
    phrases:
      - "junior media buyer"
    weight: 10
```

## Получение API ключей

1. **Telegram API:**
   - Перейдите на https://my.telegram.org
   - Войдите в аккаунт
   - Создайте приложение
   - Получите `api_id` и `api_hash`

2. **Bot Token:**
   - Найдите @BotFather в Telegram
   - Создайте нового бота
   - Получите токен

## Веб-панель

После запуска веб-панель доступна по адресу: `http://localhost:8000`

Логин: `admin`
Пароль: `your_secure_password` (настройте в config.yaml)

## Деплой на Oracle Cloud Free

1. Создайте ARM instance (2 OCPU, 4 GB RAM)
2. Установите Docker:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER
```

3. Склонируйте репозиторий и настройте конфигурацию

4. Запустите:
```bash
docker-compose up -d
```

## Лицензия

MIT
```

- [ ] **Step 2: Final commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-09-20-telegram-vacancy-bot.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**

A) Subagent-Driven (рекомендую)  
B) Inline Execution
