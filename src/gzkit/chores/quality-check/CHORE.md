# CHORE: Run Full Quality Gates

**Lane:** Heavy
**Timeout:** 900s
**Slug:** `quality-check`

---

## Overview

Run the full gz quality gate set and capture deterministic evidence.

## Policy and Guardrails

- **Lane:** Heavy — exercises the full sweep, `gz check --full`: every per-change step plus the whole unit tier, behave, the docs build, preflight and the guard-canary sweep. Plain `gz check` is the per-change gate and runs only the tests a change touches (GHI #1191), so this chore and CI are where the whole tier runs on a schedule
- **Timeout:** 900s — explicit per-chore `timeoutSeconds` on the registry entry; lane no longer carries a duration semantic (GHI #447). The full sweep measured 156s and, on one loaded run, 514s on a developer host on 2026-10-11 (a dated record, GHI #1191)
- **Tool:** `gz check --full` runs every registered quality step in one pass

## Workflow

### 1. Run — observe

```bash
uv run gz check --full
```

### 2. Validate — observe

All gates must pass with exit code 0.

### 3. Route failures — propose

For each failing gate, name what owns the repair: the chore whose subject it is (lint and idioms → `pythonic-refactoring`, complexity → `complexity-reduction-xenon`, module size → `module-sloc-cap-radon`, docstrings → `pep257-docstring-compliance`), or a direct fix when the failure is a defect with no chore. Never waive or suppress a gate to pass.

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan quality-check`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz check --full > .gzkit/chores/quality-check/proofs/gz-check.txt
```

---

**End of CHORE: Run Full Quality Gates**
