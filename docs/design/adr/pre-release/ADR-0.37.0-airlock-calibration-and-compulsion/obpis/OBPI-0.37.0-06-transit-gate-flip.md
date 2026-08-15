---
id: OBPI-0.37.0-06-transit-gate-flip
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 6
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-06-transit-gate-flip.md
  - src/gzkit/airlock/enter.py
  - src/gzkit/commands/validate_commit_trailers.py
  - tests/test_transit_gate_flip.py
reqs:
  - REQ-0.37.0-06-01
  - REQ-0.37.0-06-02
  - REQ-0.37.0-06-03
verification:
  - uv run -m unittest tests.test_transit_gate_flip -q
---

# OBPI-0.37.0-06-transit-gate-flip: Transit Gate Flip

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #6 - "OBPI-0.37.0-06 transit-gate-flip -- flip items 3 and 4 fail-closed against § Flip Criteria; live NC asserts un-triggered entry makes the claim fail"

**Status:** Draft

## Objective

OBPI-0.37.0-06 transit-gate-flip -- flip items 3 and 4 fail-closed against § Flip Criteria; live NC asserts un-triggered entry makes the claim fail.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-06-transit-gate-flip.md` — this brief
- `src/gzkit/airlock/enter.py` — the severity flag OBPI-03 shipped in its WARN posture
- `src/gzkit/commands/validate_commit_trailers.py` — the trailer gate's warn/refuse posture
- `tests/test_transit_gate_flip.py` — new covering tests, including the live negative control **CREATE**
## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** pull edges for this brief are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The scaffold carried the parent ADR and a `…/**` glob in its allowlist; removed 2026-08-15.)
- Flipping either gate before its § Flip Criteria threshold is MEASURED and met. A flip proposed on elapsed time, on a count of landed OBPIs, or on a judgment that the corpus 'looks ready' is the defect § Flip Criteria exists to prevent.
- Re-deriving or re-negotiating the thresholds. They are written in the parent ADR with measured baselines; this OBPI reads them.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-06 transit-gate-flip -- flip items 3 and 4 fail-closed against § Flip Criteria; live NC asserts un-triggered entry makes the claim fail.
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
uv run -m unittest tests.test_transit_gate_flip -q
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Both gates are fail-closed: an unaccounted invariant now blocks the crossing.
uv run gz airlock in --target OBPI-0.37.0-06-transit-gate-flip --dry-run --json

# And a src/** commit with no transit is refused rather than warned.
uv run gz validate --commit-trailers
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-06-01 [BEHAVIOR]: Given the § Flip Criteria gate-1 threshold is met — the modeled would-hold rate across law-declaring ADRs below 25%, against the measured 2026-08-15 baseline of 95% (89 of 93 entries) — when the pull-arm severity flips, then an unaccounted invariant makes PROCEED unreachable on the default path. Before the threshold is met the flip does not land; the criterion is read from the parent ADR, never re-derived here.
- [ ] REQ-0.37.0-06-02 [BEHAVIOR]: Given § Flip Criteria gate 2 — ≥90% of `src/**` and `tests/**` commits in a trailing 30-day window carrying a door-stamped `Transit:` trailer, AND OBPI-04's stamp-failure recovery path landed and exercised — when the trailer gate flips, then a commit with no transit is refused. The conjunction is binding: flipping on the percentage alone converts a silent producer failure into an unrecoverable commit refusal.
- [ ] REQ-0.37.0-06-03 [BEHAVIOR]: Given a unit of work that never entered a door at all, when the flipped gate evaluates it, then the claim FAILS. This is the live negative control and it targets the failure the parent ADR was written for — not 'un-accounted seam → GO unreachable' (that is ADR-0.33.0's existing NC, which only fires once you are already inside the airlock) but NEVER ENTERING, the mode that let 525 fix commits through in 90 days across zero transits.
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
