# Task 6 Report: Refactor Web Tests to Use tmp_path

## What Was Implemented

Refactored `tests/test_web.py` to use pytest's `tmp_path` fixture instead of manual file creation/deletion.

### Changes Made

1. **`test_db` fixture**: Now uses `tmp_path / "test.db"` instead of hardcoded `tests/test_web.db` with manual `os.remove()` cleanup.

2. **`test_health_endpoint`**: Now accepts `tmp_path` parameter and creates database in temp directory instead of `tests/test_health.db`.

3. **`test_create_app_returns_fastapi`**: Now accepts `tmp_path` parameter and creates database in temp directory instead of `tests/test_create_app.db`.

4. **Removed `import os`**: No longer needed since we're not manually managing file paths.

### Key Improvements

- **No leftover files**: pytest automatically cleans up `tmp_path` after tests complete
- **Parallel-safe**: Each test gets its own isolated temporary directory
- **Simpler code**: Removed try/finally blocks with manual file deletion
- **No hardcoded paths**: Database paths are now dynamic and unique per test

## Test Results

All 19 tests passed:
- test_health_endpoint
- test_auth_rejects_wrong_credentials
- test_auth_accepts_correct_credentials
- test_auth_api_endpoints_require_auth
- test_get_channels_empty
- test_add_channel
- test_add_channel_missing_name
- test_delete_channel
- test_delete_channel_not_found
- test_get_filters_empty
- test_add_filter
- test_add_filter_missing_name
- test_delete_filter
- test_delete_filter_not_found
- test_get_vacancies_empty
- test_get_vacancies_after_add
- test_get_stats
- test_index_page
- test_create_app_returns_fastapi

## Files Changed

- `tests/test_web.py`: Refactored 3 functions/fixtures to use `tmp_path`

## Commit

- SHA: `a28957b`
- Message: `test: refactor test_web.py to use pytest tmp_path fixture`

## Self-Review Findings

- ✅ All existing test logic preserved
- ✅ Only database path creation changed
- ✅ `tmp_path / "test.db"` pattern used as specified
- ✅ FastAPI TestClient usage maintained
- ✅ No testDatabase.db files left behind
- ✅ Code is cleaner and more maintainable
