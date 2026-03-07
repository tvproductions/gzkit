---
id: OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks: Compatibility adaptation for blocking hooks

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #2 — "OBPI-0.9.0-02: Adapt blocking/deferred canonical `.claude/hooks` for gzkit compatibility and record decisions with verification evidence."

**Status:** Draft

## Objective

Adapt canonical blocking/deferred `.claude/hooks` candidates into gzkit-safe behavior
(import, keep deferred, or exclude), with updated wiring and evidence for each decision.

## Lane

**Heavy** — Hook behavior changes operator control surfaces and requires
compatibility-safe rollout with documented verification.

## Allowed Paths

- `.claude/hooks/**` — Hook compatibility adaptations and tranche imports.
- `.claude/settings.json` — Hook wiring and matcher updates.
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` —
  intake updates and OBPI evidence.

## Denied Paths

- `src/**` and `tests/**` — Runtime/application behavior remains out of scope.
- `../airlineops/**` — Canonical source is read-only.
- Product-specific hooks (for example `dataset-guard.py`) unless ADR scope is revised.
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every canonical hook candidate reviewed in this tranche MUST be
   marked as imported, deferred, or excluded with rationale.
1. REQUIREMENT: Imported hooks MUST run through `uv run python` wiring in
   `.claude/settings.json`.
1. REQUIREMENT: Existing `ledger-writer.py` behavior MUST remain active.
1. NEVER: Do not enable blocking behavior without documented compatibility checks.
1. ALWAYS: Record deferred hooks with explicit follow-up target (OBPI or ADR).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical hook source exists: `../airlineops/.claude/hooks/`
- [ ] Claude settings exists: `.claude/settings.json`

**Existing Code (understand current state):**

- [ ] Existing intake decisions: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- [ ] Existing non-blocking imports: `.claude/hooks/instruction-router.py`, `.claude/hooks/post-edit-ruff.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run gz check-config-paths
uv run gz cli audit
uv run gz adr status ADR-0.9.0 --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.9.0-02-01: Given canonical `.claude/hooks` candidates classified as `Import with Compatibility` or `Defer`, when OBPI-02 completes, then each candidate has a concrete compatibility decision and implementation status.
- [ ] REQ-0.9.0-02-02: Given imported compatibility-safe hooks, when `.claude/settings.json` is reviewed, then each imported hook is wired with the correct matcher and command.
- [ ] REQ-0.9.0-02-03: Given deferred or excluded hooks, when intake evidence is reviewed, then each has explicit rationale and follow-up ownership.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
