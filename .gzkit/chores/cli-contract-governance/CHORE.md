# CHORE: CLI Contract Governance (Drift & Evolution)

**Lane:** Heavy
**Slug:** `cli-contract-governance`

---

## Overview

Maintain alignment between CLI doctrine and actual CLI behavior, help text, and exit codes. Detect drift between documented contracts and runtime behavior.

## Policy and Guardrails

- **Lane:** Heavy — external CLI contract changes require full gates
- Config-First; no undocumented contract changes
- Audit only; classify findings as cosmetic/ergonomic/breaking

## Workflow

### 1. Capture

```bash
uv run gz cli audit
```

### 2. Analyze

Diff against baselines. Classify findings:
- **Cosmetic:** Formatting, whitespace, ordering
- **Ergonomic:** Help text clarity, flag naming
- **Breaking:** Exit code changes, removed flags, changed behavior

### 3. Report

Document findings in proofs.

### 4. Validate

```bash
uv run gz cli audit
uv run -m unittest -q
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan cli-contract-governance`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz cli audit > .gzkit/chores/cli-contract-governance/proofs/cli-audit.txt
```

---

**End of CHORE: CLI Contract Governance**
