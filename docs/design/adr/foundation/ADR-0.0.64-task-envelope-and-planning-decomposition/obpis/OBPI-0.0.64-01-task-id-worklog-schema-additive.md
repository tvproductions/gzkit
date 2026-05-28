---
id: OBPI-0.0.64-01-task-id-worklog-schema-additive
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.64-01-task-id-worklog-schema-additive: Task Id Worklog Schema Additive

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- **Checklist Item:** #1 — Worklog schema additive (Decision item 1).

**Status:** Draft

## Objective

Add an optional `task_id: str | None = None` field to eight worklog event
models in `src/gzkit/events.py` and to the matching event shapes in
`src/gzkit/schemas/ledger.json`, so per-labor-unit TASK attribution can ride
on every worklog event the four-tier governance spine emits. The field is
nullable-additive; pre-restoration ledger events validate unchanged
(grandfathered by construction). This OBPI delivers the schema channel
only — no decorator, no validator, no CLI surface; OBPIs 02-05 layer on top.

## Lane

**Heavy** — ledger-schema change is a runtime contract.

## Allowed Paths

- `src/gzkit/events.py` — eight worklog event models gain optional `task_id` field
- `src/gzkit/schemas/ledger.json` — JSON-schema mirror of the Pydantic field
- **CREATE** `tests/governance/test_task_id_worklog_field.py` — REQ-derived `@covers` tests for the new field
- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/obpis/OBPI-0.0.64-01-task-id-worklog-schema-additive.md` — this brief

## Denied Paths

- `src/gzkit/tasks.py` — OBPI-02 owns the decorator and registry; this brief
  must not modify task-side code
- `src/gzkit/commands/task.py` — auto-coordination wiring is OBPI-04 territory
- `src/gzkit/cli/parser_maintenance.py` — no new CLI flags in this OBPI
- `src/gzkit/governance/trust_audits/` — no new validator scope here
- `src/gzkit/schemas/obpi_brief_structure.json` — `req_atomic` frontmatter is OBPI-04
- `.gzkit/rules/task-discovery.md` — OBPI-02 authors the rule
- Any TASK_BOUNDARY event models (`TaskStartedEvent`, `TaskCompletedEvent`,
  `TaskBlockedEvent`, `TaskEscalatedEvent`) — these already carry TASK identity
  by construction (rejected alternative 5 in ADR § Alternatives)
- All other paths in the repository

## Requirements (FAIL-CLOSED)

1. NEVER add the `task_id` field to TASK-boundary event models
   (`TaskStartedEvent` / `TaskCompletedEvent` / `TaskBlockedEvent` /
   `TaskEscalatedEvent`). Per ADR Alternative 5: those are TASK-boundary
   events with TASK identity by construction; re-adding `task_id` would be
   tautological.
2. ALWAYS make the field optional (`task_id: str | None = None`) so the
   7,897 pre-restoration ledger events grandfather unchanged. A required
   field would break backwards compatibility (ADR Alternative 3, rejected).
3. ALWAYS keep the Pydantic event models `extra="forbid"` per
   `.gzkit/rules/models.md`. The field is added by name; no `extra="allow"`
   escape hatch.
4. NEVER widen the field's type beyond `str | None`. The decoration-time
   validation in OBPI-02 (`TaskId.parse`) is the strict-form check; the
   schema field accepts the canonical string form only.
5. ALWAYS keep the JSON-schema mirror in `src/gzkit/schemas/ledger.json`
   byte-additive: a new `"task_id": {"type": ["string", "null"]}` (or
   equivalent nullable shape) under the event's properties, with `task_id`
   absent from the event's `"required"` array.
6. ALWAYS confirm the precise eight event types against the current schema
   during implementation (ADR Decision item 1's caveat). The operator-locked
   target list is: `artifact_edited`, `artifact_renamed`, `gate_checked`,
   `attested`, `composition_rendered`, `audit_receipt_emitted`,
   `obpi_completion_uncovered_accept`, `intrinsic-complexity-attestation`.
7. NEVER use `Optional[str]` / `List[str]` syntax per `.gzkit/rules/pythonic.md`;
   write `str | None` and `list[str]`.

> STOP-on-BLOCKERS: if any of the eight named event models is absent from
> `src/gzkit/events.py`, STOP and reconcile the list with the operator
> before editing.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim into Implementation Summary:**
  *"Worklog schema additive — `task_id: str | None = None` field added to 8
  worklog event types in `src/gzkit/events.py` and `src/gzkit/schemas/ledger.json`
  … Pre-restoration events grandfathered (the field is optional; legacy
  events validate unchanged). Pydantic `BaseModel` with
  `ConfigDict(extra='forbid')` per `.gzkit/rules/models.md`; ledger-event
  identifiers serialized via `.as_posix()` where they encode paths per
  `.gzkit/rules/cross-platform.md`."*
- [ ] Parent ADR § Intent — the GHI #553 doctrine-runtime decoupling framing.
- [ ] Parent ADR § Boundary Invariants — invariant 1 (additive-only) constrains this OBPI.

> **STOP:** If you cannot quote the parent ADR § Decision item 1, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/models.md` — Pydantic `BaseModel` + `ConfigDict(extra="forbid")` shape
- [ ] `.gzkit/rules/cross-platform.md` — `.as_posix()` rendering for path-shaped identifiers
- [ ] `.gzkit/rules/pythonic.md` — `str | None` not `Optional[str]`

