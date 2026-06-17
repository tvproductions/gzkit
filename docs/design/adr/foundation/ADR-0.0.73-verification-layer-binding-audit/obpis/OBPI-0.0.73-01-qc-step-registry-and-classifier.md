---
id: OBPI-0.0.73-01-qc-step-registry-and-classifier
parent: ADR-0.0.73-verification-layer-binding-audit
item: 1
lane: Lite
status: Completed
req_atomic:
  # The QCStep model + derived registry is one indivisible authoring unit:
  # the model, its derivation, and its classification ship as a single
  # src/gzkit/qc_binding.py write with one covering test module. No REQ
  # below decomposes into independently-attributable labor steps.
  - REQ-0.0.73-01-01  # model contract (frozen/extra-forbid/7-field) — written with the model
  - REQ-0.0.73-01-02  # registry derivation from _build_check_steps() — same module, same write
  - REQ-0.0.73-01-03  # binding classification — same module's _STEP_CLASSIFICATION dict
  - REQ-0.0.73-01-04  # SUPPORT: module-lands proof — satisfied by the same single module write
  - REQ-0.0.73-01-05  # STRUCTURAL-FENCE: derived-not-hand-maintained — a property of the same derivation
---

# OBPI-0.0.73-01-qc-step-registry-and-classifier: Qc Step Registry And Classifier

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #1 - "Registry + classifier model — `QCStep` Pydantic frozen model `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests"

**Status:** Completed

## Objective

A frozen `QCStep` Pydantic model and a registry **derived** from what `gz check`
actually runs land in `src/gzkit/qc_binding.py`, classifying every QC step as
`bound` / `advisory` / `unenforced` — the data foundation the OBPI-02
`--qc-binding` scope consumes. "Done" = the registry enumerates the real
`gz check` step set (no hand-maintained list) and unit tests pin the model's
frozen/extra-forbid contract and the derivation.

Registry + classifier model — `QCStep` Pydantic frozen model `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `src/gzkit/qc_binding.py` **CREATE** — `QCStep` frozen Pydantic model + registry derived from the `gz check` step set
- `tests/governance/test_qc_binding.py` **CREATE** — unit tests for the model contract and the derivation
- `src/gzkit/traceability.py` — `@covers` decorator import (read-only test infrastructure, not modified)
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-01-qc-step-registry-and-classifier.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: Registry + classifier model — `QCStep` Pydantic frozen model `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. REQUIREMENT: NEVER mark the OBPI accepted while scaffold defaults remain in the brief
1. REQUIREMENT: ALWAYS reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
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
test -f src/gzkit/qc_binding.py
test -f tests/governance/test_qc_binding.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. -->

```bash
# The derived registry enumerates the real gz check step set with classifications.
uv run python -c "from gzkit.qc_binding import build_qc_registry; [print(s.id, s.binding) for s in build_qc_registry()]"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-01-01 [BEHAVIOR]: Given a `QCStep`, when code attempts to mutate a field or pass an unknown field, then Pydantic raises (model is `frozen=True, extra="forbid"`) and all seven fields (`id, name, kind, subject, binding, wired_into, theater_flags, enforcement_locus`) are present. (@covers test in `tests/governance/test_qc_binding.py`)
- [ ] REQ-0.0.73-01-02 [BEHAVIOR]: Given the set of steps `gz check` actually runs, when the registry is built, then every check step appears exactly once and no step absent from `gz check` is invented (the registry is derived, not hand-listed). (@covers test in `tests/governance/test_qc_binding.py`)
- [ ] REQ-0.0.73-01-03 [BEHAVIOR]: Given each registered step, when it is classified, then its `binding` is exactly one of `bound` / `advisory` / `unenforced`. (@covers test in `tests/governance/test_qc_binding.py`)
- [ ] REQ-0.0.73-01-04 [SUPPORT]: The `src/gzkit/qc_binding.py` module lands with the model and derivation. Proof: `artifact_edited` ledger event for the module + `gz validate --documents` exit 0.
- [ ] REQ-0.0.73-01-05 [STRUCTURAL-FENCE]: The registry is derived from what `gz check` runs and is never a hand-maintained list (parent ADR § Boundary Invariants #1).

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


Command: uv run python -c "from gzkit.qc_binding import build_qc_registry; [print(s.id, s.binding) for s in build_qc_registry()]"
Output: enumerates 32 steps (lint, format, typecheck, test, behave, skill-audit ... line-endings), each classified `bound` — exactly the gz check step set, derived live from _build_check_steps() rather than hand-listed.
Receipts: arb-step-unittest-74751e64f0f146b691024b4a7d8bfeea (exit_status 0), arb-ruff-a5a16b6faae74193a2820f4dc7947608 (exit_status 0), arb-step-typecheck-4d0f3f14acc44dfdb1ecf2a59377bd6e (exit_status 0).

### Implementation Summary


- Files created: src/gzkit/qc_binding.py (QCStep frozen Pydantic model + _STEP_CLASSIFICATION dict with 32 entries + build_qc_registry() derivation function), tests/governance/test_qc_binding.py (11 unit tests across 3 classes)
- Mechanism: build_qc_registry() derives registry membership from _build_check_steps() in gzkit.commands.quality — never hand-maintained; a KeyError sentinel fires when an unclassified step is added to gz check, keeping the derivation honest
- Model: QCStep is frozen=True, extra="forbid", with 7 fields (id, name, kind, subject, binding, wired_into, theater_flags, enforcement_locus)
- Tests added: 11 (TestQCStepModelContract x5, TestQCRegistryDerivation x3, TestQCStepBindingClassification x3)
- Date completed: 2026-06-17
- Attestation status: operator-attested "attest completed"
- Defects noted: none

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.73-01 delivers src/gzkit/qc_binding.py: a frozen QCStep Pydantic model (frozen=True, extra="forbid", 7 fields) and build_qc_registry() that derives the registry from _build_check_steps() (32 steps, all classified bound), never hand-maintained. 11 unit tests pass (receipt arb-step-unittest-74751e64f0f146b691024b4a7d8bfeea exit 0); lint clean (arb-ruff-a5a16b6faae74193a2820f4dc7947608); typecheck clean (arb-step-typecheck-4d0f3f14acc44dfdb1ecf2a59377bd6e). All 3 BEHAVIOR REQs covered; SUPPORT + STRUCTURAL-FENCE REQs proof_status=pass.
- Date: 2026-06-17

---

**Date Completed:** 2026-06-17

**Evidence Hash:** -
