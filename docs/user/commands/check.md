# gz check

Run full quality checks (lint, typecheck, test) in a single pass.

## Usage

```bash
gz check [OPTIONS]
```

## Description

Runs the complete quality assurance suite: linting with Ruff, static type checking with ty, and unit tests with unittest. Suitable for pre-commit verification and CI/CD pipelines.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed |
