---
id: OBPI-0.0.9-04-lifecycle-auto-fix
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 4
lane: lite
status: attested_completed
---

# OBPI-0.0.9-04: Lifecycle Auto-Fix

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #4 - "gz closeout, gz attest, and gz obpi reconcile auto-update frontmatter to match ledger-derived state at lifecycle moments"

**Status:** Completed

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
- `src/gzkit/commands/status.py`
- `src/gzkit/commands/closeout_form.py`
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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [x] OBPI-0.0.9-02 (ledger-first status reads) for status derivation patterns

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/closeout.py` -- current closeout command
- [x] `src/gzkit/commands/attest.py` -- current attest command
- [x] `src/gzkit/commands/status.py` -- obpi reconcile command
- [x] `src/gzkit/ledger_semantics.py` -- ledger-first patterns
- [x] `src/gzkit/commands/closeout_form.py` -- frontmatter upsert helper

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests exist for auto-fix in each lifecycle command
- [x] `uv run -m unittest -q` passes

### Code Quality

- [x] `uv run ruff check . --fix && uv run ruff format .`
- [x] `uv run gz typecheck`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.test_lifecycle_auto_fix -v
# 8/8 pass in 0.003s
```

## Acceptance Criteria

- [x] REQ-0.0.9-04-01: `gz closeout` auto-fixes frontmatter status before completing
- [x] REQ-0.0.9-04-02: `gz attest` auto-fixes frontmatter status before completing
- [x] REQ-0.0.9-04-03: `gz obpi reconcile` auto-fixes frontmatter status
- [x] REQ-0.0.9-04-04: Tests verify auto-fix for each lifecycle command

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_lifecycle_auto_fix -v
8 tests in 0.003s — OK
```

### Value Narrative

Before this OBPI, frontmatter status in OBPI briefs could drift from
ledger-derived state silently. A brief could show `status: Draft` while the
ledger recorded it as `attested_completed`. Now `gz closeout`, `gz attest`,
and `gz obpi reconcile` silently fix frontmatter to match ledger-derived
state at every lifecycle moment.

### Key Proof

```text
# auto_fix_obpi_brief_frontmatter changes Draft -> Completed when ledger says attested_completed
uv run -m unittest tests.test_lifecycle_auto_fix.TestAutoFixObpiBriefFrontmatter.test_completed_state_fixes_draft_to_completed -v
# ok
```

### Implementation Summary

- Files created: `tests/test_lifecycle_auto_fix.py`
- Files modified: `src/gzkit/commands/closeout_form.py`, `closeout.py`, `attest.py`, `status.py`
- Tests added: 8 (all pass)
- Date completed: 2026-03-31
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-03-31

---

**Brief Status:** Completed

**Date Completed:** 2026-03-31

**Evidence Hash:** -
