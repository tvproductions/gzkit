---
id: OBPI-0.0.74-09-mx-retire-staging-flags
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 9
lane: Heavy
status: Draft
req_atomic:
  - REQ-0.0.74-09-01  # one deletion+rewire behavior (both flags gone; severity resolved through the shared checkpoint) + its tests — single indivisible unit
  - REQ-0.0.74-09-02  # one negative-control behavior (both gates' NCs still flag when forced hard) — no labor below the REQ
  - REQ-0.0.74-09-03  # STRUCTURAL-FENCE: parent-ADR Boundary Invariant (the checkpoint is the single severity authority); audited at closeout, no labor
---

# OBPI-0.0.74-09-mx-retire-staging-flags: Retire the Two Hand-Set Staging Flags

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #9 - "Retire the two hand-set staging flags — delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve severity through the marker mechanism; unit tests"

**Status:** Draft

## Objective

Delete `_FRESHNESS_FAIL_CLOSED` (`rendition_freshness.py`) and `_FLOOR_FAIL_CLOSED` (`rendition_floor_coherence.py`) and route both gates' effective severity through the one shared MX checkpoint — advisory inside the hangar (marker present), full strength outside — so the two hand-set hacks collapse into the honest generalization with a single severity authority, and no per-gate staging flag is left for anyone to forget or forge.

## Lane

**Heavy** - This OBPI changes the runtime severity-resolution contract of two `gz check` validators (the source of their fail-closed-vs-advisory decision moves from a hand-set module constant to the shared checkpoint).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 9, § Consequences/Positive #2)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/**` — parent ADR package scope (this brief's evidence)
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — delete `_FRESHNESS_FAIL_CLOSED`; resolve effective severity through the shared checkpoint
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — delete `_FLOOR_FAIL_CLOSED`; resolve effective severity through the shared checkpoint
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — keep `_rendition_freshness_negative_control` / `_rendition_floor_coherence_negative_control` binding (they already force `fail_closed=True`); update only if the severity-resolution signature changes
- `tests/governance/test_rendition_freshness.py` — tests for the rewired gate
- `tests/governance/test_rendition_floor_coherence.py` — tests for the rewired gate

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `sensitivity: security` is not declared.)

## Denied Paths

- Paths not listed in Allowed Paths
- Reintroducing ANY per-gate hand-set staging flag — no new `_*_FAIL_CLOSED` (or equivalent) module constant anywhere in the codebase
- Redefining or relaxing the `gate5_invariants` never-relax list (owned by OBPI-0.0.74-03)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `_FRESHNESS_FAIL_CLOSED` and `_FLOOR_FAIL_CLOSED` MUST be deleted; neither module retains a hand-set staging constant (REQ-09-01).
1. REQUIREMENT: Both gates MUST resolve effective severity through the one shared checkpoint — advisory inside the hangar (marker present), full strength outside (REQ-09-01).
1. REQUIREMENT: Both gates' negative controls MUST still flag their planted fixtures when forced hard (`fail_closed=True`) — the gates genuinely bind after the rewire (REQ-09-02).
1. NEVER: Reintroduce a per-gate hand-set staging flag — the checkpoint is the single severity authority (REQ-09-03).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the shared checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-0.0.74-02) and the marker (OBPI-0.0.74-01) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 9 — quoted verbatim:** "Retire the two hand-set staging flags. Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their severity through the one marker mechanism (the honest generalization of the two hacks)."
- [ ] Parent ADR § Intent — the hangar frame: 'Loose in the bay, hard at the door'; the marker drops guards to advisory except the `gate5_invariants`.
- [ ] Parent ADR § Decision items 1–3 — the marker, the shared checkpoint, and the `gate5_invariants` this rewire depends on.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `src/gzkit/governance/trust_audits/rendition_freshness.py` and `rendition_floor_coherence.py` — the two `_*_FAIL_CLOSED` flags and the `fail_closed: bool | None` resolution pattern being generalized
- [ ] `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_rendition_freshness_negative_control` / `_rendition_floor_coherence_negative_control` (they already pass `fail_closed=True`)

**Context:**

- [ ] OBPI-0.0.74-01 (marker), OBPI-0.0.74-02 (shared checkpoint), OBPI-0.0.74-03 (gate5_invariants) — the mechanism this OBPI consumes

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/checkpoint.py` exists (OBPI-0.0.74-02 has landed)
- [ ] The MX marker mechanism (OBPI-0.0.74-01) has landed
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
- [ ] Relevant docs updated (no operator-facing surface contract changes — the two `gz validate` scopes keep their names and exit semantics; only the severity *source* generalizes)

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
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
uv run gz validate --qc-binding
test -f src/gzkit/governance/trust_audits/rendition_freshness.py
test -f src/gzkit/governance/trust_audits/rendition_floor_coherence.py
test -f src/gzkit/mx/checkpoint.py
```

## Demo

```bash
# The two hand-set staging hacks are gone; severity is the marker's job now.
# Outside the hangar both gates run at full strength:
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
# Their negative controls still flag when forced hard — the gates genuinely bind:
uv run gz validate --qc-binding
```

## Acceptance Criteria

- [ ] REQ-0.0.74-09-01 [behavior]: Given the rendition-freshness and rendition-floor-coherence gates, when the OBPI lands, then `_FRESHNESS_FAIL_CLOSED` and `_FLOOR_FAIL_CLOSED` are deleted and both gates resolve their effective severity through the one shared checkpoint (`src/gzkit/mx/checkpoint.py`) — advisory inside the hangar, full strength outside. (@covers tests in `tests/governance/test_rendition_freshness.py` and `tests/governance/test_rendition_floor_coherence.py`)
- [ ] REQ-0.0.74-09-02 [behavior]: Given the two gates' negative controls (`_rendition_freshness_negative_control`, `_rendition_floor_coherence_negative_control`), when each is forced hard (`fail_closed=True`), then it still flags its planted fixture — the gates genuinely bind after the rewire. (@covers test in `tests/governance/test_rendition_freshness.py` / `tests/governance/test_rendition_floor_coherence.py`)
- [ ] REQ-0.0.74-09-03 [structural-fence]: No per-gate hand-set staging flag remains anywhere in the codebase; the shared checkpoint is the single severity authority for every relaxable guard (parent ADR § Boundary Invariants — "the checkpoint is the single severity authority", audited at ADR closeout).

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

Before: two gates each carried a hand-set `_*_FAIL_CLOSED` module constant — the exact per-gate, memory-dependent staging hack the parent ADR's alternative (b) rejects (N forget-sites, N hand-rolled checks). Now: both gates ask the one shared checkpoint for their severity, so the hangar marker (advisory in the bay, full strength at the door) governs them the same way it governs every other relaxable guard — one home, no per-gate flag to forget or forge.

### Key Proof

### Implementation Summary

- **Decision item 9 (verbatim):** "Retire the two hand-set staging flags. Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their severity through the one marker mechanism (the honest generalization of the two hacks)."
- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- Parent-ADR dependency (tracked here per AGENTS.md § PRIME DIRECTIVE #6, brief evidence section — no GHI): REQ-0.0.74-09-03 [structural-fence] proves against a `## Boundary Invariants` entry in ADR-0.0.74 ("the checkpoint is the single severity authority"). That entry is authored when the ADR package is built out; it is outside this brief's two-file authoring scope.
- Sequencing dependency: the shared checkpoint (`src/gzkit/mx/checkpoint.py`, OBPI-0.0.74-02) and the marker (OBPI-0.0.74-01) MUST land before this OBPI; this brief consumes them as the single severity authority.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
