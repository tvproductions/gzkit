---
id: OBPI-0.0.74-01-mx-marker-file
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 1
lane: Heavy
status: Completed
req_atomic:
  # The marker module is one indivisible authoring unit: the pydantic+stdlib
  # read/write (no gzkit-internal imports), the ledger-event binding check, and the
  # single-MX-truth-source property ship as a single src/gzkit/mx/marker.py
  # write with one covering test module. No REQ below decomposes into
  # independently-attributable labor steps.
  - REQ-0.0.74-01-01  # pydantic+stdlib read/write (no gzkit-internal imports); presence means MX==TRUE — written with the module
  - REQ-0.0.74-01-02  # ledger-event binding validity (hand-created marker is void) — same write
  - REQ-0.0.74-01-03  # STRUCTURAL-FENCE: single MX truth-source — property of the same module
---

# OBPI-0.0.74-01-mx-marker-file: Mx Marker File

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #1 - "The marker file — dumb filesystem truth-file (pydantic + stdlib only, no gzkit-internal imports); presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gzkit is broken; unit tests"

**Status:** Completed

## Objective

A pydantic + stdlib (json + pathlib) marker module that imports no gzkit-internal subsystem lands at `src/gzkit/mx/marker.py`: its presence on disk means MX==TRUE, it reads even when the rest of gzkit is the patient, and a marker is valid only when bound to a real `mx_session_opened` ledger event the tool wrote — a hand-created marker is void; "done" = the module reads/writes the marker without importing any gzkit-internal subsystem and unit tests pin both the presence==TRUE rule and the ledger-binding void rule.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the MX marker that every enforcement surface (code guards and agents) reads to decide MX==TRUE — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope
- `src/gzkit/mx/marker.py` **CREATE** — pydantic + stdlib (json + pathlib) marker read/write, no gzkit-internal imports; presence means MX==TRUE; ledger-event binding validity check (hand-created marker is void)
- `src/gzkit/mx/__init__.py` **CREATE** — `gzkit.mx` package init exposing the marker surface
- `tests/mx/test_marker.py` **CREATE** — unit tests for the presence==TRUE rule, the no-gzkit-internal-imports read, and the ledger-binding void rule
- `tests/mx/__init__.py` **CREATE** — test-package init so `unittest discover tests` imports `tests.mx.*` (every test-module subdir under `tests/` carries one)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-01-mx-marker-file.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/marker.py`
- `src/gzkit/mx/__init__.py`
- `tests/mx/test_marker.py`
- `tests/mx/__init__.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: The marker file — dumb filesystem truth-file (pydantic + stdlib only, no gzkit-internal imports); presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gzkit is broken; unit tests.
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
test -f src/gzkit/mx/marker.py
test -f src/gzkit/mx/__init__.py
test -f tests/mx/test_marker.py
```

## Demo

```bash
# Read the marker (pydantic + stdlib, no gzkit internals) — works even when the rest of gzkit is the patient.
uv run python -c "from gzkit.mx import marker; print('MX==TRUE' if marker.is_active() else 'MX==FALSE')"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-01-01 [behavior]: Given the marker module, when the marker file is present on disk, then `marker.is_active()` returns True — read without importing any gzkit-internal subsystem (pydantic + stdlib only, json + pathlib) — and the read succeeds even when unrelated gzkit subsystems fail to import (the marker reads when gzkit is the patient). (@covers test in `tests/mx/test_marker.py`)
- [ ] REQ-0.0.74-01-02 [behavior]: Given a marker file with no matching `mx_session_opened` ledger event the tool wrote, when validity is checked, then the marker is treated as void — a hand-created marker cannot stand in for a real opened session. (@covers test in `tests/mx/test_marker.py`)
- [ ] REQ-0.0.74-01-03 [structural-fence]: The marker is the single MX truth-source every surface (code guards and agents) consults — no surface reads MX state from anywhere else. (parent ADR § Boundary Invariants — single MX truth-source)

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


