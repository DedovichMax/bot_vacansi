# Design: Telegram Vacancy Bot Improvements

## Overview

Comprehensive improvements to the Telegram Vacancy Bot project covering security, code quality, CI/CD, testing, and documentation.

## 1. Security

### Problem
`config.yaml` contains real API keys and passwords tracked by git:
- `api_id: "35106112"`
- `api_hash: "fdb03ad4b4d9054472db4ea0705122d2"`
- `bot_token: "8621804672:AAGX-..."`
- `password: "A5244824a"` (web panel)

### Solution
1. Create `config.yaml.example` with placeholder values
2. Add `config.yaml` to `.gitignore`
3. Keep secrets only in `.env` (already exists)
4. Update README with setup instructions

### Files to modify
- `.gitignore` — add `config.yaml`
- `config.yaml.example` — create from current config with placeholders
- `README.md` — update setup section

## 2. Linters and Formatters

### Problem
No static analysis tools configured. Code style is inconsistent.

### Solution
Add `ruff` + `black` to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.black]
line-length = 100
target-version = ["py311"]
```

Add `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Files to modify
- `pyproject.toml` — add ruff/black config
- `.pre-commit-config.yaml` — create new file
- `requirements.txt` — add dev dependencies

## 3. CI/CD (GitHub Actions)

### Problem
No automated testing or linting on PR/push.

### Solution
Create `.github/workflows/test.yml`:
- Trigger: push to main, PR to main
- Jobs:
  1. **lint**: ruff check + ruff format --check
  2. **test**: pytest with coverage
  3. **type-check**: mypy

### Files to create
- `.github/workflows/test.yml`

## 4. Testing

### Problem
- No coverage reporting
- Tests create/delete files manually instead of using `tmp_path`
- No shared fixtures in `conftest.py`

### Solution
1. Add `pytest-cov` with 70% threshold
2. Refactor `test_database.py` to use `tmp_path`
3. Add shared fixtures to `conftest.py`

### Files to modify
- `pyproject.toml` — add pytest-cov config
- `requirements.txt` — add pytest-cov
- `tests/conftest.py` — add shared fixtures
- `tests/test_database.py` — use tmp_path
- `tests/test_web.py` — use tmp_path

## 5. Type Checking

### Problem
No static type checking. Some type hints missing.

### Solution
Add `mypy` to `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start lenient, tighten over time
```

### Files to modify
- `pyproject.toml` — add mypy config
- `requirements.txt` — add mypy (dev)

## 6. Documentation

### Problem
README references Telethon but project uses RSS.

### Solution
1. Update README: remove Telethon references
2. Add RSS-based architecture description
3. Add development section with linter/test instructions
4. Add `ctx7` CLI usage note

### Files to modify
- `README.md` — update architecture and development sections

## Implementation Order

1. Security (config.yaml.example, .gitignore)
2. Linters (pyproject.toml, .pre-commit-config.yaml)
3. Testing (pytest-cov, tmp_path, conftest.py)
4. CI/CD (.github/workflows/test.yml)
5. Type checking (mypy)
6. Documentation (README)

## Success Criteria

- [ ] config.yaml not tracked by git
- [ ] All tests pass with coverage >= 70%
- [ ] Ruff linting passes with 0 errors
- [ ] Black formatting consistent
- [ ] CI workflow runs on PR
- [ ] README accurate and complete
