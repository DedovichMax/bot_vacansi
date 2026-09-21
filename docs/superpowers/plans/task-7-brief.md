# Task 7: CI/CD - GitHub Actions Workflow

## Task Description

Create GitHub Actions workflow for automated linting, testing, and type checking.

## Files to Create

- Create: `.github/workflows/test.yml`

## Steps

1. Create .github/workflows directory
2. Create test.yml workflow with lint, test, type-check jobs
3. Verify workflow syntax
4. Commit

## Expected Output

- .github/workflows/test.yml created with:
  - lint job: ruff check + ruff format --check
  - test job: pytest with coverage
  - type-check job: mypy
- Workflow triggers on push to main and PR to main

## Constraints

- Python 3.11
- Ubuntu latest
- Checkout v4, setup-python v5
