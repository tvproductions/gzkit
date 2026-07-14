---
id: OBPI-0.0.72-04-security-floor-overridden-event
parent: ADR-0.0.72-meta-governance-coherence
item: 4
lane: Heavy
status: Completed
# req_atomic (GHI #590): each REQ's labor was one indivisible unit — no sub-REQ
# subdivision. REQ-01 (event model + min_length fail-closed fields), REQ-02
# (emission from the --accept-security-floor branch), REQ-03 (ledger census
# counts the override 0->1), REQ-04 (SUPPORT — ledger.json schema entry), and
# REQ-05 (localized _EVENT_MODELS model<->schema round-trip) each landed as one
# coherent edit to a single surface; none was subdivided into seq=02+, so the
# pipeline-minted seq=01-per-REQ buckets are the true labor shape.
req_atomic:
  - REQ-0.0.72-04-01
  - REQ-0.0.72-04-02
  - REQ-0.0.72-04-03
  - REQ-0.0.72-04-04
  - REQ-0.0.72-04-05
---

# OBPI-0.0.72-04-security-floor-overridden-event: Security Floor Overridden Event

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #4 - "ADAPTER: `security_floor_overridden` ledger event — Pydantic event model + factory + ledger.json schema entry; emitted from `gz obpi complete --accept-security-floor` recording obpi_id, overridden surface(s), reason, attestor, ts; unit tests; round-trips clean through the existing `_EVENT_MODELS` model↔schema alignment; census query surfaces the override." [OBPI-01 global validator WITHDRAWN 2026-07-13 — coherence realized via the existing `_EVENT_MODELS` alignment test.]

**Status:** Completed

## Objective

