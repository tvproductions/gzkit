# CHORE: CLI Contract Governance (Drift & Evolution)

**Version:** 1.0.0
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

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz cli audit` | 0 |
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run gz cli audit > ops/chores/cli-contract-governance/proofs/cli-audit.txt
```

---

**End of CHORE: CLI Contract Governance**
