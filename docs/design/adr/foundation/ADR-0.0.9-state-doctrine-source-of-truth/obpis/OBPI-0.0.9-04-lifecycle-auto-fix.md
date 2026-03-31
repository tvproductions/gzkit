---
id: OBPI-0.0.9-04-lifecycle-auto-fix
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 4
lane: lite
status: Draft
---

# OBPI-0.0.9-04: Lifecycle Auto-Fix

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #4 - "gz closeout, gz attest, and gz obpi reconcile auto-update frontmatter to match ledger-derived state at lifecycle moments"

**Status:** Draft

## Objective

`gz closeout`, `gz attest`, and `gz obpi reconcile` auto-update frontmatter to
match ledger-derived state at lifecycle moments. This prevents drift from
accumulating between lifecycle events by silently fixing frontmatter as a
side-effect of each command.

## Lane

**Lite** - Adds auto-fix behavior to existing commands. No new subcommands or external contract changes.

## Allowed Paths

- `src/gzkit/commands/closeout.py`
- `src/gzkit/commands/attest.py`
- `src/gzkit/commands/obpi.py`
- `tests/`

## Denied Paths

- `docs/` -- no documentation changes in this OBPI
- `features/` -- no BDD features in this OBPI
- `.gzkit/ledger.jsonl` -- never edit manually

## Requirements (FAIL-CLOSED)

1. Each lifecycle command MUST auto-fix frontmatter status before completing
2. Fix is silent (no user prompt, no confirmation step)
3. Fix uses ledger-derived state as the authoritative source
4. Tests prove auto-fix occurs for each lifecycle command

> STOP-on-BLOCKERS: if ledger status derivation is not available, this depends on OBPI-0.0.9-02.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] OBPI-0.0.9-02 (ledger-first status reads) for status derivation patterns

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/closeout.py` -- current closeout command
- [ ] `src/gzkit/commands/attest.py` -- current attest command
- [ ] `src/gzkit/commands/obpi.py` -- current obpi command
- [ ] `src/gzkit/ledger_semantics.py` -- ledger-first patterns
- [ ] `src/gzkit/sync.py` -- current frontmatter sync patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests exist for auto-fix in each lifecycle command
- [ ] `uv run -m unittest -q` passes

### Code Quality

- [ ] `uv run ruff check . --fix && uv run ruff format .`
- [ ] `uvx ty check . --exclude 'features/**'`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
# Verify: create frontmatter/ledger disagreement, run lifecycle command, confirm frontmatter fixed
```

## Acceptance Criteria

- [ ] REQ-0.0.9-04-01: `gz closeout` auto-fixes frontmatter status before completing
- [ ] REQ-0.0.9-04-02: `gz attest` auto-fixes frontmatter status before completing
- [ ] REQ-0.0.9-04-03: `gz obpi reconcile` auto-fixes frontmatter status
- [ ] REQ-0.0.9-04-04: Tests verify auto-fix for each lifecycle command

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, auto-fix tests exist for all three commands
- [ ] **Code Quality:** Ruff and ty pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