**Context:**

- [ ] OBPI-0.0.64-02 (advances decorator) — consumer of the new field; ensure schema accepts what OBPI-02 will write
- [ ] OBPI-0.0.64-04 (validator) — signature (a) reads this field; the absence-under-active-TASK signature

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/events.py:114` — `ArtifactEditedEvent` class definition
- [ ] `src/gzkit/events.py:131` — `GateCheckedEvent` class definition
- [ ] `src/gzkit/events.py:122` — `AttestedEvent` class definition
- [ ] `src/gzkit/events.py:151` — `AuditReceiptEmittedEvent` class definition
- [ ] `src/gzkit/events.py:172` — `ArtifactRenamedEvent` class definition
- [ ] `src/gzkit/events.py:264` — `ObpiCompletionUncoveredAcceptEvent` class definition
- [ ] `src/gzkit/events.py:355` — `IntrinsicComplexityAttestationEvent` class definition
- [ ] `src/gzkit/events.py:391` — `CompositionRenderedEvent` class definition
- [ ] `src/gzkit/schemas/ledger.json` — JSON-schema event-shape definitions to mirror

**Existing Code (understand current state):**

- [ ] `src/gzkit/events.py:28` — `_EventBase` model carrying `ConfigDict(extra="forbid")`
  (the per-event subclass discipline this OBPI inherits)
- [ ] `src/gzkit/events.py:314` — `_TaskEventBase` carrying `task_id` already for
  TASK-boundary events (DO NOT touch these — Denied Path)
- [ ] `tests/governance/` siblings (e.g. `tests/governance/test_attestation_receipt_validator.py`)
  for the established test shape

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR § Decision item 1 quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests in `tests/governance/test_task_id_worklog_field.py` derived from REQs, not implementation
- [ ] Red-Green-Refactor cycle per behavior increment
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff`
- [ ] Type check clean: `uv run gz arb typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] Ledger-schema change reflected anywhere the schema is documented

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy / Foundation)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/governance/test_task_id_worklog_field.py
uv run gz validate --documents

# OBPI-specific: schema additive proof
uv run python -c "from gzkit.events import ArtifactEditedEvent; print(ArtifactEditedEvent.model_fields['task_id'])"
uv run python -c "import json,pathlib; s=json.loads(pathlib.Path('src/gzkit/schemas/ledger.json').read_text()); print('task_id present' if 'task_id' in str(s) else 'MISSING')"

# Backwards-compat proof: load a pre-restoration ledger event
uv run python -c "import json; from gzkit.ledger import LedgerEvent; LedgerEvent.model_validate({'id':'evt','event':'artifact_edited','schema':'gz/v1','timestamp':'2026-01-01T00:00:00Z','agent':'pre-existing'})"
```

