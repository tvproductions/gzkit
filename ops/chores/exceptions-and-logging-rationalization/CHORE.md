# CHORE: Exceptions & Logging Rationalization

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `exceptions-and-logging-rationalization`

---

## Overview

Rationalize exceptions and logging. Replace bare `except:` with specific exception types. Replace `print()` with structured logging where appropriate.

## Policy and Guardrails

- **Lane:** Lite — internal code quality, no external contract changes
- Use `logging` module for operational output
- Catch specific exceptions; translate to `core.errors` types
- No bare `except:` or `except Exception:` outside CLI boundary

## Workflow

### 1. Baseline

```bash
uvx ruff check src/gzkit --select E722 --output-format text
```

### 2. Plan

Prioritize: bare except > print() > logging inconsistencies.

### 3. Implement

Replace bare excepts with specific types. Add structured logging.

### 4. Validate

```bash
uvx ruff check src/gzkit --select E722 --output-format text
uv run -m unittest -q
```

## Checklist

- [ ] No E722 violations (bare except)
- [ ] Logging replaces operational print() calls
- [ ] Tests pass

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uvx ruff check src/gzkit --select E722` | 0 |

## Evidence Commands

```bash
uvx ruff check src/gzkit --select E722 --output-format text > ops/chores/exceptions-and-logging-rationalization/proofs/e722-report.txt
```

---

**End of CHORE: Exceptions & Logging Rationalization**
