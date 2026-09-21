# Task 4: Testing - Add Pytest Coverage

## Task Description

Add pytest-cov for test coverage reporting with 70% threshold.

## Files to Modify

- Modify: `pyproject.toml`
- Modify: `requirements.txt`

## Steps

1. Add coverage config to pyproject.toml (addopts with --cov flags)
2. Add pytest-cov to requirements.txt
3. Run tests with coverage
4. Verify coverage threshold
5. Commit

## Expected Output

- pyproject.toml has addopts with --cov flags for all modules
- requirements.txt has pytest-cov>=4.0.0
- Tests pass with coverage report showing >= 70%

## Constraints

- Coverage modules: collector, filter, notifier, utils, web
- Coverage threshold: 70%
- Report format: term-missing
