# TMCloud Code Quality Guide

This guide explains how to maintain code quality in the TMCloud project using the configured tools.

## Available Tools

The project uses the following code quality tools (defined in `requirements.txt`):

- **ruff** (≥0.12.0): Modern Python linter and formatter
- **black** (≥25.1.0): Code formatter
- **isort** (≥6.0.0): Import sorting
- **pytest** (≥8.4.0): Testing framework
- **pytest-cov** (≥6.2.0): Coverage reporting
- **pytest-timeout** (≥2.4.0): Test timeout handling

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Quality Checks
```bash
# Using the provided script
chmod +x run_quality_checks.sh
./run_quality_checks.sh

# Or run individual tools
python3 -m ruff check .
python3 -m black --check --diff .
python3 -m isort --check-only --diff .
python3 -m pytest -v
```

## Individual Tool Usage

### 1. Ruff (Linter)

Ruff is a fast Python linter that replaces flake8, isort, and other tools.

```bash
# Check for issues
python3 -m ruff check .

# Fix auto-fixable issues
python3 -m ruff check --fix .

# Check specific files
python3 -m ruff check app_dynamic_join_claude_optimized.py

# Show available rules
python3 -m ruff linter
```

### 2. Black (Formatter)

Black is an opinionated code formatter.

```bash
# Check formatting (no changes)
python3 -m black --check .

# Show what would be changed
python3 -m black --check --diff .

# Format files
python3 -m black .

# Format specific files
python3 -m black app_dynamic_join_claude_optimized.py
```

### 3. isort (Import Sorting)

isort sorts and organizes imports.

```bash
# Check import sorting
python3 -m isort --check-only .

# Show what would be changed
python3 -m isort --check-only --diff .

# Sort imports
python3 -m isort .

# Sort specific files
python3 -m isort app_dynamic_join_claude_optimized.py
```

### 4. pytest (Testing)

pytest runs tests and generates coverage reports.

```bash
# Run all tests
python3 -m pytest

# Run with verbose output
python3 -m pytest -v

# Run with coverage
python3 -m pytest --cov=. --cov-report=html

# Run specific test file
python3 -m pytest tests/test_search.py

# Run tests with timeout
python3 -m pytest --timeout=60
```

## Configuration

The project uses `pyproject.toml` for tool configuration:

### Ruff Configuration
- Line length: 88 characters
- Target Python version: 3.12
- Excludes: temporary files, data directories, images
- Selected rules: E, W, F, I, N, UP, B, C4, PIE, SIM

### Black Configuration
- Line length: 88 characters
- Target Python version: 3.12
- Skip string normalization: true
- Excludes: same as ruff

### isort Configuration
- Profile: black (compatible with Black)
- Line length: 88 characters
- Multi-line output: 3 (vertical hanging indent)

### pytest Configuration
- Test paths: tests/
- Timeout: 300 seconds
- Markers: slow, integration, unit
- Coverage source: current directory

## Pre-commit Integration

To run these tools automatically before commits, you can set up pre-commit hooks:

### 1. Install pre-commit
```bash
pip install pre-commit
```

### 2. Create .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

### 3. Install hooks
```bash
pre-commit install
```

## Common Issues and Solutions

### 1. Line Length Violations
**Problem**: Lines longer than 88 characters
**Solution**: Break long lines, use parentheses for continuations

```python
# Bad
very_long_function_call_with_many_parameters(param1, param2, param3, param4, param5)

# Good
very_long_function_call_with_many_parameters(
    param1, param2, param3, param4, param5
)
```

### 2. Import Sorting Issues
**Problem**: Imports not in the correct order
**Solution**: Use isort to fix automatically

```python
# Bad
from flask import Flask
import os
from typing import List

# Good
import os
from typing import List

from flask import Flask
```

### 3. Linting Errors
**Problem**: Various code quality issues
**Solution**: Use ruff to identify and fix issues

```bash
# See all issues
python3 -m ruff check .

# Fix auto-fixable issues
python3 -m ruff check --fix .
```

## TMCloud-Specific Guidelines

### 1. Japanese Comments
The project contains Japanese comments. These are allowed but should be consistent:

```python
# Good - Japanese docstring
def search_trademark(query: str) -> List[Dict]:
    """商標検索を実行する"""
    pass

# Also good - English docstring
def search_trademark(query: str) -> List[Dict]:
    """Execute trademark search"""
    pass
```

### 2. Database Paths
Use Path objects for file paths:

```python
# Good
from pathlib import Path
DB_PATH = Path("output.db")

# Less preferred
DB_PATH = "output.db"
```

### 3. Type Hints
Always use type hints for function parameters and return values:

```python
# Good
def query_db(self, query: str, args: tuple = ()) -> List[Dict]:
    pass

# Bad
def query_db(self, query, args=()):
    pass
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python3 -m ruff check .
      - run: python3 -m black --check .
      - run: python3 -m isort --check-only .
      - run: python3 -m pytest --cov=. --cov-report=xml
```

## Troubleshooting

### Tool Not Found
```bash
# Check if tool is installed
python3 -m ruff --version
python3 -m black --version
python3 -m isort --version
python3 -m pytest --version

# Install if missing
pip install ruff black isort pytest
```

### Permission Denied
```bash
# Make script executable
chmod +x run_quality_checks.sh
```

### Configuration Issues
```bash
# Check configuration
python3 -m ruff config
python3 -m black --check --config pyproject.toml .
```

## Best Practices

1. **Run tools before committing**: Use pre-commit hooks or run manually
2. **Fix issues immediately**: Don't accumulate technical debt
3. **Test after formatting**: Ensure formatting doesn't break functionality
4. **Use consistent configuration**: Keep tool configurations in sync
5. **Document exceptions**: If you need to ignore a rule, document why

## Performance Tips

1. **Ruff is fastest**: Use ruff for most linting tasks
2. **Run in parallel**: Tools can run simultaneously
3. **Use caching**: Tools cache results for faster subsequent runs
4. **Target specific files**: During development, check only changed files

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

**Last Updated**: 2025-07-16
**TMCloud Project**: Code Quality maintained with modern Python tools