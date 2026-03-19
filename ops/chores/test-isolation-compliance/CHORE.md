# CHORE: Test Isolation Compliance (Temp DB + Temp Dir)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `test-isolation-compliance`

---

## Overview

Ensure all database/file-using tests are properly isolated using temporary directories and in-memory SQLite. No live or production databases in tests.

## Policy and Guardrails

- **Lane:** Lite — test infrastructure, no external contract changes
- Unit tests MUST use `tempfile` temp dirs or in-memory SQLite
- Never touch live/production databases from tests
- Prefer shared in-memory SQLite DB for speed and isolation

## Workflow

### 1. Scan

Identify tests that create files or databases without proper isolation.

### 2. Plan

Batch violations by module for systematic remediation.

### 3. Implement

Replace direct file/DB access with:
- `tempfile.TemporaryDirectory()` context managers
- In-memory SQLite via `sqlite3.connect(":memory:")`

### 4. Validate

```bash
uv run -m unittest -q
```

## Checklist

- [ ] No tests use persistent file paths
- [ ] No tests touch production databases
- [ ] All temp resources cleaned via context managers
- [ ] Tests pass

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run -m unittest -v > ops/chores/test-isolation-compliance/proofs/test-results.txt
```

---

**End of CHORE: Test Isolation Compliance**
