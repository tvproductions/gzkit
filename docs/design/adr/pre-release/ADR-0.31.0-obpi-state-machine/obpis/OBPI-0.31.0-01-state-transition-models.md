---
id: OBPI-0.31.0-01-state-transition-models
parent: ADR-0.31.0-obpi-state-machine
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.31.0-01-state-transition-models: State Transition Models

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md`
- **Checklist Item:** #1 - "OBPI-0.31.0-01: **state-transition-models** — Closed StrEnum state name-set + Pydantic State/Transition models (preconditions, adjacent-evidence, witness) with schema binding"

**Status:** Draft

## Objective

Lay the canonical OBPI-state-machine **model layer** as pure, additive domain
code: a closed `StrEnum` naming the eight canonical states plus frozen Pydantic
`State` and `Transition` models declaring each transition's predecessor state,
required adjacent evidence, and witness requirement, projected to a committed
JSON schema. This is the state anchor the runtime monitor (OBPI-03) and the
withdraw/supersede CLI verbs (OBPI-02) consume — the keel laid **alongside** the
legacy string-keyed choreography (`core/lifecycle.py`), retiring none of it.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new schema contract (`schemas/obpi_state_machine.json`)
and a new importable runtime model surface (`gzkit.core.obpi_state_machine`)
that OBPI-02/03 bind against.

## Allowed Paths

- `src/gzkit/core/obpi_state_machine.py` — **CREATE**: `OBPIState`/`WitnessRequirement` StrEnums, `State`/`Transition` Pydantic models, canonical `OBPI_STATES` + `CANONICAL_TRANSITIONS` declarations, `obpi_state_machine_json_schema()` projector
- `src/gzkit/schemas/obpi_state_machine.json` — **CREATE**: committed JSON-schema projection of the state machine (drop-in, loaded via `gzkit.schemas.load_schema`)
- `tests/test_obpi_state_machine.py` — **CREATE**: `@covers`-decorated REQ tests (flat convention, mirrors `tests/test_lifecycle.py`)
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md` — add `## Boundary Invariants` (STRUCTURAL-FENCE anchor for REQ-05)
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/obpis/OBPI-0.31.0-01-state-transition-models.md` — this brief (evidence)

## Denied Paths

- `src/gzkit/core/lifecycle.py`, `src/gzkit/lifecycle.py` — legacy content-type choreography; NOT retired or edited here (deferred-in-keel)
- `src/gzkit/governance/status_vocab.py`, `src/gzkit/ledger.py` — existing state vocabularies (`STATUS_VOCAB_MAPPING`, `OBPI_RUNTIME_STATES`); untouched
- `src/gzkit/commands/**` — no CLI verb in this OBPI (that is OBPI-02)
- `src/gzkit/governance/invariants.py`, `src/gzkit/governance/trust_audits/**` — no runtime monitor in this OBPI (that is OBPI-03)
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Deliver the closed `OBPIState` StrEnum with exactly the eight ADR-mandated states — `drafted, planned, implementing, verified, attested, synced, withdrawn, superseded` — no more, no fewer.
2. REQUIREMENT: `State` and `Transition` are frozen (`ConfigDict(frozen=True, extra="forbid")`) Pydantic models per `.claude/rules/models.md`; `Transition` state fields are typed to `OBPIState` so non-member strings fail validation.
3. NEVER: Encode a TTY/PTY/interactive-terminal witness value. The witness requirement is transport-agnostic — `human_attested` (a human attests, relayed verbatim via `--attestor-present` / `--attestation-text`) vs `self_close`; the mechanism serves attestation, never gates it (canon-owner directive; parent ADR § Decision item 2).
4. NEVER: Add a runtime monitor, a `gz obpi` transition verb, or any edit to the legacy `core/lifecycle.py` choreography — those are OBPI-03, OBPI-02, and deferred-in-keel respectively.
5. ALWAYS: Keep the committed `schemas/obpi_state_machine.json` byte-equal to the model's generated schema (coherence fail-close), so schema and model cannot silently drift.
6. ALWAYS: Reconcile this brief against the parent ADR § Decision (items 1–2) before implementation; quote the Decision items into Implementation Summary.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision items 1–2 quoted** verbatim into Implementation Summary below. Items 1 (named states, closed enum, schema-bound) and 2 (named transitions with declared preconditions/witness) ARE this OBPI's contract.
- [x] Parent ADR § Intent — choreography-not-state-machine framing; the canonical observed symptom (GHI #348 silent `Withdrawn`→`pending` demotion).
- [x] Parent ADR § Target Scope — the airlock-critical tracer (schema → model → monitor → CLI → ledger); this OBPI is the schema+model slice.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Prerequisites (STOP if missing):**

- [x] `src/gzkit/core/` exists (siblings: `lifecycle.py`, `models.py`) — new module lands here
- [x] `src/gzkit/schemas/` exists with `load_schema`/`get_schema_path` — new schema lands here
- [x] Parent ADR present and registered in `gz state`

**Existing Code (read; do NOT modify — establishes what the canonical enum supersedes):**

- [x] `src/gzkit/core/lifecycle.py` — legacy `TransitionRule` + `OBPI_TRANSITIONS` (`Draft→Active→Completed/Abandoned`), string-keyed content-type tables; NOT retired here
- [x] `src/gzkit/governance/status_vocab.py` — `STATUS_VOCAB_MAPPING` frontmatter→ledger terms; `CANONICAL_LEDGER_TERMS`
- [x] `src/gzkit/ledger.py` — `OBPI_RUNTIME_STATES` (ADR-0.0.9 canonical ledger states)
- [x] `src/gzkit/req_kind.py` — `enum.StrEnum` + frozen Pydantic model precedent for a closed governance taxonomy (the pattern this module mirrors)
- [x] `src/gzkit/schemas/__init__.py` — `load_schema(name)` drop-in loader; `.claude/rules/models.md` (Pydantic policy)
- [x] `tests/test_lifecycle.py` — flat test-file convention and state-machine test shape to mirror

## Quality Gates

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

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test) proving the codebase is healthy.
     AUTHORING CONTRACT: single-program, shell-less invocations only — no &&, ||,
     |, ;, $(...), or redirects (GHI #415). -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_obpi_state_machine -v

# Specific verification for this OBPI
test -f src/gzkit/core/obpi_state_machine.py
test -f src/gzkit/schemas/obpi_state_machine.json
```

## Demo

<!-- THE YIELDED PRODUCT: the importable canonical model surface OBPI-02/03 consume. -->

```bash
# The closed canonical state name-set (exactly eight, ordered)
uv run python -c "from gzkit.core.obpi_state_machine import OBPIState; print([s.value for s in OBPIState])"

# The declared canonical transitions with witness + adjacent-evidence
uv run python -c "from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS; [print(f'{t.from_state} -> {t.to_state}  witness={t.witness}  evidence={t.required_evidence}') for t in CANONICAL_TRANSITIONS]"

# Closed set: an unknown state is not a member (fail-closed schema binding;
# ValidationError-on-construction is proven by the REQ-01-02 @covers test)
uv run python -c "from gzkit.core.obpi_state_machine import OBPIState; print('bogus is a valid state:', 'bogus' in [s.value for s in OBPIState])"

# Committed schema equals the model projection (drift fail-close)
uv run python -c "from gzkit.schemas import load_schema; from gzkit.core.obpi_state_machine import obpi_state_machine_json_schema; print('schema coherent:', load_schema('obpi_state_machine') == obpi_state_machine_json_schema())"
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59); BEHAVIOR proves via
     @covers test, STRUCTURAL-FENCE via parent ADR ## Boundary Invariants. -->

- [ ] REQ-0.31.0-01-01 [BEHAVIOR]: `gzkit.core.obpi_state_machine.OBPIState` is a closed `StrEnum` whose members are exactly `drafted, planned, implementing, verified, attested, synced, withdrawn, superseded` (eight — no more, no fewer), with string values equal to their lowercase names; pinned by a `@covers(REQ-0.31.0-01-01)` test in `tests/test_obpi_state_machine.py`.
- [ ] REQ-0.31.0-01-02 [BEHAVIOR]: `Transition` is a frozen `extra="forbid"` Pydantic model whose `from_state`/`to_state` are typed `OBPIState`, carrying `required_evidence: list[str]` and `witness: WitnessRequirement`; constructing a `Transition` with a non-member state OR an unknown field raises `pydantic.ValidationError`.
- [ ] REQ-0.31.0-01-03 [BEHAVIOR]: `State` is a frozen Pydantic model declaring a `terminal: bool`; the canonical `OBPI_STATES` declaration holds exactly one `State` per `OBPIState` member, with `withdrawn` and `superseded` terminal and all other six non-terminal.
- [ ] REQ-0.31.0-01-04 [BEHAVIOR]: the committed `src/gzkit/schemas/obpi_state_machine.json` equals `obpi_state_machine_json_schema()` — `load_schema("obpi_state_machine")` is byte-coherent with the model projection — asserted by a `@covers(REQ-0.31.0-01-04)` coherence test that fails on drift.
- [ ] REQ-0.31.0-01-05 [STRUCTURAL-FENCE]: OBPI-01 delivers the state/transition models + schema only — it adds NO runtime invariant monitor (OBPI-03) and NO `gz obpi` transition verb (OBPI-02), and the new module imports no monitor/command surface; witness requirement is transport-agnostic (no TTY/PTY value). Anchored in the parent ADR `## Boundary Invariants`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

Before: OBPI lifecycle state is choreographed across three disagreeing
vocabularies (`core/lifecycle.py` strings, `ledger.OBPI_RUNTIME_STATES`,
`status_vocab` frontmatter terms), with no single canonical name-set or
declared transition contract — the condition that let GHI #348 silently
demote a hand-marked `Withdrawn` brief to `pending`. After: one closed
canonical `OBPIState` enum + declared `Transition` models (predecessor,
adjacent evidence, witness) exist as the schema-bound anchor OBPI-02/03 bind
to — no behavior change yet, but the spine the monitor will enforce.

### Key Proof

`uv run python -c "from gzkit.core.obpi_state_machine import OBPIState; print([s.value for s in OBPIState])"`
→ `['drafted', 'planned', 'implementing', 'verified', 'attested', 'synced', 'withdrawn', 'superseded']`

### Implementation Summary

**Parent ADR § Decision item 1 (verbatim):** "Named states (closed enum,
schema-bound). Every OBPI is in exactly one of: `drafted`, `planned`,
`implementing`, `verified`, `attested`, `synced`, `withdrawn`, `superseded`.
The current `STATUS_VOCAB_MAPPING` becomes a *legacy-import* table only — new
briefs author against the closed enum directly, and the vocab table shrinks
rather than grows."

**Parent ADR § Decision item 2 (verbatim):** "Named transitions (closed enum,
schema-bound). Every state change is an event with a name (e.g.
`obpi.transitioned.attested`), declared preconditions (predecessor state,
required adjacent evidence), declared postconditions (successor state, emitted
ancillary events), and a declared witness requirement: `human_attested` (a
human attests — transport-agnostic, relayed verbatim via `--attestor-present`
/ `--attestation-text`) or `self_close` per Exception-mode rules. Human
attestation is sacrosanct and transport-agnostic; no
TTY/PTY/interactive-terminal mechanism gates the witness — the mechanism
serves the attestation, never gates it (canon-owner directive). The witness
requirement is a property of the transition, not of one CLI command."

**Witness taxonomy (canon-conformant):** This OBPI encodes a transport-agnostic
`WitnessRequirement` — `human_attested` (a human attests, relayed verbatim via
`--attestor-present` / `--attestation-text`) vs `self_close`. No TTY/PTY value
exists: human attestation is sacrosanct and transport-agnostic (canon-owner
directive), matching parent ADR § Decision item 2 and Boundary Invariant #2.

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
