---
id: OBPI-0.0.9-05-l3-gate-independence
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 5
lane: lite
status: attested_completed
---

# OBPI-0.0.9-05: L3 Gate Independence

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #5 - "No Layer 3 artifact (pipeline markers, caches, derived indexes) can fail-close a gate check"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [x] OBPI-0.0.9-01 (three-layer model) for layer definitions

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/gates.py` -- current gate check logic
- [x] `src/gzkit/pipeline_markers.py` -- pipeline marker management
- [x] `.gzkit/markers/` -- current marker files (if any)

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Test exists proving gates pass with L3 artifacts deleted
- [x] `uv run -m unittest -q` passes

### Code Quality

- [x] `uv run ruff check . --fix && uv run ruff format .`
- [x] `uvx ty check . --exclude 'features/**'`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
# Verify: delete .gzkit/markers/, run gz gates, confirm no failures from missing markers
```

## Acceptance Criteria

- [x] REQ-0.0.9-05-01: No gate check reads pipeline markers as sole evidence
- [x] REQ-0.0.9-05-02: Test proves gates pass after deleting all `.gzkit/markers/`
- [x] REQ-0.0.9-05-03: L3 artifacts produce warnings only, never gate failures

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, L3-independence test exists
- [x] **Code Quality:** Ruff and ty pass
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
test_gate1_passes_after_markers_deleted ... ok
test_gate1_passes_with_markers_directory_present ... ok
test_gate1_passes_without_markers_directory ... ok
test_gate_imports_exclude_pipeline_markers ... ok
test_gates_independent_of_pipeline_active_markers ... ok

Ran 5 tests in 0.016s
OK
```

### Value Narrative

Before this OBPI, there was no test or documented audit proving that gate checks are independent of Layer 3 artifacts. If a future change introduced an L3 dependency in gate logic, it would silently violate the state doctrine's authority rules. Now, 5 tests prove empirically that gates depend only on L1 (governance canon) and L2 (ledger events), and a static AST guard prevents gates.py from importing pipeline_markers in the future.

### Key Proof

```bash
uv run -m unittest tests.commands.test_l3_gate_independence -v
```

### Implementation Summary

- Files created/modified: tests/commands/test_l3_gate_independence.py (created)
- Tests added: 5 tests (gate1 without markers, with markers, after deletion, pipeline marker independence, AST import guard)
- Date completed: 2026-03-31
- Attestation status: Human attested
- Defects noted: None — gates.py was already L3-independent; no refactoring needed

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: attest completed
- Date: 2026-03-31

---

**Brief Status:** Completed

**Date Completed:** 2026-03-31

**Evidence Hash:** -