A first-class `security_floor_overridden` ledger event is emitted whenever
`gz obpi complete --accept-security-floor` fires, recording the `obpi_id`, the
overridden security surface(s), the operator `reason`, the `attestor`, and a
`ts`. This makes an operator override of the completion-state-editing security
floor auditable via ledger census — closing the invisible-override hole the
OBPI-0.0.71-01 override exposed — and the new event round-trips clean through
the existing `_EVENT_MODELS` model↔schema alignment surface (localized
writer-model coherence; the OBPI-01 global validator was withdrawn 2026-07-13).

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
- `src/gzkit/commands/obpi_complete.py` — emit the event from the `--accept-security-floor` override branch (the `if accept_security_floor and effective_sensitivity == "security":` block, ~line 1103)
- `src/gzkit/governance/trust_audits/sensitivity.py` — add a public `detect_brief_security_surfaces(brief_text, project_root) -> tuple[str, ...]` helper (mirrors `detect_brief_security_floor`, reuses the canonical allowed-paths extractor + registry load, returns `match_globs(...)` categories) so the emission records the overridden `surfaces` without duplicating extraction logic. Operator-approved Allowed-Paths amendment (2026-07-13): the brief under-declared this coupled surface; recording `surfaces` cleanly is a correction to fulfill the declared intent, not scope creep. `sensitivity.py` is not itself a registered security surface.
- `src/gzkit/governance/trust_audits/events.py` — add the `security_floor_overridden` entry to `_NO_GRAPH_IMPACT` (audit-only event, no artifact-graph handler). Mechanically forced coupled fence: `audit_event_handlers` fails closed on any emitted event type lacking a handler-or-waiver. Operator-approved Allowed-Paths amendment (2026-07-13).
- `src/gzkit/ontology/corpus.py` — add `security_floor_overridden` to `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES`. Mechanically forced coupled fence (ADR-0.32.0 BI#1, registry-coupled): the ontology projection fails closed on any un-dispositioned live discriminator. Operator-approved Allowed-Paths amendment (2026-07-13).
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
- [ ] REQ-0.0.72-04-05 [BEHAVIOR]: Given the new model and schema entry, when the `tests/test_schemas.py` `_EVENT_MODELS` model↔schema alignment test runs, then the `security_floor_overridden` event round-trips clean via the existing `_EVENT_MODELS` model↔schema alignment (localized writer-model coherence). (@covers test)

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

Operator `g0` attested "attest completed" (2026-07-13), holding the Step-4b
verdict below.

### Step 4b — Independent Adversarial Validation

- **Adversary:** Codex (tier-1; codex-cli 0.144.1, authenticated) — 5 rounds.
  Claude subagent forbidden per GHI #678 (tier-1 available).
- **Verdict:** REFUTED-WITH-CAVEATS.
- **Rounds 1–4 (real OBPI defects, all fixed + regression-tested):** (1) override
  emitted ~193 lines BEFORE the atomic transaction → phantom record + double-emit
  on retry; (2) appended BEFORE the receipt inside the transaction → a
  receipt-append failure orphaned it; (3) a HARD append after the receipt GATED
  completion and tripped the rollback when it failed (violating REQ-04 "NEVER a
  gate"); (4) the best-effort warning path could itself throw (`ValueError` on a
  closed stream) and re-enter the rollback. Resolution: the witness is emitted by
  a post-transaction, fully best-effort helper
  (`_emit_security_floor_override_best_effort`) structurally OUTSIDE the rollback
  boundary; 11 regression tests in `tests/test_security_floor_overridden.py`
  encode every failure mode.
- **Round 5 (confirmation + surviving caveat):** the emission is phantom-free,
  double-emit-free, never gates completion, and never reverts committed state
  ("cannot invoke transaction rollback, create a phantom, or revert the
  receipt"). Surviving caveat = a PRE-EXISTING, system-wide `Ledger.append`
  non-atomicity (a partial mid-write corrupts any append; `ledger_integrity`
  security surface) — Codex's own distinction places it OUTSIDE this OBPI.
  Operator-ruled out-of-scope; tracked in **GHI #687**.

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Self-dogfooding: obpi_complete.py is a registered auth_boundaries security surface, so completing this OBPI itself requires --accept-security-floor, which fires the new emission. Ledger census (event=='security_floor_overridden') goes 0 -> 1 at this OBPI's own Gate 5. Round-trip coherence: security_floor_overridden_event(...).model_dump() -> parse_typed_event() -> SecurityFloorOverriddenEvent (test_schemas _EVENT_MODELS alignment, 25/25). Step-4b Codex refuted-with-caveats after 5 adversarial rounds.

### Implementation Summary


- Model: SecurityFloorOverriddenEvent (src/gzkit/events.py) + TypedLedgerEvent union — obpi_id/surfaces/reason/attestor Field(min_length=1); ts inherited from _EventBase
- Factory: security_floor_overridden_event (src/gzkit/ledger_events.py) mirroring obpi_completion_uncovered_accept_event
- Schema: security_floor_overridden entry (src/gzkit/schemas/ledger.json), required 4 fields min_length:1
- Emission: post-transaction best-effort helper _emit_security_floor_override_best_effort (src/gzkit/commands/obpi_complete.py), structurally OUTSIDE the transaction rollback boundary (Step-4b rounds 1-4)
- Helper: public detect_brief_security_surfaces (src/gzkit/governance/trust_audits/sensitivity.py) — matched categories via match_globs, no duplicated extraction
- Coupled event-type fences: _NO_GRAPH_IMPACT (trust_audits/events.py), _ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES (ontology/corpus.py)
- Registration: _EVENT_MODELS (tests/test_schemas.py)
- Tests: tests/test_security_floor_overridden.py (11 tests; 5-round Codex-adversary-hardened)
- Date completed: 2026-07-13
- Attestation status: operator g0 attested "attest completed"
- Defects noted: GHI #687 (pre-existing Ledger.append non-atomicity, out-of-scope)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #687** — `Ledger.append` is not failure-atomic (a partial mid-write
  corrupts the JSONL ledger). Pre-existing, system-wide `ledger_integrity`
  primitive defect surfaced by this OBPI's Step-4b round 5; NOT this OBPI's
  emission defect (operator-ruled out-of-scope, 2026-07-13). Routed for its own
  scoped fix.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.72-04 security_floor_overridden ledger event (Pydantic model + factory + ledger.json schema entry + post-transaction best-effort emission + census + localized round-trip) closes the invisible-override audit hole OBPI-0.0.71-01 exposed. Unit tests green (arb-step-unittest-14ebd83141db47aaa34e1d4038e91b28), lint clean (arb-ruff-6dfb8d7b8a414fcfb72fda2944967416), typecheck clean (arb-step-typecheck-57c3e773fed1472cac1942ac31daefae), mkdocs --strict clean (arb-step-mkdocs-cde8a081c7154eddaa59ed42f8b59715); 4 BEHAVIOR REQs @covers + RED-witnessed; schema alignment 25/25. Step-4b Codex tier-1, 5 rounds, refuted-with-caveats — rounds 1-4 emission defects all fixed, round-5 caveat is the pre-existing system-wide Ledger.append non-atomicity tracked in GHI #687.
- Date: 2026-07-14

---

**Date Completed:** 2026-07-14

**Evidence Hash:** -
