# Telegram Vacancy Bot Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve security, code quality, CI/CD, testing, and documentation for the Telegram Vacancy Bot.

**Architecture:** Security-first approach: move secrets to .env, add linters/formatters, CI/CD with GitHub Actions, improve test coverage and type checking.

**Tech Stack:** Python 3.11+, ruff, black, mypy, pytest-cov, GitHub Actions, pre-commit

## Global Constraints

- Python 3.11+ required
- All existing tests must pass (68 tests)
- No breaking changes to existing functionality
- config.yaml secrets must be removed from git tracking

---

## File Structure

| File | Action | Purpose |
|------|--------|---------|
| `.gitignore` | Modify | Add config.yaml |
| `config.yaml.example` | Create | Template without secrets |
| `pyproject.toml` | Modify | Add ruff, black, mypy, pytest-cov config |
| `.pre-commit-config.yaml` | Create | Pre-commit hooks |
| `.github/workflows/test.yml` | Create | CI/CD pipeline |
| `tests/conftest.py` | Modify | Add shared fixtures |
| `tests/test_database.py` | Modify | Use tmp_path fixture |
| `tests/test_web.py` | Modify | Use tmp_path fixture |
| `README.md` | Modify | Update documentation |

---

## Task 1: Security - Remove Secrets from Git

**Files:**
- Modify: `.gitignore`
- Create: `config.yaml.example`
- Modify: `README.md`

**Interfaces:**
- Consumes: existing `config.yaml` structure
- Produces: `.gitignore` updated, `config.yaml.example` created

- [ ] **Step 1: Add config.yaml to .gitignore**

```bash
# Add to .gitignore
echo "config.yaml" >> .gitignore
```

- [ ] **Step 2: Create config.yaml.example with placeholders**

```yaml
# Telegram settings
telegram:
  api_id: "YOUR_API_ID"
  api_hash: "YOUR_API_HASH"
  bot_token: "YOUR_BOT_TOKEN"
  target_channel: "@your_target_channel"

# Channels to monitor
channels:
  - "@channel1"
  - "@channel2"

# Filters
filters:
  - name: "Junior позиции"
    phrases:
      - "junior media buyer"
      - "младший медиабайер"
    exclude:
      - "senior junior"
    weight: 10

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
  password: "CHANGE_ME"

# Logging
logging:
  level: "INFO"
  file: "logs/bot.log"
```

- [ ] **Step 3: Verify .gitignore works**

Run: `git status --ignored -- config.yaml`
Expected: `config.yaml` should appear in ignored files

- [ ] **Step 4: Commit**

```bash
git add .gitignore config.yaml.example
git commit -m "security: move secrets to .env, add config.yaml.example"
```

---

## Task 2: Linters and Formatters - Configure Ruff and Black

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: existing Python 3.11+ codebase
- Produces: linter and formatter configuration

- [ ] **Step 1: Add ruff and black to pyproject.toml**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by black)

[tool.ruff.lint.isort]
known-first-party = ["collector", "filter", "notifier", "utils", "web"]

[tool.black]
line-length = 100
target-version = ["py311"]
```

- [ ] **Step 2: Add dev dependencies to requirements.txt**

Add to `requirements.txt`:
```
ruff>=0.1.0
black>=24.0.0
mypy>=1.0.0
pytest-cov>=4.0.0
pre-commit>=3.0.0
```

- [ ] **Step 3: Install dev dependencies**

Run: `pip install ruff black mypy pytest-cov pre-commit`
Expected: Installation successful

- [ ] **Step 4: Run ruff check to verify configuration**

Run: `ruff check .`
Expected: Some linting errors found (expected on first run)

- [ ] **Step 5: Run black to format code**

Run: `black .`
Expected: Files reformatted

- [ ] **Step 6: Run ruff check again**

Run: `ruff check .`
Expected: Fewer or no errors

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "chore: add ruff, black, mypy, pytest-cov configuration"
```

---

## Task 3: Pre-commit Hooks

**Files:**
- Create: `.pre-commit-config.yaml`

**Interfaces:**
- Consumes: ruff and black configuration from Task 2
- Produces: pre-commit hooks installed

- [ ] **Step 1: Create .pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

- [ ] **Step 2: Install pre-commit hooks**

Run: `pre-commit install`
Expected: Pre-commit hooks installed

- [ ] **Step 3: Run pre-commit on all files**

Run: `pre-commit run --all-files`
Expected: Hooks run, some files may be modified

- [ ] **Step 4: Commit modified files**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit hooks for ruff and black"
```

---

## Task 4: Testing - Add Pytest Coverage

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: existing pytest configuration
- Produces: coverage reporting enabled

- [ ] **Step 1: Add coverage config to pyproject.toml**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "--cov=collector --cov=filter --cov=notifier --cov=utils --cov=web --cov-report=term-missing --cov-fail-under=70"
```

