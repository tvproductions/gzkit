---
id: OBPI-0.41.0-01-ledger-event-types-for-tdd
parent: ADR-0.41.0
item: 1
lane: Heavy
status: pending
---

# OBPI-0.41.0-01: Ledger Event Types for TDD Emission

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md`
- **Checklist Item:** #1 — "Typed ledger events tdd_red_observed and tdd_green_observed with JSON schema"

**Status:** Draft

## Objective

Add two new typed Pydantic ledger events — `TddRedObservedEvent` and `TddGreenObservedEvent` — plus a JSON schema at `data/schemas/tdd_event.schema.json`, so downstream OBPIs have a typed emission channel for TDD discipline evidence. No CLI surface yet (OBPI-02), no rule integration (OBPI-03), no docs (OBPI-04) — this brief is pure data-layer.

## Lane

**Heavy** — adds new ledger event types to the schema-controlled event stream. The ledger is an append-only governance surface; adding event types is a schema change.

## Allowed Paths

- `src/gzkit/events.py` — add two Pydantic event classes
- `src/gzkit/ledger_events.py` — extend event union/registry if applicable
- `data/schemas/tdd_event.schema.json` — new JSON schema file
- `data/schemas/ledger_event.schema.json` — extend event union if the top-level schema lists known event types
- `tests/test_tdd_events.py` — new test file
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/obpis/OBPI-0.41.0-01-ledger-event-types-for-tdd.md` — this brief

## Denied Paths

- `src/gzkit/commands/` — no CLI surface in this OBPI (belongs to OBPI-02)
- `.gzkit/rules/` — no rule updates here (belongs to OBPI-03)
- `docs/user/commands/` — no manpage here (belongs to OBPI-04)
- `.gzkit/ledger.jsonl` — never edited directly
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. `TddRedObservedEvent` is a frozen Pydantic `BaseModel` subclass with fields: `event` (literal `"tdd_red_observed"`), `id`, `schema_`, `req_id`, `test_target`, `exit_code`, `failure_kind`, `stdout_digest`, `agent`, and any inherited `LedgerEvent` fields.
2. `TddGreenObservedEvent` is a frozen Pydantic `BaseModel` subclass with fields: `event` (literal `"tdd_green_observed"`), `id`, `schema_`, `req_id`, `test_target`, `exit_code`, `test_count`, `red_event_ref` (optional), `agent`, and inherited fields.
3. `failure_kind` is a typed enum with values: `assertion`, `missing_attribute`, `missing_module`, `name_error`, `type_error`, `collection_error`. `collection_error` is explicitly included so OBPI-02's verifier can reject it as invalid RED.
4. Both events serialize round-trip through `model_dump_json()` / `model_validate_json()` without loss.
5. `data/schemas/tdd_event.schema.json` has `$id: gzkit.tdd_event.schema.json` and declares the field shape for both event types (anyOf over the two).
6. The existing ledger event validation registry recognizes the new event types (if the registry uses a closed enum of known types, it is updated; if it uses structural validation, no registry edit needed).
7. Writing a `tdd_red_observed` or `tdd_green_observed` event through the existing `Ledger.append()` API succeeds without raising.
8. Tests cover: field validation (missing required), failure_kind enum strictness, round-trip serialization, schema load, Ledger.append integration.

> STOP-on-BLOCKERS: if `src/gzkit/events.py` does not have a clear pattern for adding new event classes, read the existing TaskStartedEvent/TaskCompletedEvent precedent (added under ADR-0.22.0) before authoring.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` — agent operating contract (especially DO IT RIGHT and TASK-driven workflow)
- [ ] `ADR-0.41.0` — parent ADR for full context

**Context:**

- [ ] `src/gzkit/events.py` — existing event class precedents (TaskStartedEvent, ObpiCreatedEvent, etc.)
- [ ] `src/gzkit/ledger.py` — how LedgerEvent base class is defined and how events are appended
- [ ] `data/schemas/` — existing schema files for naming and `$id` convention
- [ ] `tests/test_events.py` or similar — existing test patterns for event validation

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/events.py` exists and contains a base `LedgerEvent` class or similar shared model
- [ ] `data/schemas/` directory exists and is writable

**Existing Code (understand current state):**

