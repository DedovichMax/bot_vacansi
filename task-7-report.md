# Task 7: Main Entry Point - Report

## What Was Implemented

Created the main entry point (`main.py`) that orchestrates all components:
- **`load_config()`** — loads YAML configuration from file
- **`check_and_notify()`** — core orchestration: collects messages from channels, applies filters, sends notifications, saves vacancies to DB
- **`main()`** — async entry point that initializes all components, starts APScheduler for periodic checks, and runs FastAPI web server

### Supporting Files Created

| File | Purpose |
|------|---------|
| `main.py` | Entry point with load_config, check_and_notify, main functions |
| `tests/test_main.py` | 10 unit tests covering config loading and orchestration logic |
| `web/app.py` | Minimal FastAPI app stub with health check endpoint (will be expanded in Task 8) |
| `web/routes.py` | Minimal APIRouter stub (will be expanded in Task 8) |
| `conftest.py` | pytest configuration for asyncio marker registration |
| `pyproject.toml` | pytest config with `asyncio_mode = "auto"` |

## TDD Evidence

### RED Phase
```
ERROR collecting tests/test_main.py
ModuleNotFoundError: No module named 'main'
```
Tests written first, correctly failed because `main.py` did not exist.

### GREEN Phase
```
tests/test_main.py::test_load_config_reads_yaml PASSED
tests/test_main.py::test_load_config_missing_file PASSED
tests/test_main.py::test_load_config_invalid_yaml PASSED
tests/test_main.py::test_check_and_notify_filters_and_sends PASSED
tests/test_main.py::test_check_and_notify_no_messages PASSED
tests/test_main.py::test_check_and_notify_no_filter_matches PASSED
tests/test_main.py::test_check_and_notify_sends_failure_logged PASSED
tests/test_main.py::test_check_and_notify_collector_error PASSED
tests/test_main.py::test_check_and_notify_multiple_matches PASSED
tests/test_main.py::test_load_config_preserves_all_sections PASSED

10 passed in 1.65s
```

### Regression Check
```
tests/ - 29 passed in 1.75s (0 failures)
```

## Tests Covered

1. **Config Loading**
   - `test_load_config_reads_yaml` — reads valid YAML config
   - `test_load_config_missing_file` — raises FileNotFoundError for missing file
   - `test_load_config_invalid_yaml` — raises YAMLError for invalid syntax
   - `test_load_config_preserves_all_sections` — preserves all config sections

2. **Orchestration (check_and_notify)**
   - `test_check_and_notify_filters_and_sends` — full flow: collect → filter → send → save
   - `test_check_and_notify_no_messages` — empty messages = no actions
   - `test_check_and_notify_no_filter_matches` — no filter matches = no notifications
   - `test_check_and_notify_sends_failure_logged` — send failure = vacancy not saved to DB
   - `test_check_and_notify_collector_error` — collector error = logged + error notification sent
   - `test_check_and_notify_multiple_matches` — multiple matches per message = multiple sends

## Files Changed

- **Created:** `main.py`, `tests/test_main.py`, `web/app.py`, `web/routes.py`, `conftest.py`, `pyproject.toml`

## Commit

```
e69201f feat: add main entry point with APScheduler orchestration (Task 7)
```

## Concerns / Notes

1. **Web stubs:** `web/app.py` and `web/routes.py` are minimal stubs. Task 8 will replace them with full implementations including routes, auth, and HTML templates.

2. **Dependencies:** Required `pytest-asyncio` to be installed for async test support. Added `pyproject.toml` with `asyncio_mode = "auto"` to enable automatic async test detection.

3. **Config path:** `main()` hardcodes `config.yaml` as default path. Could be made configurable via env var in future.
