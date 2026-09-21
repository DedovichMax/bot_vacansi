# Task 2: Linters and Formatters - Configure Ruff and Black

## Task Description

Add ruff and black linter/formatter configuration to the project.

## Files to Modify

- Modify: `pyproject.toml`
- Modify: `requirements.txt`

## Steps

1. Add ruff and black config to pyproject.toml
2. Add dev dependencies to requirements.txt
3. Install dev dependencies
4. Run ruff check to verify configuration
5. Run black to format code
6. Run ruff check again
7. Commit

## Expected Output

- pyproject.toml has ruff and black configuration
- requirements.txt has dev dependencies
- Code is formatted with black
- Ruff linting passes

## Constraints

- Python 3.11+ required
- Line length: 100
- Target version: py311
- Ignore E501 (line too long - handled by black)
