---
id: OBPI-0.37.0-04-transit-trailer-stamp
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 4
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-04-transit-trailer-stamp.md
  - .gzkit/hooks/prepare-commit-msg-task-trailers
  - src/gzkit/tasks.py
  - src/gzkit/commands/validate_commit_trailers.py
  - tests/test_transit_trailer.py
reqs:
  - REQ-0.37.0-04-01
  - REQ-0.37.0-04-02
  - REQ-0.37.0-04-03
  - REQ-0.37.0-04-04
verification:
  - uv run -m unittest tests.test_transit_trailer -q
---

# OBPI-0.37.0-04-transit-trailer-stamp: Transit Trailer Stamp

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #4 - "OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it; carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today); carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today)"

**Status:** Draft

## Objective

OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it; carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today); carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-04-transit-trailer-stamp.md` — this brief
- `.gzkit/hooks/prepare-commit-msg-task-trailers` — the producer that already stamps `Task:`; gains the `Transit:` stamp
- `src/gzkit/tasks.py` — trailer parsing and the `src/`+`tests/` scope roots the `Task:` floor already uses
- `src/gzkit/commands/validate_commit_trailers.py` — the validator surface that warns on a missing trailer
- `tests/test_transit_trailer.py` — new covering tests (flat convention) **CREATE**
## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** pull edges for this brief are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The scaffold carried the parent ADR and a `…/**` glob in its allowlist; removed 2026-08-15.)
- Flipping the trailer gate fail-closed — OBPI-06 owns that, gated on § Flip Criteria gate 2, whose (b) conjunct is this OBPI's recovery path.
- `gz git-sync` — exempt unconditionally (parent ADR § Boundary Invariants #5, standing operator ruling).
- Widening or altering the existing `Task:` trailer invariant — `Transit:` is a separate key alongside it, never a replacement.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it; carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today); carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today).
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

- [ ] Allowed Path resolves on disk before implementation begins: `.gzkit/hooks/prepare-commit-msg-task-trailers`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/tasks.py`
- [ ] Allowed Path resolves on disk before implementation begins: `src/gzkit/commands/validate_commit_trailers.py`
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
uv run -m unittest tests.test_transit_trailer -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# A src/** commit now carries a door-stamped Transit: trailer alongside Task:.
git log -1 --format=%B -- src/

# The validator warns (does not yet refuse) on a src/** commit with no transit.
uv run gz validate --commit-trailers
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-04-01 [BEHAVIOR]: Given a commit touching `src/**` or `tests/**` and a transit recorded for the working session, when the commit message is prepared, then a `Transit:` trailer is stamped by the producer — never asked of the author. Scope matches the existing `Task:` floor exactly; an authored `Transit:` trailer of any form suppresses the stamp, as `Task:` does.
- [ ] REQ-0.37.0-04-02 [BEHAVIOR]: Given a `src/**` or `tests/**` commit carrying no `Transit:` trailer, when `gz validate --commit-trailers` runs, then it WARNS and exits 0. Fail-closed is OBPI-06's, not this increment's.
- [ ] REQ-0.37.0-04-03 [BEHAVIOR]: Given a stamping failure, when the operator inspects the result, then the failure is visible and recoverable WITHOUT the operator needing to know a transit id. Derived from the parent ADR § Negative #5: the producer's every failure path is a silent no-op — correct for an advisory trailer, and stranding under a fail-closed consumer. This REQ is the (b) conjunct § Flip Criteria gate 2 will not flip without.
- [ ] REQ-0.37.0-04-04 [STRUCTURAL-FENCE]: `gz git-sync` is never gated, warned, or refused by the trailer mechanism. Proof channel is the parent ADR's `## Boundary Invariants` #5, which names OBPI-04; audited at ADR closeout.
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
