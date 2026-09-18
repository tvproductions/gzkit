# CHORE: CLI Contract Governance (Drift & Evolution)

**Lane:** Heavy
**Slug:** `cli-contract-governance`

---

## Overview

Maintain alignment between CLI doctrine and actual CLI behavior, help text, and exit codes. Detect drift between documented contracts and runtime behavior.

## Policy and Guardrails

- **Lane:** Heavy — external CLI contract changes require full gates
- Config-First; no undocumented contract changes
- Classify every finding as cosmetic, ergonomic or breaking before any change
- Cosmetic and ergonomic drift is repaired in place; a breaking change lands only in an operator-initiated run

## Workflow

### 1. Capture — observe

```bash
uv run gz cli audit
```

### 2. Analyze — observe

Diff against baselines. Classify findings:
- **Cosmetic:** Formatting, whitespace, ordering
- **Ergonomic:** Help text clarity
- **Breaking:** Exit code changes, removed or renamed flags, changed behavior

### 3. Report — propose

Document findings in proofs, each with its classification and the repair it needs.

### 4. Repair cosmetic and ergonomic drift — repair

Fix formatting, ordering and help-text clarity so runtime matches `.gzkit/rules/cli.md`. Never change a flag name, exit code or behavior in this step.

### 5. Breaking changes (operator-initiated) — operator-only-repair

Only in a run the operator started: land each breaking change the report names, updating manpages and runbooks in the same change (Heavy lane, all gates).

### 6. Validate — observe

```bash
uv run gz cli audit
uv run gz test
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan cli-contract-governance`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz cli audit > .gzkit/chores/cli-contract-governance/proofs/cli-audit.txt
```

---

**End of CHORE: CLI Contract Governance**
