# Task 6: Telegram Notifier — Report

## What was implemented

`TelegramNotifier` class that sends vacancy notifications to a target Telegram channel using the Bot API (Telethon). Key capabilities:

- **Initialization**: Extracts `bot_token` and `target_channel` from config, strips `@` prefix from channel name
- **Message formatting**: Formats `FilterResult` objects into readable Telegram messages with category, matched phrase, channel, and link
- **Async send**: `send_vacancy()` and `send_error()` methods that start a TelegramClient on demand and send messages to the target channel
- **Graceful lifecycle**: `start()` / `stop()` methods for client management

## Files created

| File | Description |
|------|-------------|
| `notifier/telegram_notifier.py` | TelegramNotifier class (88 LOC) |
| `tests/test_notifier.py` | 3 unit tests (53 LOC) |

## TDD Evidence

### RED Phase
```
FAILED tests/test_notifier.py::test_notifier_initialization
ModuleNotFoundError: No module named 'notifier.telegram_notifier'
```

### GREEN Phase
```
tests/test_notifier.py::test_notifier_initialization PASSED    [ 89%]
tests/test_notifier.py::test_notifier_formats_message PASSED   [ 94%]
tests/test_notifier.py::test_notifier_strips_channel_prefix PASSED [100%]

3 passed in 0.29s
```

### Full Suite Regression
```
19 passed in 0.39s (all tasks 1-6 tests green)
```

## Commit

- **SHA**: `2540a5a`
- **Message**: `feat: add Telegram notifier for vacancy notifications`

## Issues / Concerns

1. **Telethon dependency**: Tests require the `telethon` package. It was already installed in the project venv. Tests must be run via the venv Python (`.venv\Scripts\python.exe -m pytest`), not the system Python, to pick it up.

2. **Async methods untested in isolation**: `send_vacancy()` and `send_error()` are async methods that depend on a live Telegram client. The unit tests only cover synchronous behavior (initialization, message formatting, channel prefix stripping). The async send logic is tested implicitly through integration (Task 7's `check_and_notify`).

3. **Hard dependency on `api_id`/`api_hash` in `start()`**: The `start()` method reads `config["telegram"]["api_id"]` and `config["telegram"]["api_hash"]` directly. The test config fixture only provides `bot_token` and `target_channel`, so tests that don't call `start()` are fine, but this could raise `KeyError` in production if those keys are missing. Consider adding a guard or validation.
