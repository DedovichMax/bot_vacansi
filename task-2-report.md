# Task 2 Report: Logger Setup

## What I Implemented

- **`utils/logger.py`** — `setup_logger()` and `get_logger()` functions with rotating file handler
- **`tests/test_logger.py`** — 2 tests verifying file creation and log writing

## TDD Evidence

### RED (test fails before implementation)

```
FAILED tests/test_logger.py::test_setup_logger_creates_log_file - ModuleNotFoundError: No module named 'utils.logger'
FAILED tests/test_logger.py::test_logger_writes_to_file - ModuleNotFoundError: No module named 'utils.logger'
2 failed in 0.14s
```

### GREEN (tests pass after implementation)

```
tests/test_logger.py::test_setup_logger_creates_log_file PASSED
tests/test_logger.py::test_logger_writes_to_file PASSED
2 passed in 0.03s
```

## Files Changed

| File | Action |
|------|--------|
| `utils/logger.py` | Created |
| `tests/test_logger.py` | Created |

## Self-Review Findings

### Adaptation from task brief
The task brief provided exact test code, but on Windows the `RotatingFileHandler` locks the log file, causing `PermissionError` during cleanup. I made two minimal adaptations:

1. **`utils/logger.py`**: Added `_logger.handlers.clear()` in `setup_logger()` — makes it idempotent (safe to call multiple times without duplicating handlers). This is good practice regardless of OS.

2. **`tests/test_logger.py`**: Extracted `_cleanup_logger()` helper that properly closes all handlers before removing the log file. The test assertions and structure match the brief exactly — only cleanup logic was adapted for Windows compatibility.

### What's working correctly
- Logger creates log directory and file
- RotatingFileHandler configured with 10MB max size, 5 backups
- Console handler outputs to stderr
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- `get_logger()` auto-initializes if `setup_logger()` wasn't called
- Level defaults to INFO
