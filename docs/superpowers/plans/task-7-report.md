# Task 7: CI/CD - GitHub Actions Workflow

## Status: DONE

## What I Implemented

Created `.github/workflows/test.yml` with three jobs:

- **lint**: Runs `ruff check .` and `ruff format --check .`
- **test**: Runs `python -m pytest tests/ -v --tb=short`
- **type-check**: Runs `mypy .`

Workflow triggers on push to `main` and PR to `main`.

## Configuration

- Python version: 3.11
- Runner: ubuntu-latest
- Actions: checkout@v4, setup-python@v5

## Commit

- `4461824` - ci: add GitHub Actions workflow for lint, test, and type-check

## Self-Review

**Complete:** All requirements met - lint job (ruff check + ruff format), test job (pytest), type-check job (mypy), proper triggers, correct action versions.

**Quality:** Clean YAML, well-named steps, follows GitHub Actions best practices.

**Concerns:**
- mypy is not in `requirements.txt` - added as `pip install mypy` in the workflow
- This is fine for now but should be added to requirements.txt for consistency
