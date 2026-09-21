# Task 3: Pre-commit Hooks

## Task Description

Add pre-commit hooks for ruff and black to automatically check code on commit.

## Files to Create

- Create: `.pre-commit-config.yaml`

## Steps

1. Create .pre-commit-config.yaml with ruff and pre-commit-hooks
2. Install pre-commit hooks
3. Run pre-commit on all files
4. Commit

## Expected Output

- .pre-commit-config.yaml created with:
  - ruff-pre-commit hooks (ruff, ruff-format)
  - pre-commit-hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files)
- Pre-commit hooks installed
- All files pass pre-commit checks

## Constraints

- Uses ruff-pre-commit from astral-sh
- Uses pre-commit-hooks v4.5.0
- Ruff args: [--fix]
