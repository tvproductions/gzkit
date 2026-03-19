# CHORE: Sync Manpage Docstrings (One-Liner Alignment)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `sync-manpage-docstrings`

---

## Overview

Ensure one-liner summaries in manpage IMPLEMENTATION TRACE match docstring first lines. Docstring is the source of truth; manpage summaries must track it.

## Policy and Guardrails

- **Lane:** Lite — internal alignment, no contract changes
- Docstring first line is source of truth
- One-liner shared between docstring and manpage trace
- Uses `gz cli audit` for comprehensive validation

## Workflow

### 1. Check

```bash
uv run gz cli audit
```

### 2. Fix

Update manpage one-liners to match docstring first lines.

### 3. Re-validate

```bash
uv run gz cli audit
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz cli audit` | 0 |

## Evidence Commands

```bash
uv run gz cli audit > ops/chores/sync-manpage-docstrings/proofs/cli-audit.txt
```

---

**End of CHORE: Sync Manpage Docstrings**