- [ ] **Step 2: Add pytest-cov to requirements.txt**

Add to `requirements.txt`:
```
pytest-cov>=4.0.0
```

- [ ] **Step 3: Run tests with coverage**

Run: `pytest tests/ -v --tb=short`
Expected: All 68 tests pass, coverage report shown

- [ ] **Step 4: Verify coverage threshold**

Expected: Coverage >= 70% (or adjust threshold in pyproject.toml)

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "test: add pytest-cov with 70% coverage threshold"
```

---

## Task 5: Testing - Refactor Database Tests to Use tmp_path

**Files:**
- Modify: `tests/test_database.py`

**Interfaces:**
- Consumes: existing Database class
- Produces: tests using pytest tmp_path fixture

- [ ] **Step 1: Update test_database.py to use tmp_path**

Replace manual file creation/deletion with pytest's `tmp_path` fixture:

```python
# tests/test_database.py
import sqlite3
import pytest
from utils.database import Database


def test_database_initialization(tmp_path):
    """Test that database creates all tables on init."""
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))

    # Check tables exist
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "channels" in tables
    assert "filters" in tables
    assert "vacancies" in tables
    assert "processed_messages" in tables
    assert "error_log" in tables


def test_add_channel(tmp_path):
    """Test adding a channel to database."""
    db_path = tmp_path / "test_add_channel.db"
    db = Database(str(db_path))

    # Add channel
    channel_id = db.add_channel("@test_channel")
    assert channel_id is not None

    # Get channels
    channels = db.get_channels()
    assert len(channels) == 1
    assert channels[0]["channel_name"] == "@test_channel"
    assert channels[0]["is_active"] == True


def test_add_filter(tmp_path):
    """Test adding a filter to database."""
    db_path = tmp_path / "test_add_filter.db"
    db = Database(str(db_path))

    # Add filter
    filter_id = db.add_filter(
        name="Test Filter",
        phrases=["test phrase", "another phrase"],
        exclude=["exclude me"],
        weight=5,
    )
    assert filter_id is not None

    # Get filters
    filters = db.get_filters()
    assert len(filters) == 1
    assert filters[0]["name"] == "Test Filter"


def test_add_vacancy(tmp_path):
    """Test adding a vacancy to database."""
    db_path = tmp_path / "test_add_vacancy.db"
    db = Database(str(db_path))

    # Add vacancy
    vacancy_id = db.add_vacancy(
        channel_name="@test_channel",
        message_id=12345,
        category="Test Category",
        matched_phrase="test phrase",
        weight=5,
        text="Test vacancy text",
        link="https://t.me/test/12345",
    )
    assert vacancy_id is not None

    # Get vacancies
    vacancies = db.get_vacancies()
    assert len(vacancies) == 1
    assert vacancies[0]["channel_name"] == "@test_channel"


def test_is_message_processed(tmp_path):
    """Test duplicate detection."""
    db_path = tmp_path / "test_duplicate.db"
    db = Database(str(db_path))

    # Message not processed yet
    assert db.is_message_processed("@channel", 12345) == False

    # Mark as processed
    db.mark_message_processed("@channel", 12345)

    # Now it's processed
    assert db.is_message_processed("@channel", 12345) == True

    # Different message still not processed
    assert db.is_message_processed("@channel", 12346) == False
```

- [ ] **Step 2: Run database tests**

Run: `pytest tests/test_database.py -v`
Expected: All 5 tests pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_database.py
git commit -m "test: refactor database tests to use tmp_path fixture"
```

---

## Task 6: Testing - Refactor Web Tests to Use tmp_path

**Files:**
- Modify: `tests/test_web.py`

**Interfaces:**
- Consumes: existing Database and FastAPI app
- Produces: tests using pytest tmp_path fixture

- [ ] **Step 1: Update test_web.py to use tmp_path**

Add `tmp_path` parameter to tests that create database files:

```python
# In tests/test_web.py, update tests that create Database instances
# to use tmp_path fixture


def test_get_channels_empty(tmp_path):
    """Test getting channels from empty database."""
    db = Database(str(tmp_path / "test.db"))
    app = create_app(db, {"web": {"username": "admin", "password": "test"}})
    client = TestClient(app)
    response = client.get("/api/channels", auth=("admin", "test"))
    assert response.status_code == 200
    assert response.json() == []


def test_add_channel(tmp_path):
    """Test adding a channel."""
    db = Database(str(tmp_path / "test.db"))
    app = create_app(db, {"web": {"username": "admin", "password": "test"}})
    client = TestClient(app)
    response = client.post(
        "/api/channels", json={"channel_name": "@test_channel"}, auth=("admin", "test")
    )
    assert response.status_code == 200
    assert response.json()["channel_name"] == "@test_channel"


# Apply similar pattern to all tests that create Database instances
```

- [ ] **Step 2: Run web tests**

Run: `pytest tests/test_web.py -v`
Expected: All 16 tests pass

