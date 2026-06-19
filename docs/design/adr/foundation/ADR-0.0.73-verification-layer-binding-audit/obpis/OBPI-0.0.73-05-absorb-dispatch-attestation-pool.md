---
id: OBPI-0.0.73-05-absorb-dispatch-attestation-pool
parent: ADR-0.0.73-verification-layer-binding-audit
item: 5
lane: Lite
status: Completed
sensitivity: security
# req_atomic: each REQ is a single indivisible unit. Registering one bound QC
# step (01) — the function, its _build_check_steps() wiring, its
# _STEP_CLASSIFICATION entry, and its test — is one atomic registration. Adding
# the absorption marker to one pool ADR (02) and changing that ADR's status to
# Superseded (03) are single frontmatter edits in the same file. None decomposes
# into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.73-05-01
  - REQ-0.0.73-05-02
  - REQ-0.0.73-05-03
---

# OBPI-0.0.73-05-absorb-dispatch-attestation-pool: Absorb Dispatch Attestation Pool

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #5 - "Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests"

**Status:** Completed

## Objective

The dispatch-attestation concern carried by ADR-pool.obpi-pipeline-dispatch-attestation
is folded into this ADR's bound-checker mechanism (it is the same "checker not
bound" class), and the pool ADR is annotated/retired as absorbed so it no longer
floats as an unpromoted free item. "Done" = the dispatch-attestation enforcement
is a bound QC step the registry classifies, and the pool ADR records its
absorption into ADR-0.0.73.

Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md` — annotate as absorbed-into ADR-0.0.73 (retire the free pool item)
- `src/gzkit/qc_binding.py` **CREATE** — SHARED surface created by OBPI-01 (which lands first); extended here to register the dispatch-attestation enforcement as a bound QC step
- `src/gzkit/quality.py` — add `run_dispatch_attestation_audit` function (the bound enforcement step body)
- `src/gzkit/commands/quality.py` — wire `run_dispatch_attestation_audit` into `_build_check_steps()`; coupled consumer (a new `gz check` step cannot be registered without both the function in `quality.py` and the wiring here)
- `tests/commands/test_skills.py` — add `run_dispatch_attestation_audit` to the `gz check` step mock list; coupled-consumer fix (the step-list mock fails closed when a new step is unmocked)
- `tests/governance/test_dispatch_attestation_absorption.py` **CREATE** — unit tests for the bound dispatch-attestation step
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-05-absorb-dispatch-attestation-pool.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests.
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
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/**`
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
test -f tests/governance/test_dispatch_attestation_absorption.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. -->

```bash
# The dispatch-attestation enforcement is now a bound, classified QC step.
uv run python -c "from gzkit.qc_binding import build_qc_registry; print([s.id for s in build_qc_registry() if 'dispatch' in s.id])"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-05-01 [BEHAVIOR]: Given the OBPI-pipeline dispatch-attestation concern, when the QC registry is built, then the dispatch-attestation enforcement appears as a `bound` QC step (no longer an unpromoted pool intent). (@covers test in `tests/governance/test_dispatch_attestation_absorption.py`)
- [ ] REQ-0.0.73-05-02 [SUPPORT]: The pool ADR `ADR-pool.obpi-pipeline-dispatch-attestation` is annotated as absorbed into ADR-0.0.73. Proof: `gz validate --documents` exit 0 + `artifact_edited` ledger event for `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md`.
- [ ] REQ-0.0.73-05-03 [SUPPORT]: After absorption the pool item no longer floats as a free unpromoted ADR. Proof: `gz validate --adr-status-fresh` exit 0 + `artifact_edited` ledger event recording the absorption.

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


$ python -c "from gzkit.qc_binding import build_qc_registry; print([s.id for s in build_qc_registry() if 'dispatch' in s.id])"
['dispatch-attestation']

The dispatch-attestation concern is now a bound, classified QC step in the registry (kind=audit, binding=bound), enforced by run_dispatch_attestation_audit on every gz check run. ARB receipts: arb-step-unittest-ed0d4d6302d048ba94882b502aeb6d96 (6249+ pass, exit 0), arb-ruff-35d3188b29ce469f8a20df1338be50aa (clean), arb-step-typecheck-fcca3f21c3a048a090d4a3bbe6f2ff4b (clean), arb-step-mkdocs-8f76902c22fe4c4da098d0109ce7dcfd (clean).

### Implementation Summary


- Decision item: Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into ADR-0.0.73's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests.
- Pool ADR docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md: status Pool -> Superseded; absorbed_into: ADR-0.0.73 frontmatter marker added; ## Absorption Note section added to body.
- src/gzkit/quality.py: added run_dispatch_attestation_audit — reads the pool ADR, fails closed (exit 3) when the absorbed_into marker is absent.
- src/gzkit/commands/quality.py: wired ("Dispatch attestation", run_dispatch_attestation_audit) into _build_check_steps().
- src/gzkit/qc_binding.py: classified "Dispatch attestation" as ("audit", "docs/", "bound", "python_function") in _STEP_CLASSIFICATION.
- tests/governance/test_dispatch_attestation_absorption.py: 7 unit tests (registry membership, absorption marker, status, negative controls).
- tests/commands/test_skills.py: added run_dispatch_attestation_audit to the gz check mock step list (coupled-consumer fix).
- Tests added: 7. Date completed: 2026-06-18. Attestation status: operator-verbatim. Defects noted: none.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator Gate-5 verbatim attestation for OBPI-0.0.73-05-absorb-dispatch-attestation-pool. Dispatch-attestation concern folded into ADR-0.0.73 bound-checker registry; pool ADR annotated Superseded with absorbed_into: ADR-0.0.73. Receipts: arb-step-unittest-ed0d4d6302d048ba94882b502aeb6d96 (6249+ pass), arb-ruff-35d3188b29ce469f8a20df1338be50aa, arb-step-typecheck-fcca3f21c3a048a090d4a3bbe6f2ff4b, arb-step-mkdocs-8f76902c22fe4c4da098d0109ce7dcfd (all exit 0). REQ parity uncovered_reqs=0.
- Date: 2026-06-18

---

**Date Completed:** 2026-06-18

**Evidence Hash:** -