- [ ] The TaskStartedEvent pattern from `src/gzkit/events.py` is the closest precedent — it was added under ADR-0.22.0 and wires into Ledger.append identically to what this OBPI needs.
- [ ] Read at least two existing event schemas in `data/schemas/` to match the `$id` / `$schema` / `type` conventions.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per REQ increment
- [ ] Tests pass: `uv run gz test`
- [ ] Per-REQ TDD events will be emitted via `gz tdd red/green` once OBPI-02 ships; until then, the TDD cycle is documented in the OBPI evidence but not yet machine-verified (meta: this OBPI is the data layer for the verification mechanism that does not yet exist)

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] No new user-facing docs here (OBPI-04 owns that); this gate is satisfied by the build passing with no new doc surfaces introduced

### Gate 4: BDD (Heavy)

- [ ] No new BDD scenarios in this OBPI (OBPI-02 owns command-level BDD)

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded at ADR closeout

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_tdd_events -v

# OBPI-specific: schema loads and validates sample events
uv run python -c "import json; json.loads(open('data/schemas/tdd_event.schema.json').read())"

# OBPI-specific: instantiate and serialize
uv run python -c "from gzkit.events import TddRedObservedEvent; print(TddRedObservedEvent.__name__)"
```

## Acceptance Criteria

- [ ] REQ-0.41.0-01-01: Given `src/gzkit/events.py`, when imported, then `TddRedObservedEvent` is a frozen Pydantic `BaseModel` with `event` literal `"tdd_red_observed"` and fields req_id, test_target, exit_code, failure_kind, stdout_digest, agent.
- [ ] REQ-0.41.0-01-02: Given `src/gzkit/events.py`, when imported, then `TddGreenObservedEvent` is a frozen Pydantic `BaseModel` with `event` literal `"tdd_green_observed"` and fields req_id, test_target, exit_code, test_count, optional red_event_ref, agent.
- [ ] REQ-0.41.0-01-03: Given the `failure_kind` field on `TddRedObservedEvent`, when instantiated with a value outside {assertion, missing_attribute, missing_module, name_error, type_error, collection_error}, then a `ValidationError` is raised.
- [ ] REQ-0.41.0-01-04: Given an instantiated `TddRedObservedEvent` or `TddGreenObservedEvent`, when `.model_dump_json()` is called and the result is round-tripped through `.model_validate_json()`, then the reconstructed object equals the original.
- [ ] REQ-0.41.0-01-05: Given `data/schemas/tdd_event.schema.json`, when loaded, then it parses as valid JSON Schema with `$id: gzkit.tdd_event.schema.json` and declares the field shape for both event types via `anyOf`.
- [ ] REQ-0.41.0-01-06: Given a valid `TddRedObservedEvent` instance and an open `Ledger`, when `ledger.append(event)` is called, then the event is written to the ledger file and appears in `ledger.read_all()`.
- [ ] REQ-0.41.0-01-07: Given a test suite for this OBPI, when run with `uv run -m unittest tests.test_tdd_events`, then all seven REQ-aligned tests pass.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed per REQ, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included (instantiation + append + read)
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here after implementation
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# No BDD scope for this OBPI
```

### Gate 5 (Human)

```text
# Attestation recorded at ADR closeout
```

### Value Narrative

Before this OBPI: TDD RED/GREEN had no typed representation in the ledger. Agents could emit claims about their TDD discipline via prose, but nothing distinguished a "tests pass" claim (ARB receipt) from a "tests failed for the right reason, then I fixed them" claim (verified RED→GREEN cycle).

After this OBPI: the ledger has two first-class, schema-validated event types for the TDD cycle. Downstream tooling (OBPI-02) can emit them; downstream rules (OBPI-03) can cite them in attestation enrichment. The data layer is ready before the CLI surface or rule integration depend on it.

### Key Proof

```python
from gzkit.events import TddRedObservedEvent
from gzkit.ledger import Ledger

event = TddRedObservedEvent(
    event="tdd_red_observed",
    id="tdd-red-2026-04-15T13-00-00",
    schema_="gzkit.ledger_event.schema.json",
    req_id="REQ-0.41.0-01-01",
    test_target="tests.test_tdd_events.TestTddRedObservedEvent.test_event_field",
    exit_code=1,
    failure_kind="assertion",
    stdout_digest="sha256:...",
    agent="claude-code",
)
Ledger(Path(".gzkit/ledger.jsonl")).append(event)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` at ADR closeout
- Attestation: n/a until ADR-0.41.0 closeout
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
