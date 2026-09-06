---
id: OBPI-0.37.0-03-seam-accounting-predicate
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 3
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-03-seam-accounting-predicate.md
  - src/gzkit/airlock/enter.py
  - src/gzkit/airlock/model.py
  - src/gzkit/events.py
  - src/gzkit/schemas/ledger.json
  - tests/test_airlock_severity_ladder.py
  - tests/test_airlock_events.py
reqs:
  - REQ-0.37.0-03-01
  - REQ-0.37.0-03-02
  - REQ-0.37.0-03-03
  - REQ-0.37.0-03-04
verification:
  - uv run -m unittest tests.test_airlock_severity_ladder -q
---

# OBPI-0.37.0-03-seam-accounting-predicate: Seam Accounting Predicate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #3 - "OBPI-0.37.0-03 seam-accounting-predicate -- the graduated severity ladder: unaccounted law WARNs (pending the § Flip Criteria threshold), a parent declaring NO `## Boundary Invariants` section PROCEEDs and emits a counted L2 warning naming the gap; plus override-frequency tracking, so Negative #1's mitigation has an owner"

**Status:** Draft

## Objective

OBPI-0.37.0-03 seam-accounting-predicate -- the graduated severity ladder: unaccounted law WARNs (pending the § Flip Criteria threshold), a parent declaring NO `## Boundary Invariants` section PROCEEDs and emits a counted L2 warning naming the gap; plus override-frequency tracking, so Negative #1's mitigation has an owner.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-03-seam-accounting-predicate.md` — this brief
- `src/gzkit/airlock/enter.py` — `_decide` (:154-166) and the warning channel ONLY — the accounting predicate in `_reconcile` belongs to OBPI-02.
- `src/gzkit/airlock/model.py` — severity/warning fields on the seam-map or preflight snapshot
- `src/gzkit/events.py` — the `airlock_in` event carries the law-absent warning and the override signal
- `src/gzkit/schemas/ledger.json` — L2 schema for the same
- `tests/test_airlock_severity_ladder.py` — new covering tests (flat convention) **CREATE**
- `tests/test_airlock_events.py` — existing airlock event tests
## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** pull edges for this brief are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The scaffold carried the parent ADR and a `…/**` glob in its allowlist; removed 2026-08-15.)
- `src/gzkit/airlock/enter.py::_reconcile` (:116-151) — the accounting predicate is OBPI-02's. This OBPI changes what an unaccounted edge DOES, never what `accounted` MEANS.
- Flipping either gate fail-closed — that is OBPI-06, gated on § Flip Criteria. This OBPI ships the ladder in its WARN posture.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-03 seam-accounting-predicate -- the graduated severity ladder: unaccounted law WARNs (pending the § Flip Criteria threshold), a parent declaring NO `## Boundary Invariants` section PROCEEDs and emits a counted L2 warning naming the gap; plus override-frequency tracking, so Negative #1's mitigation has an owner.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/airlock/enter.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/airlock/model.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/events.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/schemas/ledger.json`
- [ ] Parent ADR § Boundary Invariants parses and each invariant carries an `(OBPI-NN)` binding token
- [ ] Parent ADR § Flip Criteria baselines re-measured rather than transcribed from this brief
**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_airlock_severity_ladder -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Parent declares law, an invariant is unaccounted: WARNs, does not yet HOLD.
uv run gz airlock in --target OBPI-0.37.0-06-transit-gate-flip --dry-run --json

# Parent declares NO Boundary Invariants section: proceeds, and the gap is
# COUNTED rather than invisible. 147 of 166 ADRs are in this state today.
uv run gz airlock in --target OBPI-0.30.0-01-okf-inventory-and-classification --dry-run --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-03-01 [BEHAVIOR]: Given a parent ADR that DECLARES `## Boundary Invariants` and an entry with at least one unaccounted invariant, when the gate decides, then the outcome is a WARNING and the transit proceeds — it does not HOLD. Derived from the ADR's § Flip Criteria, not from convenience: modelled across the 19 law-declaring ADRs, 89 of 93 entries carry at least one unaccounted invariant, so shipping HOLD would put ~95% of entries at NO-GO on day one and make CaptainOverride the default verb — parent ADR § Negative #1 by construction.
- [ ] REQ-0.37.0-03-02 [BEHAVIOR]: Given a parent ADR that declares NO `## Boundary Invariants` section, when the gate decides, then the transit PROCEEDS and a warning naming the missing-law gap is emitted. Holding here instead would put ~88% of the corpus (147 of 166 ADRs) at NO-GO for a condition the entering work cannot fix from inside the entry.
- [ ] REQ-0.37.0-03-03 [SUPPORT]: The `airlock_in` L2 event and `src/gzkit/schemas/ledger.json` carry the law-absent warning and the override signal, so both are countable from the ledger rather than from agent narrative. Witnessed by `airlock_in` citing `src/gzkit/schemas/ledger.json` + `gz validate --documents`.
- [ ] REQ-0.37.0-03-04 [BEHAVIOR]: Given a CaptainOverride on an airlock entry, when the transit is booked, then the override is recorded such that its FREQUENCY is queryable from L2. This closes the parent ADR § Negative #1 mitigation (*'override frequency is a tracked signal rather than a free escape'*), which was asserted in Consequences with no owning checklist item until the 2026-08-15 amendment.
## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
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

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
