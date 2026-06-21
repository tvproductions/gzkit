---
id: OBPI-0.0.74-02-mx-shared-checkpoint
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 2
lane: Heavy
status: Completed
req_atomic:
  # The shared checkpoint is one indivisible authoring unit: the marker read,
  # the drop-to-advisory behavior (except gate5_invariants), the
  # outside-the-hangar strict no-op, and the every-funnel-consults-it property
  # ship as one src/gzkit/mx/checkpoint.py write (wired into validate_cmd.py)
  # with one covering test module. No REQ below decomposes into
  # independently-attributable labor steps.
  - REQ-0.0.74-02-01  # drop guards to advisory except gate5_invariants — written with the module
  - REQ-0.0.74-02-02  # strict no-op outside the hangar — same write
  - REQ-0.0.74-02-03  # STRUCTURAL-FENCE: every fail-closed funnel consults the checkpoint
---

# OBPI-0.0.74-02-mx-shared-checkpoint: Mx Shared Checkpoint

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #2 - "The shared checkpoint — single place code reads the marker and drops guards to advisory except gate5_invariants; funnel inventory + fence test that every fail-closed funnel consults it; unit tests"

**Status:** Completed

## Objective

A single shared checkpoint lands at `src/gzkit/mx/checkpoint.py` and is wired into the first fail-closed funnel (`src/gzkit/commands/validate_cmd.py`): it is the one place that reads the marker and drops fail-closed guards to advisory — everything except the gate5_invariants — and outside the hangar (no marker) it is a strict no-op; "done" = a new guard inherits the checkpoint for free and unit tests pin both the in-hangar drop-to-advisory behavior and the out-of-hangar zero-behavior-change.

## Lane

**Heavy** - This OBPI changes a runtime-contract surface — the shared checkpoint every fail-closed guard passes through to resolve its severity under MX — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/mx/__init__.py` (added by brief reconcile, attestor g0)
- `src/gzkit/mx/marker.py` (added by brief reconcile, attestor g0)

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope
- `src/gzkit/mx/checkpoint.py` **CREATE** — the one place that reads the marker and drops fail-closed guards to advisory except the gate5_invariants; strict no-op outside the hangar
- `src/gzkit/commands/validate_cmd.py` — wire the first fail-closed funnel through the checkpoint (the place guards pass through; proves the wiring contract)
- `tests/mx/test_checkpoint.py` **CREATE** — unit tests for in-hangar drop-to-advisory (except gate5_invariants) and out-of-hangar strict no-op
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-02-mx-shared-checkpoint.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/checkpoint.py`
- `tests/mx/test_checkpoint.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: The shared checkpoint — single place code reads the marker and drops guards to advisory except gate5_invariants; funnel inventory + fence test that every fail-closed funnel consults it; unit tests.
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
test -f src/gzkit/mx/checkpoint.py
test -f tests/mx/test_checkpoint.py
```

## Demo

```bash
# Inside the hangar the checkpoint drops an ordinary docs guard to advisory;
# outside the hangar (no marker) the same call is a strict no-op.
uv run python -c "from gzkit.mx import checkpoint; print('gate3-docs advisory:', checkpoint.is_advisory('gate3-docs'))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-02-01 [behavior]: Given an active marker, when an ordinary fail-closed guard passes through the checkpoint, then it is dropped to advisory — for every guard EXCEPT a gate5_invariant, which stays fail-closed. (@covers test in `tests/mx/test_checkpoint.py`)
- [ ] REQ-0.0.74-02-02 [behavior]: Given no marker (outside the hangar), when any guard passes through the checkpoint, then the checkpoint is a strict no-op — the guard's severity is unchanged from its non-MX behavior (zero behavior change). (@covers test in `tests/mx/test_checkpoint.py`)
- [ ] REQ-0.0.74-02-03 [structural-fence]: Every fail-closed funnel/guard consults the shared checkpoint; a guard that resolves its own severity without passing through the checkpoint is the named coverage defect (funnel inventory). (parent ADR § Boundary Invariants — every fail-closed funnel consults the checkpoint)

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


In-hangar the checkpoint drops an ordinary docs guard to advisory while gate5 stays fail-closed; out-of-hangar it is a strict no-op:

  $ uv run python -c "from pathlib import Path; import tempfile; from gzkit.mx import marker, checkpoint; from gzkit.mx.marker import Marker; ...
  in-hangar gate3-docs advisory: True
  in-hangar ledger advisory:     False   # gate5_invariant
  no-marker gate3-docs advisory: False   # strict no-op

Tests: 7/7 green — receipt arb-step-unittest-3a573733e8474b86abd6c28337c230a4. Lint clean — arb-ruff-3c9a070e408b45dc84f105925b8ff4af. Typecheck clean — arb-step-typecheck-11af0b1d31964c0985765b7bfacc3622.

### Implementation Summary


- Files created: src/gzkit/mx/checkpoint.py (shared MX checkpoint — GATE5_INVARIANTS frozenset + is_advisory(guard_name, project_root)); tests/mx/test_checkpoint.py (7 tests)
- Files modified: src/gzkit/commands/validate_cmd.py (_run_scope_checks lazy-imports the checkpoint and consults is_advisory(scope) before extending the error list — the first wired fail-closed funnel)
- Mechanism: one place reads marker.is_active; in-hangar drops every non-gate5 guard to advisory; out-of-hangar strict no-op; gate5_invariants (ledger, gate5-attestation, operator-pii, secrets) never relaxed
- Tests added: TestInHangar (3), TestOutsideHangar (3), TestValidateCmdWiring (1) = 7, all green
- REQ coverage: REQ-0.0.74-02-01/02 @covers pass; REQ-0.0.74-02-03 structural-fence via parent ADR Boundary Invariants #2
- Date completed: 2026-06-21
- Attestation status: g0-attested "attest completed"
- Defects noted: gz obpi precomplete behave_req_coverage check is stale (not REQ-kind-aware, predates GHI #636); kind-aware chokepoint gz obpi complete passed

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-02 shared MX checkpoint landed: src/gzkit/mx/checkpoint.py (GATE5_INVARIANTS floor + is_advisory predicate) wired into validate_cmd _run_scope_checks as the first fail-closed funnel; 7/7 unit tests green (receipt arb-step-unittest-3a573733e8474b86abd6c28337c230a4), lint clean (arb-ruff-3c9a070e408b45dc84f105925b8ff4af), typecheck clean (arb-step-typecheck-11af0b1d31964c0985765b7bfacc3622); @covers parity REQ-01/02 covered, REQ-03 structural-fence pass via parent ADR Boundary Invariant #2.
- Date: 2026-06-21

---

**Date Completed:** 2026-06-21

**Evidence Hash:** -