- [ ] **Step 3: Commit**

```bash
git add tests/test_web.py
git commit -m "test: refactor web tests to use tmp_path fixture"
```

---

## Task 7: CI/CD - GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/test.yml`

**Interfaces:**
- Consumes: ruff, black, mypy, pytest configuration
- Produces: automated CI pipeline

- [ ] **Step 1: Create .github/workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create test.yml workflow**

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff black
      - name: Run ruff check
        run: ruff check .
      - name: Run ruff format check
        run: ruff format --check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: pytest tests/ -v --tb=short --cov=collector --cov=filter --cov=notifier --cov=utils --cov=web --cov-report=term-missing --cov-fail-under=70

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mypy
      - name: Run mypy
        run: mypy --ignore-missing-imports collector/ filter/ notifier/ utils/ web/
```

- [ ] **Step 3: Verify workflow syntax**

Run: `yamllint .github/workflows/test.yml` (if available) or manual review
Expected: Valid YAML syntax

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/test.yml
git commit -m "ci: add GitHub Actions workflow for lint, test, type-check"
```

---

## Task 8: Type Checking - Configure Mypy

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: existing codebase with partial type hints
- Produces: mypy configuration

- [ ] **Step 1: Add mypy config to pyproject.toml**

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
```

- [ ] **Step 2: Add mypy to requirements.txt**

Add to `requirements.txt`:
```
mypy>=1.0.0
```

- [ ] **Step 3: Run mypy to check current state**

Run: `mypy --ignore-missing-imports collector/ filter/ notifier/ utils/ web/`
Expected: Some type errors found (expected on first run)

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "chore: add mypy configuration for type checking"
```

---

## Task 9: Documentation - Update README

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: all previous changes
- Produces: updated documentation

- [ ] **Step 1: Update README Architecture section**

Replace Telethon references with RSS-based architecture:

```markdown
## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+ |
| Telegram API | RSS (tg-channel-to-rss.vercel.app) + Bot API |
| База данных | SQLite |
| Веб-сервер | FastAPI 0.115.0 + Uvicorn 0.30.0 |
| Шаблонизация | Jinja2 3.1.4 |
| Планировщик | APScheduler 3.10.4 |
| Конфигурация | PyYAML 6.0.1 |
| Контейнеризация | Docker |
```

- [ ] **Step 2: Add Development section**

```markdown
## Разработка

### Установка зависимостей

```bash
# Основные зависимости
pip install -r requirements.txt

# Dev-зависимости (линтеры, форматтеры, тесты)
pip install ruff black mypy pytest-cov pre-commit
```

### Настройка pre-commit

```bash
pre-commit install
```

### Запуск линтеров

```bash
# Проверка стиля
ruff check .

# Форматирование
black .
```

### Запуск тестов

```bash
# Все тесты с coverage
pytest tests/ -v --cov=collector --cov=filter --cov=notifier --cov=utils --cov=web

# Конкретный модуль
pytest tests/test_filter.py -v
```

### Type checking

```bash
mypy --ignore-missing-imports collector/ filter/ notifier/ utils/ web/
```
```

- [ ] **Step 3: Update Setup section**

```markdown
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
cp config.yaml.example config.yaml
cp .env.example .env
```

Отредактируйте `config.yaml` и `.env` — впишите реальные API-ключи.

4. Запустите бота:

```bash
python main.py
```
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README with RSS architecture and development guide"
```

---

## Task 10: Final Verification

**Files:**
- None (verification only)

**Interfaces:**
- Consumes: all previous tasks
- Produces: verified working state

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v --tb=short`
Expected: All 68 tests pass

- [ ] **Step 2: Run ruff check**

Run: `ruff check .`
Expected: No errors

- [ ] **Step 3: Run black check**

Run: `black --check .`
Expected: All files formatted correctly

- [ ] **Step 4: Run mypy**

Run: `mypy --ignore-missing-imports collector/ filter/ notifier/ utils/ web/`
Expected: No critical errors

- [ ] **Step 5: Verify config.yaml not tracked**

Run: `git status --ignored -- config.yaml`
Expected: config.yaml is ignored

- [ ] **Step 6: Commit all changes**

```bash
git add .
git commit -m "chore: complete improvements - security, linters, CI/CD, tests, docs"
```

---

## Summary

| Task | Description | Status |
|------|-------------|--------|
| 1 | Security - Remove secrets from git | Pending |
| 2 | Linters - Configure ruff and black | Pending |
| 3 | Pre-commit hooks | Pending |
| 4 | Testing - Add pytest-cov | Pending |
| 5 | Testing - Refactor database tests | Pending |
| 6 | Testing - Refactor web tests | Pending |
| 7 | CI/CD - GitHub Actions | Pending |
| 8 | Type checking - Configure mypy | Pending |
| 9 | Documentation - Update README | Pending |
| 10 | Final verification | Pending |
