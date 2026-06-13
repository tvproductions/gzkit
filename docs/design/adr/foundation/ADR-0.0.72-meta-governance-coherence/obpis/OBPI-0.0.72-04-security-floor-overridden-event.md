---
id: OBPI-0.0.72-04-security-floor-overridden-event
parent: ADR-0.0.72-meta-governance-coherence
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.72-04-security-floor-overridden-event: Security Floor Overridden Event

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #4 - "ADAPTER: `security_floor_overridden` ledger event — Pydantic event model + factory + ledger.json schema entry; emitted from `gz obpi complete --accept-security-floor` recording obpi_id, overridden surface(s), reason, attestor, ts; unit tests; round-trips clean through the OBPI-01 validator; census query surfaces the override."

**Status:** Draft

## Objective

A first-class `security_floor_overridden` ledger event is emitted whenever
`gz obpi complete --accept-security-floor` fires, recording the `obpi_id`, the
overridden security surface(s), the operator `reason`, the `attestor`, and a
`ts`. This makes an operator override of the completion-state-editing security
floor auditable via ledger census — closing the invisible-override hole the
OBPI-0.0.71-01 override exposed — and the new event round-trips clean through
the model↔schema alignment surface the OBPI-01 round-trip validator consumes.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/events.py` — new `SecurityFloorOverriddenEvent` Pydantic model (subclass `_EventBase`, `event: Literal["security_floor_overridden"]`, required string fields via `Field(..., min_length=1)`); add it to the `TypedLedgerEvent` discriminated union
- `src/gzkit/ledger_events.py` — new `security_floor_overridden_event(...)` factory mirroring `obpi_completion_repudiated_event`
- `src/gzkit/schemas/ledger.json` — new `security_floor_overridden` entry under `events` (required list + properties with `min_length`/enum constraints)
- `src/gzkit/commands/obpi_complete.py` — emit the event from the `--accept-security-floor` override branch (the `if accept_security_floor and effective_sensitivity == "security":` block, ~line 1031)
- `tests/test_schemas.py` — register the model in the `_EVENT_MODELS` model↔schema alignment map
- `tests/test_security_floor_overridden.py` — **CREATE** new unit test for the model, factory, emission, and census
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR package line (checklist item #4 reconciliation)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- Any existing event model, factory, or `ledger.json` event entry (this change is additive only — never mutate a sibling event)
- The `--accept-security-floor` gate semantics in `_enforce_security_review_gate` (the override stays operator-sovereign; only the audit event is added)
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: `SecurityFloorOverriddenEvent` required string fields (`obpi_id`, `surfaces`, `reason`, `attestor`) use `Field(..., min_length=1)` so an empty value fails closed at model construction — no override may be recorded with a blank reason or attestor.
2. NEVER: mutate, rename, re-type, or reorder any existing event model, factory, or `ledger.json` event entry. The model, factory, schema entry, and union membership land additively, exactly mirroring the `obpi_completion_repudiated` shape (ADR-0.0.71).
3. ALWAYS: emit the event exactly when `gz obpi complete --accept-security-floor` fires and the security floor is actually overridden (the `effective_sensitivity == "security"` downgrade branch). NEVER emit it on a normal completion that did not override the floor.
4. ALWAYS: the emission is additive and best-effort-after-completion within the existing receipt transaction; a failed emission is a defect to fix, NEVER a new gate on the override itself — the override remains operator-sovereign (ADR-0.0.72 § Consequences, 2am-operator scenario).
5. ALWAYS: stdlib + Pydantic only; no new runtime dependency is introduced.
6. ALWAYS: follow TDD — the failing unit test in `tests/test_security_floor_overridden.py` is authored and observed red before the model/factory/schema/emission implementation makes it green.
7. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
8. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/**`
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
uv run gz validate --documents
uv run -m unittest tests.test_security_floor_overridden -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Emit-then-census: run the new unit test that exercises the full path
# (model construction, factory, --accept-security-floor emission, census).
uv run -m unittest tests.test_security_floor_overridden -v

# After a real override, the event is visible to a ledger census grep:
uv run python -c "import json,pathlib; print(sum(1 for l in pathlib.Path('.gzkit/ledger.jsonl').read_text(encoding='utf-8').splitlines() if l.strip() and json.loads(l).get('event')=='security_floor_overridden'))"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.72-04-01 [BEHAVIOR]: Given a `SecurityFloorOverriddenEvent`, when it is constructed, then it carries `obpi_id`, `surfaces`, `reason`, `attestor`, and `ts`, and constructing it with any empty required string field raises a Pydantic `ValidationError` (fail-closed via `min_length=1`). (@covers test)
- [ ] REQ-0.0.72-04-02 [BEHAVIOR]: Given a security-floor brief, when `gz obpi complete --accept-security-floor` fires, then exactly one `security_floor_overridden` ledger event is emitted recording the override `reason`, `attestor`, and overridden `surfaces`, and no such event is emitted on a normal completion. (@covers test)
- [ ] REQ-0.0.72-04-03 [BEHAVIOR]: Given the event has been emitted, when a ledger census counts `security_floor_overridden` events, then the override surfaces (lifetime count increments from 0 to 1). (@covers test)
- [ ] REQ-0.0.72-04-04 [SUPPORT]: Given `src/gzkit/schemas/ledger.json`, when the `security_floor_overridden` entry is added under `events` with its required fields and `min_length`/enum constraints, then the change is proven by an `artifact_edited` ledger event plus `gz validate --documents`.
- [ ] REQ-0.0.72-04-05 [BEHAVIOR]: Given the new model and schema entry, when the `tests/test_schemas.py` `_EVENT_MODELS` model↔schema alignment test runs, then the `security_floor_overridden` event round-trips clean — the same surface the OBPI-01 round-trip validator consumes. (@covers test)

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
