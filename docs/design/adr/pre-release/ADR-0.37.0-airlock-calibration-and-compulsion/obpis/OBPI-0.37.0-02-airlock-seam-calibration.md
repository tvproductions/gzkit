---
id: OBPI-0.37.0-02-airlock-seam-calibration
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 2
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-02-airlock-seam-calibration.md
  - src/gzkit/airlock/enter.py
  - tests/test_airlock_seam_accounting.py
  - tests/test_airlock_enter.py
reqs:
  - REQ-0.37.0-02-01
  - REQ-0.37.0-02-02
  - REQ-0.37.0-02-03
  - REQ-0.37.0-02-04
verification:
  - uv run -m unittest tests.test_airlock_seam_accounting -q
---

# OBPI-0.37.0-02-airlock-seam-calibration: Airlock Seam Calibration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #2 - "OBPI-0.37.0-02 airlock-seam-calibration -- replace `accounted = inv in brief_text` with the two-arm predicate (parent binds the invariant to this OBPI via `_fence_obpi_anchored`, OR the brief carries a STRUCTURAL-FENCE REQ citing it); live NC asserts the DIFFERENTIAL pair -- accounted entry PROCEEDs, one unaccounted invariant makes GO unreachable -- and that per-entry pull edges never exceed the parent's declared invariant count"

**Status:** Draft

## Objective

OBPI-0.37.0-02 airlock-seam-calibration -- replace `accounted = inv in brief_text` with the two-arm predicate (parent binds the invariant to this OBPI via `_fence_obpi_anchored`, OR the brief carries a STRUCTURAL-FENCE REQ citing it); live NC asserts the DIFFERENTIAL pair -- accounted entry PROCEEDs, one unaccounted invariant makes GO unreachable -- and that per-entry pull edges never exceed the parent's declared invariant count.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-02-airlock-seam-calibration.md` — this brief
- `src/gzkit/airlock/enter.py` — `_reconcile`'s accounting predicate ONLY — the `accounted=` expressions at :136 and :146. `_decide` (:154) belongs to OBPI-03.
- `tests/test_airlock_seam_accounting.py` — new covering tests (flat `tests/test_airlock_*.py` convention) **CREATE**
- `tests/test_airlock_enter.py` — existing enter tests, updated where the predicate changes their expectations
## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** pull edges for this brief are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The scaffold carried the parent ADR and a `…/**` glob in its allowlist; removed 2026-08-15.)
- `src/gzkit/req_kind_fence.py` — `_fence_obpi_anchored` is REUSED UNCHANGED. Modifying it would fork the binding grammar that `gz validate --req-kind-discipline` already reads (parent ADR § Boundary Invariants #2, one primitive).
- `src/gzkit/airlock/enter.py::_decide` (:154-166) — the severity ladder is OBPI-03's. This OBPI changes what `accounted` MEANS, never what an unaccounted edge DOES.
- `src/gzkit/airlock/exit.py` — carries the identical empty-`parent_invariants` defect; explicitly not scoped here.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-02 airlock-seam-calibration -- replace `accounted = inv in brief_text` with the two-arm predicate (parent binds the invariant to this OBPI via `_fence_obpi_anchored`, OR the brief carries a STRUCTURAL-FENCE REQ citing it); live NC asserts the DIFFERENTIAL pair -- accounted entry PROCEEDs, one unaccounted invariant makes GO unreachable -- and that per-entry pull edges never exceed the parent's declared invariant count.
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
uv run -m unittest tests.test_airlock_seam_accounting -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# An entry whose parent BINDS its law to this OBPI: every pull edge accounted.
uv run gz airlock in --target OBPI-0.37.0-02-airlock-seam-calibration --dry-run --json

# Naming an invariant in the brief no longer accounts for it. Before this OBPI a
# brief could clear a seam by pasting the invariant's text; now the parent must
# bind it, or the brief must carry a STRUCTURAL-FENCE REQ citing it.
uv run gz validate --req-kind-discipline
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-02-01 [BEHAVIOR]: Given a pull edge for invariant I on an entry for OBPI N, when accounting is computed, then the edge is `accounted` IFF (a) the parent ADR's `## Boundary Invariants` binds I to N in the `(OBPI-NN)` form `_fence_obpi_anchored` parses, OR (b) N's brief carries a STRUCTURAL-FENCE REQ citing I. The prior `inv in brief_text` substring test is REMOVED, not narrowed — narrowing it to declarative sections leaves the defect, because the defect is direction: under any substring rule the brief accounts for a seam by NAMING it, and the brief is a file the entering agent controls.
- [ ] REQ-0.37.0-02-02 [BEHAVIOR]: Given the same target and the same command, when one invariant is accounted and when one is not, then the two runs differ in `decision` — accounted reaches `proceed`, unaccounted cannot. **The pair is the assertion.** A single non-emptiness check cannot distinguish a gate that bites from a constant that does not: the withdrawn inverse-reach D1 would have produced a non-empty seam-map on every entry and satisfied it.
- [ ] REQ-0.37.0-02-03 [BEHAVIOR]: Given any entry, when the seam-map is computed, then the pull-edge count never exceeds the number of numbered invariants declared by that entry's parent ADR. The bound is STRUCTURAL, derived from the parent's authored list — it is never a tuned constant, and never a threshold read off a run of the code.
- [ ] REQ-0.37.0-02-04 [STRUCTURAL-FENCE]: `_fence_obpi_anchored` is consumed, never forked or reimplemented, so one binding grammar serves both `gz validate --req-kind-discipline` and the airlock. Proof channel is the parent ADR's `## Boundary Invariants` #2 (one primitive; doors CALL and never fork), which names OBPI-02; audited at ADR closeout.
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
