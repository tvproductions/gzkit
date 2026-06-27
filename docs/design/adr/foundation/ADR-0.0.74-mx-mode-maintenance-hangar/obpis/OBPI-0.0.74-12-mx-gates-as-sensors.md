---
id: OBPI-0.0.74-12-mx-gates-as-sensors
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 12
lane: Heavy
status: Completed
req_atomic:
  # Gates-as-sensors + the one disposition handler is one indivisible authoring unit:
  # the guard-emits-a-level contract, the single level->route handler (disposition.py
  # built from the ADR matrix), and the under-marker demotion (non-floor to advisory,
  # gate5 pinned CRITICAL) ship together with one covering test module. No REQ below
  # decomposes into independently-attributable labor steps.
  - REQ-0.0.74-12-01  # a guard emits a GZ_<LEVEL> sensor reading instead of self-deciding block/warn
  - REQ-0.0.74-12-02  # the one handler maps level->route per the matrix; under marker non-floor demote to advisory, gate5 pins CRITICAL
  - REQ-0.0.74-12-03  # STRUCTURAL-FENCE: the one disposition handler routes the checkpoint-resolved level
---

# OBPI-0.0.74-12-mx-gates-as-sensors: Mx Gates As Sensors

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #12 - "Gates-as-T/F sensors + the one disposition handler — guards emit a `GZ_<LEVEL>` instead of self-deciding; one handler maps the (design × build × vibes) diagnosis → level → route (AOG/MX hangar, GHI-fix, refactor/Chores, drift-drain, track); unit tests"

**Status:** Completed

## Objective

The one disposition handler lands at `src/gzkit/mx/disposition.py`: each guard stops self-deciding block/warn and instead emits a `GZ_<LEVEL>` (a T/F sensor reading); ONE handler maps that checkpoint-resolved level to its route per the parent ADR's (design × build × vibes) matrix — CRITICAL → AOG/MX hangar, ERROR → block/GHI-fix, WARNING → refactor/Chores, NOTICE → drift/Chores-drain, INFO → track, DEBUG → steering — and under an active marker non-floor levels demote to advisory debt accrued visibly on the ledger while `gate5_invariants` pin to CRITICAL. "Done" = `disposition.py` is the single level→route mapping, the checkpoint routes a guard's emitted level through it, and unit tests pin each matrix row plus the under-marker demotion and the gate5 CRITICAL pin.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the single disposition handler every guard's level routes through, replacing per-guard self-decided dispositions — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 12, the matrix table)
- `src/gzkit/mx/disposition.py` **CREATE** — the one disposition handler: the level→route matrix from the parent ADR
- `src/gzkit/mx/checkpoint.py` — the checkpoint routes a guard's emitted `GZ_<LEVEL>` through the handler (consumer); under-marker demotion of non-floor levels
- `tests/mx/test_disposition.py` **CREATE** — unit tests for each matrix row, the under-marker non-floor demotion, and the `gate5_invariants` CRITICAL pin
- `src/gzkit/mx/marker.py` — **READ-ONLY fixture dependency** (unchanged; owned by OBPI-02): the under-marker tests import `marker.write`/`marker.is_active` to set up the active-marker fixture, matching the `test_checkpoint.py` convention
- `src/gzkit/mx/__init__.py` — **READ-ONLY package dependency** (unchanged): the `gzkit.mx` package init through which the tests import siblings
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-12-mx-gates-as-sensors.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/disposition.py`
- `tests/mx/test_disposition.py`

## Denied Paths

- Paths not listed in Allowed Paths
- The `GZ_<LEVEL>` vocabulary / grounding threshold (owned by OBPI-0.0.74-11)
- A second disposition input — re-expanding the (level × owning-airlock) 2-D matrix (ADR § Alternatives, rejection (g)); the handler is level-keyed, the airlock is the route not a second input
- Redefining or relaxing the `gate5_invariants` never-relax list (owned by OBPI-0.0.74-03)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A guard MUST emit a `GZ_<LEVEL>` (a sensor reading) rather than self-deciding block/warn; the disposition is computed in ONE place, not at the guard (REQ-12-01).
1. REQUIREMENT: `src/gzkit/mx/disposition.py` MUST map each level to its route exactly as the parent ADR matrix declares — CRITICAL → AOG/MX hangar, ERROR → block/GHI-fix, WARNING → refactor/Chores, NOTICE → drift/Chores-drain, INFO → track, DEBUG → steering (REQ-12-02).
1. REQUIREMENT: Under an active marker, non-floor levels MUST demote to advisory (visible ledger debt) while `gate5_invariants` pin to CRITICAL — the demotion never crosses the floor (REQ-12-02).
1. NEVER: Add a second disposition input (a level × airlock 2-D matrix); the handler is level-keyed (REQ-12-03).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-02) and the `GZ_<LEVEL>` vocabulary (`src/gzkit/mx/levels.py`, OBPI-11) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 12 — quoted verbatim:** "Gates-as-T/F sensors + the one disposition handler (the matrix). Each guard stops self-deciding block/warn and instead emits a `GZ_<LEVEL>`; ONE handler maps level → disposition. The level is the diagnosis of three axes — is the **design** wrong? is the **build** wrong? did the agent **vibe**? — where the forward airlocks (Design, Build) are the diagnosis axes and the maintenance airlocks (MX, Chores) are the routes ... gate5_invariants pin to CRITICAL (item 3); under the marker, non-floor levels demote to advisory debt accrued visibly on the ledger."
- [ ] Parent ADR § Decision item 12 — the matrix table (CRITICAL/ERROR/WARNING/NOTICE/INFO/DEBUG rows): copy each row's route verbatim into `disposition.py`.
- [ ] Parent ADR § Intent — the airlock frame; forward airlocks diagnose, maintenance airlocks route.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `docs/governance/work-phases-and-airlock.md` — the four-airlock (Design | Build | MX | Chores) frame the matrix routes against

**Context:**

- [ ] `src/gzkit/mx/levels.py` (OBPI-11) — the `GZ_<LEVEL>` vocabulary the handler keys on
- [ ] `src/gzkit/mx/checkpoint.py` (OBPI-02) — the checkpoint that resolves the level and routes it through the handler
- [ ] `src/gzkit/mx/checkpoint.py` — the `GATE5_INVARIANTS` frozenset (seeded by OBPI-02; OBPI-03 formal set pending; the constant lives in checkpoint.py, not a separate invariants.py)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/checkpoint.py` exists (OBPI-0.0.74-02 has landed)
- [ ] `src/gzkit/mx/levels.py` exists (OBPI-0.0.74-11 has landed)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/mx/test_checkpoint.py` reviewed for the local test convention before authoring `test_disposition.py`
- [ ] `src/gzkit/mx/checkpoint.py` reviewed for how guards currently consult the checkpoint (the self-deciding seam this OBPI replaces)

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
test -f src/gzkit/mx/disposition.py
test -f tests/mx/test_disposition.py
```

