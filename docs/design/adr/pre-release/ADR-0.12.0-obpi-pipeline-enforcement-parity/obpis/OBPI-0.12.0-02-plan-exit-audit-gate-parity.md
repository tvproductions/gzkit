---
id: OBPI-0.12.0-02-plan-exit-audit-gate-parity
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.12.0-02-plan-exit-audit-gate-parity: Plan-exit audit gate parity

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #2 - "OBPI-0.12.0-02: Port the plan-exit audit gate with gzkit-compatible blocking behavior."

**Status:** Draft

## Objective

Port the AirlineOps `plan-audit-gate.py` hook into gzkit as a generated Claude
hook artifact with faithful allow/block behavior for plan-audit receipts, while
leaving `.claude/settings.json` registration to `OBPI-0.12.0-06`.

## Lane

**Heavy** -- This unit ports a blocking runtime contract used by operators and
future Claude hook orchestration.

## Allowed Paths

- `src/gzkit/hooks/claude.py` -- generated hook source of truth
- `tests/test_hooks.py` -- direct hook behavior and hook-generation coverage
- `.claude/hooks/**` and `.claude/settings.json` -- generated Claude hook
  artifacts and settings surface touched by control-surface sync
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- ADR, parity matrix, and OBPI evidence package for this tranche

## Denied Paths

- `../airlineops/**`
- `.gzkit/skills/gz-plan-audit/**` -- already owned by `OBPI-0.12.0-07`
- `.claude/hooks/pipeline-router.py`, `.claude/hooks/pipeline-gate.py`,
  `.claude/hooks/pipeline-completion-reminder.py` -- later hook OBPIs
- Active `.claude/settings.json` registration/order changes -- reserved for
  `OBPI-0.12.0-06`
- New dependencies, CI files, lockfiles, or unrelated runtime changes

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The hook MUST be generated into
   `.claude/hooks/plan-audit-gate.py` from `src/gzkit/hooks/claude.py`.
1. REQUIREMENT: The hook MUST choose the newest non-hidden markdown plan from
   `.claude/plans/` and extract all referenced OBPI ids.
1. REQUIREMENT: The hook MUST block plan exit when the audit receipt is
   missing, corrupt, stale by file mtime, mismatched to the plan OBPI, or has
   an invalid verdict.
1. REQUIREMENT: The hook MUST allow exit when no OBPI plan is present or when a
   matching receipt with verdict `PASS` or `FAIL` is newer than the plan file.
1. REQUIREMENT: The non-blocking prior-art reminder from AirlineOps MUST be
   preserved.
1. REQUIREMENT: `.claude/settings.json` MUST remain unwired for this hook in
   this OBPI; registration is a later tranche.
1. NEVER: Reinterpret this gate into PASS-only routing behavior; that belongs
   to `OBPI-0.12.0-03`.
1. ALWAYS: Keep the operator error text explicit about running
   `/gz-plan-audit <OBPI-ID>` before exiting plan mode.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `../airlineops/.claude/hooks/plan-audit-gate.py`
- [x] `.claude/settings.json`
- [x] `src/gzkit/hooks/claude.py`
- [x] `tests/test_hooks.py`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related OBPIs in the same ADR, especially `OBPI-0.12.0-03` and
      `OBPI-0.12.0-06`

**Prerequisites (check existence, STOP if missing):**

- [x] Hook generator exists: `src/gzkit/hooks/claude.py`
- [x] Generated hook sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Receipt contract exists:
      `.gzkit/skills/gz-plan-audit/SKILL.md`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Targeted hook tests pass
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run python -m unittest tests.test_hooks -v
uv run gz agent sync control-surfaces
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.12.0-02-01: `.claude/hooks/plan-audit-gate.py` exists as a
      generated hook and enforces the receipt allow/block contract when
      executed directly.
- [x] REQ-0.12.0-02-02: The hook preserves AirlineOps parity for receipt
      freshness and the advisory prior-art warning.
- [x] REQ-0.12.0-02-03: The repo documents the hook as ported but still
      unregistered in `.claude/settings.json`.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief and linked to checklist item #2.
- [x] Parity matrix updated to `Ported (inactive)` for `plan-audit-gate.py`.
- [x] Current contract keeps registration deferred to `OBPI-0.12.0-06`.

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_hooks -v
Ran 23 tests in 0.282s

OK

$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/plan-audit-gate.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Running tests...
Ran 359 tests in 8.823s

OK

Tests passed.
```

### Code Quality

```text
$ uv run gz lint
Running linters...
All checks passed!

ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!

Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.75 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.318s
```

### Gate 5 (Human)

```text
# Pending human attestation
```

## Value Narrative

Before this OBPI, gzkit had the `gz-plan-audit` skill and receipt contract but
no native hook implementation that could enforce “audit before exiting plan
mode.” After this tranche, the blocking hook exists as a tested generated
surface with faithful receipt semantics, and the repo documents it honestly as
ported but not yet wired into active Claude settings.

## Key Proof

Direct hook target:

```text
.claude/hooks/plan-audit-gate.py
```

### Implementation Summary

- Files created/modified:
  - `src/gzkit/hooks/claude.py`
  - `tests/test_hooks.py`
  - Generated `.claude/hooks/plan-audit-gate.py` plus README/settings surfaces
  - ADR package files in this tranche
- Tests added: direct plan-audit gate behavior coverage in `tests/test_hooks.py`
- Date completed: 2026-03-12
- Attestation status: pending
- Defects noted: none currently; final settings registration remains tracked by
  `OBPI-0.12.0-06`

## Human Attestation

- Attestor: `human:<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
