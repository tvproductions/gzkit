---
id: OBPI-0.8.0-03-chores-lifecycle
parent: ADR-0.8.0-gz-chores-system
item: 3
lane: Heavy
status: in_progress
---

# OBPI-0.8.0-03-chores-lifecycle: Chores lifecycle (plan, list, audit) and logging

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- **Checklist Item:** #3 -- "Lifecycle: Planning, listing, auditing, and logging commands."

**Status:** Completed

## Objective

Deliver deterministic `gz chores list`, `gz chores plan`, and `gz chores audit` lifecycle behavior with evidence-backed logging visibility, without executing undeclared commands during lifecycle inspection.

## Lane

**Heavy** -- Lifecycle commands are user-facing CLI contracts and require docs + BDD + attestation evidence.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/obpis/OBPI-0.8.0-03-chores-lifecycle.md` -- record lifecycle evidence and acceptance state.
- `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md` -- reconcile parent ADR checklist linkage for completed OBPIs.

## Denied Paths

- `src/gzkit/**` -- no lifecycle behavior changes unless verification exposes a defect.
- `tests/**` -- no new tests unless command behavior fails verification.
- New dependencies unrelated to verification.
- CI files, lockfiles.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz chores list` must load the registry and present deterministic rows (`slug`, `lane`, `steps`, `title`).
1. REQUIREMENT: `gz chores plan <slug>` must show registry path, deterministic log path, evidence commands, and acceptance checks.
1. REQUIREMENT: `gz chores audit --all` must report log-presence status for each chore using deterministic log paths.
1. NEVER: Lifecycle commands (`list`, `plan`, `audit`) execute chore steps or shell strings.
1. ALWAYS: Lifecycle output remains config-first from `config/gzkit.chores.json` and references deterministic log locations under `docs/design/briefs/chores/`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` -- agent operating contract
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- [x] Related OBPIs reviewed for boundary (`OBPI-0.8.0-01`, `OBPI-0.8.0-02`)

**Prerequisites (check existence, STOP if missing):**

- [x] `config/gzkit.chores.json` exists and parses
- [x] `docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md` exists for audit visibility

**Existing Code (understand current state):**

- [x] Lifecycle implementation path: `src/gzkit/commands/chores.py` (`chores_list`, `chores_plan`, `chores_audit`)
- [x] Lifecycle test coverage path: `tests/commands/test_chores.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Coverage maintained: `uv run -m coverage run -m unittest discover tests && uv run -m coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz check` (includes format check)
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated (OBPI closeout evidence and ADR checklist reconciliation)

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run -m unittest discover tests
uv run -m coverage run -m unittest discover tests && uv run -m coverage report
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/

# OBPI-0.8.0-03 lifecycle proof
uv run gz chores list
uv run gz chores plan quality-check
uv run gz chores audit --all
```

## Acceptance Criteria

- [x] REQ-0.8.0-03-01: `gz chores list` renders registry entries from `config/gzkit.chores.json`.
- [x] REQ-0.8.0-03-02: `gz chores plan quality-check` reports deterministic lifecycle details including log path and acceptance checks.
- [x] REQ-0.8.0-03-03: `gz chores audit --all` reports log presence for configured chores.
- [x] REQ-0.8.0-03-04: Lifecycle commands remain non-executing inspection/audit surfaces.
- [x] REQ-0.8.0-03-05: Human attestation explicitly accepts lifecycle closeout evidence.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now documented below
- [x] **Key Proof:** One concrete usage example included below
- [x] **OBPI Acceptance:** Human attestation and OBPI receipt event recorded

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.commands.test_chores -v
Ran 8 tests in 1.173s
OK

$ uv run -m unittest discover tests
Ran 303 tests in 3.704s
OK

$ uv run -m coverage run -m unittest discover tests && uv run -m coverage report
Ran 303 tests in 4.824s
OK
TOTAL                                    8478   1097    87%

$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Code Quality

```text
$ uv run gz lint
All checks passed.

$ uv run gz typecheck
All checks passed.

$ uv run mkdocs build --strict
Documentation built successfully.
```

### Value Narrative

Before this OBPI closeout, lifecycle behavior existed but completion evidence for list/plan/audit command contracts was not captured in the OBPI ledger chain. After this OBPI, lifecycle command proofs, gate verification, and checklist linkage are documented and ready for heavy-lane human attestation.

### Key Proof

`uv run gz chores plan quality-check` and `uv run gz chores audit --all` now provide deterministic lifecycle evidence tied to:
`docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md`

### Implementation Summary

- Files created/modified: `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/obpis/OBPI-0.8.0-03-chores-lifecycle.md`, `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- Tests added: none (existing lifecycle coverage in `tests/commands/test_chores.py` validated)
- Date completed: 2026-03-07

## Human Attestation

- Attestor: human:jeff
- Attestation: Accepted. I attest I understand the completion of OBPI-0.8.0-03-chores-lifecycle.
- Date: 2026-03-07

---

**Brief Status:** Completed

**Date Completed:** 2026-03-07

**Evidence Hash:** d92a0f5