## Demo

```bash
# The checkpoint routes each guard's emitted level through the one disposition
# handler; the rendition-floor gate exercises it. Matrix pinned by tests/mx/test_disposition.py.
uv run gz validate --rendition-floor-coherence
```

## Acceptance Criteria

- [ ] REQ-0.0.74-12-01 [behavior]: Given a fail-closed guard, when it reports, then it emits a `GZ_<LEVEL>` (a sensor reading) rather than self-deciding block/warn — the block-or-advise disposition is computed in ONE place (the handler), not at the guard. (@covers test in `tests/mx/test_disposition.py`)
- [ ] REQ-0.0.74-12-02 [behavior]: Given the one disposition handler, when a level is routed, then it maps to its parent-ADR matrix disposition (CRITICAL → AOG/MX hangar, ERROR → block/GHI-fix, WARNING → refactor/Chores, NOTICE → drift/Chores-drain, INFO → track, DEBUG → steering); and under an active marker non-floor levels demote to advisory (visible ledger debt) while a `gate5_invariant` pins to CRITICAL. (@covers test in `tests/mx/test_disposition.py`)
- [ ] REQ-0.0.74-12-03 [structural-fence]: The one disposition handler routes the checkpoint-resolved level; a guard that decides its own disposition without passing its level through the handler is the named coverage defect (parent ADR § Boundary Invariants #2 — the one disposition handler routes that level).

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

Before: each guard decided its own disposition — block here, warn there — so the never-relax floor and the advisory-demotion rule were re-encoded at every call site (the exact opt-in coverage surface ADR § Alternatives (a) rejects). Now: guards are dumb sensors that emit a `GZ_<LEVEL>`, and ONE handler owns the level→route matrix; the marker's advisory demotion and the gate5 CRITICAL pin live in exactly one place, so a new guard inherits correct routing for free and nobody can forget the floor.

### Key Proof


Command: uv run -m unittest tests/mx/test_disposition.py -v

All 5 tests pass. test_gate5_invariant_pins_critical_route iterates every GATE5_INVARIANTS member under an active marker and asserts Route.AOG_MX_HANGAR (the floor cannot be demoted); test_non_floor_guard_demotes_to_advisory confirms non-floor guards under the marker resolve to Route.ADVISORY; test_each_matrix_row pins all six ADR matrix rows. Receipts: arb-step-unittest-b0e62c71321b4561ae23def93bd51fb6, arb-ruff-f5b4455a57754a889583e4b6f3d5b564, arb-step-typecheck-8cb68a897949499c89fabadefb486151, arb-step-mkdocs-66a758be7f454e4ebe0846608a854eec.

### Implementation Summary


- Decision item 12 (verbatim): "Gates-as-T/F sensors + the one disposition handler (the matrix). Each guard stops self-deciding block/warn and instead emits a GZ_<LEVEL>; ONE handler maps level -> disposition."
- Files created: src/gzkit/mx/disposition.py (Route StrEnum + route() matrix handler); tests/mx/test_disposition.py (5 tests, 3 classes)
- Files modified: src/gzkit/mx/checkpoint.py (added resolve(); is_advisory() preserved); ADR-0.0.74 matrix enriched with V.I.B.E.S.-management-band semantics (operator refinement)
- Tests added: 6-row matrix coverage, sensor-API interface, non-floor under-marker demotion, gate5-invariant CRITICAL pin, CRITICAL-floor no-demotion
- Date completed: 2026-06-22
- Attestation status: operator-attested ("attest completed")
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-12 lands the one disposition handler (src/gzkit/mx/disposition.py): guards emit a GZ_<LEVEL> sensor reading and checkpoint.resolve() routes it through the single ADR-matrix handler, with under-marker non-floor demotion to ADVISORY and gate5_invariants pinned to CRITICAL. Operator refined the sub-ERROR rows into the V.I.B.E.S.-management band (NOTICE=escalation, INFO=tracking incl. inherent model behavior, DEBUG=anti-vibing steering), now encoded in disposition.py and the ADR matrix. Verified: 5/5 scoped tests pass, behavior_uncovered_reqs=0, lint/typecheck/mkdocs clean. Receipts arb-step-unittest-b0e62c71321b4561ae23def93bd51fb6, arb-ruff-f5b4455a57754a889583e4b6f3d5b564, arb-step-typecheck-8cb68a897949499c89fabadefb486151, arb-step-mkdocs-66a758be7f454e4ebe0846608a854eec.
- Date: 2026-06-22

---

**Date Completed:** 2026-06-22

**Evidence Hash:** -