Anti-contrivance (REQ-01-02) and no-gzkit-imports (REQ-01-01) proven by TDD:
  $ uv run -m unittest tests.mx.test_marker -v
  Ran 12 tests ... OK
    test_handcreated_marker_with_no_event_is_void ... ok  (present, is_valid()==False)
    test_marker_bound_to_open_session_is_valid ... ok     (matching open => valid)
    test_closed_session_voids_the_marker ... ok           (later close => void)
    test_marker_module_imports_no_gzkit_internals ... ok  (reads when gzkit is the patient)
Full suite receipt arb-step-unittest-8c36eb010f774eadb9944bc84d6ed1de exit_status=0 (6363 tests). Demo: from gzkit.mx import marker; marker.is_active() -> MX==FALSE in the clean repo.

### Implementation Summary


- Files created: src/gzkit/mx/__init__.py, src/gzkit/mx/marker.py, tests/mx/__init__.py, tests/mx/test_marker.py
- Files modified: ADR-0.0.74 (Decision 1 + Checklist wording; gz->gzkit prose), OBPI-0.0.74-01 brief (allowlist + tests/mx/__init__.py; REQ-01-01/Objective wording; Tracked Defects), .gzkit/insights/agent-insights.jsonl (improvement insight)
- Mechanism: gzkit.mx.marker - Marker(BaseModel, frozen, extra=forbid); is_active() presence==MX==TRUE; is_valid() binds marker.session_id to an mx_session_opened ledger event read raw with stdlib (a later mx_session_closed voids it); marker_path() is the single truth-source (.gzkit/mx.json); module imports no gzkit internals (AST-asserted)
- Tests added: 12 (@covers-decorated: TestMarkerPresence x5 -> REQ-01-01, TestMarkerLedgerBinding x6 -> REQ-01-02; test_marker_path_is_single_truth_source backs REQ-01-03 structural-fence)
- In-flight correction: stdlib-only premise corrected to pydantic+stdlib, no gzkit-internal imports (operator-caught)
- Date completed: 2026-06-20
- Attestation status: operator-attested (g0) 'attest completed'
- Defects noted: (1) OBPI-07 brief carries pre-correction 'stdlib-only marker read' framing (tracked; route at OBPI-07); (2) behave_req_coverage precomplete gate vs waiver-ratchet deadlock for unit-only OBPIs - GHI to be filed; (3) adr-interview.json left as historical capture

## Tracked Defects

- **Sibling-OBPI coherence (surfaced during OBPI-01, route to OBPI-07).**
  OBPI-0.0.74-07's brief (`OBPI-0.0.74-07-mx-awareness-hook.md:46,75`) carries the
  pre-correction framing — "stdlib-only marker read" / "The marker read MUST be
  stdlib-only". The marker read now imports pydantic (a pinned core dependency;
  the corrected invariant is *no gzkit-internal imports*, ADR Decision #1 as
  reworded). `awareness.py` reuses this marker, so OBPI-07's REQ must be
  reconciled to "no gzkit-internal imports" when OBPI-07 is pulled, not literal
  stdlib-only. Not edited here — sibling brief outside OBPI-01's allowlist.
- **Historical capture (no action).** `adr-interview.json` preserves the raw
  interview verbatim ("Read with stdlib only…"); left intact as the immutable
  interview record. The binding ADR Decision/Checklist surfaces carry the
  correction.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed - OBPI-0.0.74-01 (MX marker) verified green: 12/12 tests.mx.test_marker pass; full suite green (receipt arb-step-unittest-8c36eb010f774eadb9944bc84d6ed1de, 6363 tests, exit_status=0 read from the ARB receipt - a piped exit had masked two RED runs earlier this session); lint arb-ruff-07db9c0fa81446948e841473fc490777, typecheck arb-step-typecheck-cdc0ca50e8bf474b980cb5b9aaa6a481, docs arb-step-mkdocs-78d00649c4814e8388e08955b708d7e6; @covers REQ-coverage chokepoint green. In-flight correction (operator-caught): the ADR 'stdlib-only' premise was confused - Marker is now a pydantic BaseModel (project standard, passes audit_pydantic_models, no waiver); the real invariant 'no gzkit-internal imports' is enforced by test_marker_module_imports_no_gzkit_internals; ADR Decision 1 + REQ-01-01 reworded.
- Date: 2026-06-20

---

**Date Completed:** 2026-06-20

**Evidence Hash:** -