## Demo

```bash
# Worklog event with explicit TASK attribution (the new capability):
uv run python -c "from gzkit.events import ArtifactEditedEvent; from gzkit.ledger import LEDGER_SCHEMA; e = ArtifactEditedEvent(event='artifact_edited', id='demo', schema_=LEDGER_SCHEMA, agent='claude-code', task_id='TASK-0.0.64-01-01-01'); print(e.model_dump_json(indent=2))"

# Worklog event WITHOUT TASK attribution (grandfathered path):
uv run python -c "from gzkit.events import ArtifactEditedEvent; from gzkit.ledger import LEDGER_SCHEMA; e = ArtifactEditedEvent(event='artifact_edited', id='demo', schema_=LEDGER_SCHEMA, agent='claude-code'); print('task_id =', e.task_id)"
```

## Acceptance Criteria

- [ ] REQ-0.0.64-01-01 [BEHAVIOR]: Each of the eight named worklog event models in `src/gzkit/events.py` exposes a `task_id: str | None = None` field; a `@covers`-decorated test in `tests/governance/test_task_id_worklog_field.py` instantiates each event with `task_id=None` AND with a valid canonical TASK ID string and asserts both paths validate.
- [ ] REQ-0.0.64-01-02 [BEHAVIOR]: Each of the eight worklog event models rejects an unknown field per `ConfigDict(extra="forbid")`; a `@covers`-decorated test asserts `ValidationError` on a `garbage="x"` keyword on every one of the eight models.
- [ ] REQ-0.0.64-01-03 [BEHAVIOR]: `src/gzkit/schemas/ledger.json` validates a legacy event (no `task_id` key present) AND a new-shape event (`task_id` set to a canonical TASK ID string) for each of the eight event types; a `@covers`-decorated test runs the JSON schema across fixture events and asserts both shapes pass.
- [ ] REQ-0.0.64-01-04 [BEHAVIOR]: The four TASK-boundary event models (`TaskStartedEvent`, `TaskCompletedEvent`, `TaskBlockedEvent`, `TaskEscalatedEvent`) are NOT changed by this OBPI; a `@covers`-decorated test asserts the model_fields keysets of these four classes are identical to their pre-restoration shape (regression guard against Alternative-5 violation).
- [ ] REQ-0.0.64-01-05 [SUPPORT]: The eight worklog event types in `src/gzkit/schemas/ledger.json` carry a `task_id` property whose JSON schema admits string-or-null and is NOT listed in the event's `"required"` array — gz validate --documents + artifact_edited event proves the schema parses and the legacy ledger remains valid.
- [ ] REQ-0.0.64-01-06 [STRUCTURAL-FENCE]: This OBPI is additive against `d70793c4` — no commit on this OBPI's branch removes, renames, or alters the auto-coordination call sites `auto_start_obpi_tasks` / `auto_complete_obpi_tasks` in `src/gzkit/commands/task.py`; the parent ADR-0.0.64 § Boundary Invariants invariant 1 (restoration-is-additive) names this invariant.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief; Decision item 1 quoted
- [ ] **Gate 2 (TDD):** RGR cycle followed; REQ-covering tests present in `tests/governance/test_task_id_worklog_field.py`
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` § OBPI Acceptance Protocol.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste arb-step-unittest receipt output here
```

### Code Quality

```text
# Paste arb-ruff + arb-step-typecheck receipt outputs here
```

### Gate 3 (Docs)

```text
# Paste arb-step-mkdocs output here
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

### Key Proof

### Implementation Summary

- Parent ADR § Decision item 1 (verbatim): _filled at completion_
- Files created/modified: _filled at completion_
- Tests added: _filled at completion_
- Date completed: _filled at completion_
- Attestation status: _filled at completion_
- Defects noted: _filled at completion_

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
