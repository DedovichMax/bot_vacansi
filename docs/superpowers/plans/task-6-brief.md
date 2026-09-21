# Task 6: Testing - Refactor Web Tests to Use tmp_path

## Task Description

Refactor test_web.py to use pytest's tmp_path fixture instead of manual file creation/deletion.

## Files to Modify

- Modify: `tests/test_web.py`

## Steps

1. Update test_web.py to use tmp_path fixture
2. Run web tests
3. Commit

## Expected Output

- All web tests use tmp_path fixture
- Tests pass without manual file cleanup
- No testDatabase.db files left behind

## Constraints

- Keep all existing test logic
- Only change how database paths are created
- Use tmp_path / "test.db" pattern
- Maintain FastAPI TestClient usage
