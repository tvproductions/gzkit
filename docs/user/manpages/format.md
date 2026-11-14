# gz format

Auto-format Python code using Ruff.

## Usage

```bash
gz format [OPTIONS]
```

## Description

Applies automatic code formatting to all Python files using Ruff's formatter, then `gz lint --fix`. Enforces consistent style across the codebase including indentation, line length, and quote style. Dated evidence scripts are sealed records: `[tool.ruff.format] exclude` in `pyproject.toml` keeps the formatter off them, even when a file is named outright (`force-exclude`).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Formatting applied successfully |
| 1 | Formatting check failed |
