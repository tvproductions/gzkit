---
id: OBPI-0.0.74-03-mx-gate5-invariants
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 3
lane: Heavy
status: Draft
req_atomic:
  # The never-relax floor is one indivisible authoring unit: the gate5_invariants
  # code constant and the structural guarantee that the checkpoint cannot
  # downgrade a member ship together (src/gzkit/mx/invariants.py plus the guard
  # inside src/gzkit/mx/checkpoint.py) with one covering test module. No REQ
  # below decomposes into independently-attributable labor steps.
  - REQ-0.0.74-03-01  # gate5_invariants code constant naming the never-relax guards
  - REQ-0.0.74-03-02  # checkpoint structurally cannot downgrade a member — same unit
  - REQ-0.0.74-03-03  # STRUCTURAL-FENCE: membership is the never-relax floor
---

# OBPI-0.0.74-03-mx-gate5-invariants: Mx Gate5 Invariants

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #3 - "gate5_invariants — the never-relax guards as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity); structural proof the checkpoint cannot downgrade a member; unit tests"

**Status:** Draft

## Objective

The never-relax guards land as a code constant `GATE5_INVARIANTS` at `src/gzkit/mx/invariants.py` (a code constant, NOT config) — faked Gate-5 attestation, secrets, operator-PII, ledger integrity — and the shared checkpoint at `src/gzkit/mx/checkpoint.py` is structurally unable to drop any member to advisory even under an active marker; "done" = the constant names exactly the four never-relax guards in code and unit tests prove the checkpoint cannot downgrade a member.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the never-relax floor on which airworthiness rests, which the checkpoint reads and can never relax — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope
- `src/gzkit/mx/invariants.py` **CREATE** — the `GATE5_INVARIANTS` code constant naming the never-relax guards (faked Gate-5 attestation, secrets, operator-PII, ledger integrity)
- `src/gzkit/mx/checkpoint.py` — the checkpoint reads `GATE5_INVARIANTS` and structurally cannot downgrade a member (consumer of the constant)
- `tests/mx/test_gate5_invariants.py` **CREATE** — unit tests for the constant's membership and the cannot-downgrade guarantee
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-03-mx-gate5-invariants.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/invariants.py`
- `tests/mx/test_gate5_invariants.py`
- `src/gzkit/mx/checkpoint.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: gate5_invariants — the never-relax guards as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity); structural proof the checkpoint cannot downgrade a member; unit tests.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/mx/invariants.py
test -f tests/mx/test_gate5_invariants.py
```

## Demo

```bash
# The never-relax guards as a code constant — these can never drop to advisory.
uv run python -c "from gzkit.mx.invariants import GATE5_INVARIANTS; print(sorted(GATE5_INVARIANTS))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-03-01 [behavior]: Given `GATE5_INVARIANTS`, when it is read, then it is a code constant (defined in `src/gzkit/mx/invariants.py`, not loaded from config) naming exactly the never-relax guards — faked Gate-5 attestation, secrets, operator-PII, ledger integrity. (@covers test in `tests/mx/test_gate5_invariants.py`)
- [ ] REQ-0.0.74-03-02 [behavior]: Given an active marker, when the checkpoint resolves a guard that is a member of `GATE5_INVARIANTS`, then the member stays fail-closed — the checkpoint structurally cannot downgrade it to advisory. (@covers test in `tests/mx/test_gate5_invariants.py`)
- [ ] REQ-0.0.74-03-03 [structural-fence]: Membership of `GATE5_INVARIANTS` is the never-relax floor on which airworthiness rests; no marker, lane, or sensitivity can remove a member. (parent ADR § Boundary Invariants — gate5_invariants never-relax floor)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
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

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
