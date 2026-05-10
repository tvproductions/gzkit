# CHORE: Run Full Quality Gates

**Version:** 2.0.0
**Lane:** Medium
**Slug:** `quality-check`

---

## Overview

Run the full gz quality gate set and capture deterministic evidence.

## Policy and Guardrails

- **Lane:** Medium — full `gz check` pipeline (lint + typecheck + tests + preflight) exceeds the 120s lite ceiling; medium (300s) is the canonical lane for expanded-check runs (registry.json `lanes.medium`)
- **Tool:** `gz check` runs lint, typecheck, test, and readiness gates in one pass

## Workflow

### 1. Run

```bash
uv run gz check
```

### 2. Validate

All gates must pass with exit code 0.

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz check` | 0 |

## Evidence Commands

```bash
uv run gz check > ops/chores/quality-check/proofs/gz-check.txt
```

---

**End of CHORE: Run Full Quality Gates**
