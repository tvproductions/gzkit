# CHORE: Run Full Quality Gates

**Version:** 2.1.0
**Lane:** Heavy
**Timeout:** 300s
**Slug:** `quality-check`

---

## Overview

Run the full gz quality gate set and capture deterministic evidence.

## Policy and Guardrails

- **Lane:** Heavy — exercises the full `gz check` pipeline (lint + typecheck + tests + preflight) including behave when present; matches AGENTS.md § Gate Covenant heavy = all gates required
- **Timeout:** 300s — explicit per-chore `timeoutSeconds` on the registry entry; lane no longer carries a duration semantic (GHI #447)
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
