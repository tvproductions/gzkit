---
id: OBPI-0.0.74-01-mx-marker-file
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 1
lane: Heavy
status: Draft
req_atomic:
  # The marker module is one indivisible authoring unit: the stdlib-only
  # read/write, the ledger-event binding validity check, and the
  # single-MX-truth-source property ship as a single src/gzkit/mx/marker.py
  # write with one covering test module. No REQ below decomposes into
  # independently-attributable labor steps.
  - REQ-0.0.74-01-01  # stdlib-only read/write; presence means MX==TRUE — written with the module
  - REQ-0.0.74-01-02  # ledger-event binding validity (hand-created marker is void) — same write
  - REQ-0.0.74-01-03  # STRUCTURAL-FENCE: single MX truth-source — property of the same module
---

# OBPI-0.0.74-01-mx-marker-file: Mx Marker File

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #1 - "The marker file — dumb stdlib-only filesystem truth-file; presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gz is broken; unit tests"

**Status:** Draft

## Objective

A stdlib-only (json + pathlib) marker module lands at `src/gzkit/mx/marker.py`: its presence on disk means MX==TRUE, it reads even when the rest of gz is broken, and a marker is valid only when bound to a real `mx_session_opened` ledger event the tool wrote — a hand-created marker is void; "done" = the module reads/writes the marker with stdlib only and unit tests pin both the presence==TRUE rule and the ledger-binding void rule.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the MX marker that every enforcement surface (code guards and agents) reads to decide MX==TRUE — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope
- `src/gzkit/mx/marker.py` **CREATE** — stdlib-only (json + pathlib) marker read/write; presence means MX==TRUE; ledger-event binding validity check (hand-created marker is void)
- `src/gzkit/mx/__init__.py` **CREATE** — `gzkit.mx` package init exposing the marker surface
- `tests/mx/test_marker.py` **CREATE** — unit tests for the presence==TRUE rule, the stdlib-only read, and the ledger-binding void rule
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-01-mx-marker-file.md` — this brief (evidence recording)

## Creates These Files

- `src/gzkit/mx/marker.py`
- `src/gzkit/mx/__init__.py`
- `tests/mx/test_marker.py`

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver: The marker file — dumb stdlib-only filesystem truth-file; presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gz is broken; unit tests.
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
# Read the marker with stdlib only — works even when the rest of the toolchain is down.
uv run python -c "from gzkit.mx import marker; print('MX==TRUE' if marker.is_active() else 'MX==FALSE')"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-01-01 [behavior]: Given the marker module, when the marker file is present on disk, then `marker.is_active()` returns True — read with stdlib only (json + pathlib) — and the read succeeds even when unrelated gz subsystems fail to import (the marker reads when gz is the patient). (@covers test in `tests/mx/test_marker.py`)
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
