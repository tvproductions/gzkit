# CHORE: Exceptions & Logging Rationalization

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

### 1. Baseline — observe

```bash
uvx ruff check src/gzkit --select E722 --output-format text
```

### 2. Plan — propose

Prioritize: bare except > print() > logging inconsistencies.

### 3. Implement — repair

Replace bare excepts with specific types. Add structured logging.

### 4. Validate — observe

```bash
uvx ruff check src/gzkit --select E722 --output-format text
uv run -m unittest -q
```

## Checklist

- [ ] No E722 violations (bare except)
- [ ] Logging replaces operational print() calls
- [ ] Tests pass

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan exceptions-and-logging-rationalization`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uvx ruff check src/gzkit --select E722 --output-format text > .gzkit/chores/exceptions-and-logging-rationalization/proofs/e722-report.txt
```

---

**End of CHORE: Exceptions & Logging Rationalization**
