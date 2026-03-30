---
id: OBPI-0.0.9-05-l3-gate-independence
parent: ADR-0.0.9
item: 5
lane: lite
status: Draft
---

# OBPI-0.0.9-05: L3 Gate Independence

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #5 - "No Layer 3 artifact (pipeline markers, caches, derived indexes) can fail-close a gate check"

**Status:** Draft

## Objective

No Layer 3 artifact (pipeline markers, caches, derived indexes) can fail-close
a gate check. L3 artifacts are derived state -- they may produce warnings but
must never be the sole reason a gate fails. Gates must depend only on L1
(governance canon) and L2 (ledger events).

## Lane

**Lite** - Audit and refactor existing gate checks. No new subcommands or external contract changes.

## Allowed Paths

- `src/gzkit/commands/gates.py`
- `src/gzkit/pipeline_markers.py`
- `tests/`

## Denied Paths

- `docs/` -- no documentation changes in this OBPI
- `features/` -- no BDD features in this OBPI
- `.gzkit/ledger.jsonl` -- never edit manually

## Requirements (FAIL-CLOSED)

1. Audit all gate checks; identify any that depend solely on L3 artifacts
2. Refactor any L3-dependent gate checks to use L1/L2 evidence instead
3. L3 artifacts may produce warnings but must never cause gate failure
4. Add test asserting gates pass with all L3 artifacts (`.gzkit/markers/`) deleted

> STOP-on-BLOCKERS: if gate checks are not clearly separated from pipeline markers, halt and file defect.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] OBPI-0.0.9-01 (three-layer model) for layer definitions

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/gates.py` -- current gate check logic
- [ ] `src/gzkit/pipeline_markers.py` -- pipeline marker management
- [ ] `.gzkit/markers/` -- current marker files (if any)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Test exists proving gates pass with L3 artifacts deleted
- [ ] `uv run -m unittest -q` passes

### Code Quality

- [ ] `uv run ruff check . --fix && uv run ruff format .`
- [ ] `uvx ty check . --exclude 'features/**'`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
# Verify: delete .gzkit/markers/, run gz gates, confirm no failures from missing markers
```

## Acceptance Criteria

- [ ] REQ-0.0.9-05-01: No gate check reads pipeline markers as sole evidence
- [ ] REQ-0.0.9-05-02: Test proves gates pass after deleting all `.gzkit/markers/`
- [ ] REQ-0.0.9-05-03: L3 artifacts produce warnings only, never gate failures

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, L3-independence test exists
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
