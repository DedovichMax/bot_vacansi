# Task 2: Logger Setup

**Files:**
- Create: `utils/logger.py`
- Create: `tests/test_logger.py`

**Interfaces:**
- Consumes: None
- Produces: `setup_logger()` function, `get_logger()` function

## Steps

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

    with open(log_file, "r") as f:
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
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
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
