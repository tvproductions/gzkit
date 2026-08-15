---
id: OBPI-0.37.0-01-ontology-inverse-reach
parent: ADR-0.37.0-airlock-calibration-and-compulsion
item: 1
lane: Heavy
status: Draft
allowlist:
  - docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-01-ontology-inverse-reach.md
  - src/gzkit/airlock/enter.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/commands/airlock.py
  - src/gzkit/commands/mx_cmd.py
  - src/gzkit/commands/permitted_entry.py
  - tests/test_airlock_parent_invariants.py
  - tests/test_airlock_enter.py
reqs:
  - REQ-0.37.0-01-01
  - REQ-0.37.0-01-02
  - REQ-0.37.0-01-03
verification:
  - uv run -m unittest tests.test_airlock_parent_invariants -q
---

# OBPI-0.37.0-01-ontology-inverse-reach: Ontology Inverse Reach

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- **Checklist Item:** #1 - "OBPI-0.37.0-01 ontology-inverse-reach -- thread parent_invariants from the parent ADR's `## Boundary Invariants` through all FIVE airlock_enter call sites, including commands/airlock.py:95 (the door `gz airlock in` uses, omitted from the original "all four"); the element is one numbered invariant, identified by its (OBPI-NN) binding token, never its prose"

**Status:** Draft

## Objective

OBPI-0.37.0-01 ontology-inverse-reach -- thread parent_invariants from the parent ADR's `## Boundary Invariants` through all FIVE airlock_enter call sites, including commands/airlock.py:95 (the door `gz airlock in` uses, omitted from the original "all four"); the element is one numbered invariant, identified by its (OBPI-NN) binding token, never its prose.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-01-ontology-inverse-reach.md` — this brief
- `src/gzkit/airlock/enter.py` — `airlock_enter` signature and `_reconcile`'s pull-edge construction
- `src/gzkit/pipeline_runtime.py` — call sites at `:590` and `:592`
- `src/gzkit/commands/airlock.py` — call site at `:95`, the door `gz airlock in` uses (the omitted fifth)
- `src/gzkit/commands/mx_cmd.py` — call site at `:108`
- `src/gzkit/commands/permitted_entry.py` — call site at `:243`
- `tests/test_airlock_parent_invariants.py` — new covering tests for the threading (flat `tests/test_airlock_*.py` convention, matching test_airlock_enter/exit/model/events) **CREATE**
- `tests/test_airlock_enter.py` — existing enter tests, updated for the new signature usage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **`docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md` — the parent ADR. BINDING, parent ADR § Boundary Invariants #9:** this brief's pull edges are computed FROM that file's `## Boundary Invariants` section, so write access would let this OBPI grant itself accounting. Read it; never edit it. (The brief carried the parent ADR and a `…/**` glob in its allowlist at authoring; removed 2026-08-15.)
- `src/gzkit/airlock/exit.py` — carries the identical empty-`parent_invariants` defect but is NOT scoped here; tracked separately
- `src/gzkit/req_kind_fence.py` — `_fence_obpi_anchored` is REUSED UNCHANGED by OBPI-02; this OBPI does not modify it
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: OBPI-0.37.0-01 ontology-inverse-reach -- thread parent_invariants from the parent ADR's `## Boundary Invariants` through all FIVE airlock_enter call sites, including commands/airlock.py:95 (the door `gz airlock in` uses, omitted from the original "all four"); the element is one numbered invariant, identified by its (OBPI-NN) binding token, never its prose.
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

- [ ] All FIVE `airlock_enter` call sites still resolve — re-derive rather than trust this list: `grep -rn "airlock_enter(" src/ | grep -v "def airlock_enter"`
- [ ] `src/gzkit/airlock/enter.py` `airlock_enter` still accepts `parent_invariants: tuple[str, ...] = ()`
- [ ] Parent ADR § Boundary Invariants section parses and each invariant carries an `(OBPI-NN)` binding token
- [ ] Parent ADR evidence artifacts referenced by this brief are present

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
uv run -m unittest tests.test_airlock_parent_invariants -q
```

> **The scaffold's `test -f <the parent ADR>` was removed 2026-08-15.** It was true
> before any work began, so it could never fail and the pipeline verify stage would
> have passed vacuously. A verification command that cannot go RED is not a
> verification command.

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The observing door now carries LAW. Before this OBPI this printed "pull": []
uv run gz airlock in --target OBPI-0.37.0-02-airlock-seam-calibration --dry-run --json

# The same door under a parent that declares NO Boundary Invariants — pull is
# legitimately empty here, and OBPI-03 is what makes that state visible.
uv run gz airlock in --target OBPI-0.30.0-01-okf-inventory-and-classification --dry-run --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.37.0-01-01 [BEHAVIOR]: Given an OBPI whose parent ADR declares a `## Boundary Invariants` section, when `airlock_enter` is invoked through ANY of the five call sites — `pipeline_runtime.py` (both), `commands/permitted_entry.py`, `commands/mx_cmd.py`, and `commands/airlock.py` — then the resulting `SeamMap.pull_edges` carries one edge per numbered invariant. **The fifth site is the REQ's point:** a threading that covers only the four sites named in the ADR's original text leaves `gz airlock in` reporting `pull: []`, so the test asserts the invariant across all five, enumerated from source rather than from a hardcoded list.
- [ ] REQ-0.37.0-01-02 [BEHAVIOR]: Given a parent ADR whose invariants are multi-line prose paragraphs, when pull edges are constructed, then each `SeamEdge.target` carries the invariant's `(OBPI-NN)` binding identity and NEVER the paragraph text. Rationale the assertion derives from, not from a run: `SeamEdge.target` is persisted to the L2 ledger, and ADR-0.33.0's invariants run to five lines including verbatim operator quotes — carrying prose there would put paragraphs in the append-only record and make an entry's identity unstable under any prose edit.
- [ ] REQ-0.37.0-01-03 [STRUCTURAL-FENCE]: This OBPI never acquires write access to its own parent ADR. Proof channel is the parent ADR's `## Boundary Invariants` #9 (*"No OBPI may hold write access to the ADR that grants its accounting"*), which names OBPI-01; audited at ADR closeout, not by a per-OBPI test.

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
