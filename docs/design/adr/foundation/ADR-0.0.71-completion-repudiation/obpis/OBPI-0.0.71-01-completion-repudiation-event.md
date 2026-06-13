---
id: OBPI-0.0.71-01-completion-repudiation-event
parent: ADR-0.0.71-completion-repudiation
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.71-01-completion-repudiation-event: Completion Repudiation Event

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`
- **Checklist Item:** #1 - "`obpi_completion_repudiated` ledger event model + factory + `ledger.json` schema entry + state-resolution semantics (flip ledger_completed, set repudiated, NOT withdrawn; genuine re-completion clears repudiated); unit tests"

**Status:** Draft

## Objective

Deliver the `obpi_completion_repudiated` ledger event (Pydantic model + factory + `ledger.json` schema) and its graph state-resolution semantics: applying it flips a completed OBPI back to live (`ledger_completed=False`, `repudiated=True`) without the sticky `withdrawn` retirement, and a later genuine completion clears it — all proven by TDD unit tests. This is the engine layer; the `repudiate` CLI verb is OBPI-02.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/events.py` — NEW `ObpiCompletionRepudiatedEvent` Pydantic model
- `src/gzkit/ledger_events.py` — NEW `obpi_completion_repudiated_event(...)` factory
- `src/gzkit/ledger.py` — NEW `_apply_obpi_completion_repudiated_metadata` + wiring into `_apply_graph_event_metadata`
- `src/gzkit/schemas/ledger.json` — NEW `obpi_completion_repudiated` event schema entry
- `tests/test_completion_repudiation.py` **CREATE** — NEW: unit tests for model + state-resolution
- `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/obpis/OBPI-0.0.71-01-completion-repudiation-event.md` — this brief (evidence recording)
- `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md` — parent ADR (read-only, for intent)

> The `repudiate` CLI verb, its parser, manpage, behave smoke, and the
> AGENTS.md disambiguation are OUT OF SCOPE here — they are OBPI-0.0.71-02.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The `ObpiCompletionRepudiatedEvent` model MUST carry `obpi_id`, `repudiated_receipt`, `cause`, `attestor`, `reason`, `ts`; `attestor` and `reason` MUST be non-empty (Pydantic `min_length=1`) so an empty repudiation fails closed at construction (parent ADR Boundary Invariant 1).
1. REQUIREMENT: `cause` MUST be a closed enum — `model-induced-fabrication`, `operator-error`, `verification-invalid` — rejecting any other value (parent ADR Boundary Invariant 4).
1. REQUIREMENT: Applying an `obpi_completion_repudiated` event MUST set `ledger_completed=False` and `repudiated=True` (+ `repudiated_reason`) on the OBPI node, and MUST NEVER set `withdrawn` (parent ADR Boundary Invariant 2).
1. REQUIREMENT: A subsequent genuine `obpi_receipt_emitted` (completed/attested_completed) for the same OBPI MUST clear `repudiated` and re-complete the node; no other event clears it (parent ADR Boundary Invariant 5).
1. REQUIREMENT: A repudiated (not withdrawn) OBPI MUST remain visible in the default `gz state` graph — repudiation reverses, it does not retire.
1. NEVER: mutate or delete the prior `obpi_receipt_emitted` event; the append-only ledger is preserved and the repudiation is additive counter-evidence (parent ADR Boundary Invariant 3).
1. REQUIREMENT: The module surface MUST import stdlib + Pydantic only (no new third-party dependency).
1. ALWAYS: TDD (RED→GREEN) — tests derive from these REQ semantics, not from a run of the code.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/**`
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
uv run -m unittest tests.test_completion_repudiation -v
uv run gz validate --documents
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The event + state-resolution proven at the model layer (the CLI verb is OBPI-02):
uv run -m unittest tests.test_completion_repudiation -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.71-01-01 [behavior]: Given a construction of `ObpiCompletionRepudiatedEvent` with an empty `attestor` or empty `reason`, when the model is built, then it raises a validation error (empty repudiation fails closed). (@covers test)
- [ ] REQ-0.0.71-01-02 [behavior]: Given a `cause` value outside `{model-induced-fabrication, operator-error, verification-invalid}`, when the model is built, then it raises a validation error. (@covers test)
- [ ] REQ-0.0.71-01-03 [behavior]: Given a completed OBPI node and an `obpi_completion_repudiated` event applied over it, when the graph is resolved, then `ledger_completed` is False, `repudiated` is True with the reason, and `withdrawn` is unset. (@covers test)
- [ ] REQ-0.0.71-01-04 [behavior]: Given a repudiated OBPI node and a subsequent genuine `obpi_receipt_emitted` (attested_completed) for the same id, when the graph is resolved, then `repudiated` is cleared and `ledger_completed` is True. (@covers test)
- [ ] REQ-0.0.71-01-05 [behavior]: Given a repudiated (not withdrawn) OBPI, when the default `gz state` graph is built, then the OBPI is present (visible), unlike a withdrawn OBPI which is hidden. (@covers test)
- [ ] REQ-0.0.71-01-06 [support]: The `obpi_completion_repudiated` event schema entry lands in `src/gzkit/schemas/ledger.json` and the model round-trips (serialize → schema-validate → deserialize). Proof: `gz validate --documents` exit 0 + the `artifact_edited` ledger event for `ledger.json`.

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
