# Task 5: Testing - Refactor Database Tests to Use tmp_path

## Task Description

Refactor test_database.py to use pytest's tmp_path fixture instead of manual file creation/deletion.

## Files to Modify

- Modify: `tests/test_database.py`

## Steps

1. Update test_database.py to use tmp_path fixture
2. Run database tests
3. Commit

## Expected Output

- All database tests use tmp_path fixture
- Tests pass without manual file cleanup
- No testDatabase.db files left behind

## Constraints

- Keep all existing test logic
- Only change how database paths are created
- Use tmp_path / "test.db" pattern
