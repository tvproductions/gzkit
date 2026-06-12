# CHORE: Control Surface — Rule Prose vs. Promoted Check Drift (Pass C)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `control-surface-rule-vs-check-drift`

---

## Overview

Audit-only pass. For every rule in `.gzkit/rules/**` that has a promoted mechanical check (any `gz validate --<scope>` flag), diff the rule's prose against what the check actually asserts. Flag cases where the prose says X and the check enforces a narrower or different X' — a rule that *looks* promoted but whose promotion is partial.

Background: `docs/governance/advisory-rules-audit.md` tracks *whether* a rule is promoted; it does not track whether the promoted check covers the full scope of the rule's prose. The scorecard is a promotion-status ledger, not a prose-vs-check parity ledger. This chore produces the parity ledger.

## Policy and Guardrails

- **Lane:** Lite — audit-only; zero edits to rules, validator, or source.
- **Scope:** every rule with a scorecard entry marked "Promoted" in `docs/governance/advisory-rules-audit.md` AND a corresponding `gz validate --<scope>` flag registered in the CLI parser.
- **Read-only on validator.** This chore does NOT modify `src/gzkit/commands/validate*` or any check implementation. It reads and reports.

## Workflow

### 1. Enumerate promoted rules

Cross-reference the scorecard with `uv run gz validate --help` output. Record every (rule_file, promoted_scope_flag) pair in `proofs/promoted-inventory.md`.

### 2. Prose extraction

For each promoted rule, extract the prose assertions (typically in a § "Mechanical check" or § "Invariants" section). Record normalized assertion list per rule in `proofs/prose-assertions.md`.

### 3. Check-behavior extraction

For each promoted scope flag, trace into the validator implementation and record what the check actually asserts (file enumeration, regex match, frontmatter field check, etc.) in `proofs/check-behaviors.md`. This is the only step that reads source — read only, do not edit.

### 4. Parity diff

For each promoted rule, one row in `proofs/parity-diff.md`:

- Rule file + § section
- Prose assertion count
- Check assertion count
- Gap: prose-only assertions (rule says, check doesn't enforce)
- Gap: check-only assertions (check enforces, rule doesn't document)
- Parity verdict: `parity` / `prose-wider` / `check-wider` / `divergent`

### 5. Summary

`proofs/summary.md`: counts by verdict; top 5 `prose-wider` cases (the high-value promotion targets); top 5 `divergent` cases (the highest-risk drift).

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md` | 0 |
| exitCodeEquals | `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` | 0 |

## Evidence Commands

```bash
uv run gz validate --help > .gzkit/chores/control-surface-rule-vs-check-drift/proofs/validate-help.txt 2>&1
uv run gz validate --advisory-scorecard > .gzkit/chores/control-surface-rule-vs-check-drift/proofs/advisory-scorecard.txt 2>&1
```

---
