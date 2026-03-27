# gz lint

Run code linting checks using Ruff and PyMarkdown.

## Usage

```bash
gz lint [OPTIONS]
```

## Description

Runs static linting analysis on Python code and documentation. Detects style violations, complexity issues, and documentation formatting errors. Use `--fix` to auto-correct fixable issues.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No lint violations found |
| 1 | Lint violations detected |
