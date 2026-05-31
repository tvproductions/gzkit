---
id: OBPI-0.0.43-05-ledger-event-schemas-emit-paths
parent: ADR-0.0.43
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.43-05-ledger-event-schemas-emit-paths: Cascade ledger event schemas + emit paths

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #5 — "Ledger event schemas + emit paths — `bounded_context_{created,renamed,retired}`, `glossary_term_{added,revised}`, `context_map_updated`, `domain_model_{created,revised}`, `legacy_mapping_ratified`, `cascade_reconciled`, `cascade_debt_acknowledged`, `cascade_import_bypass`, `bounded_context_pending_ratification`."

**Status:** Draft

## Objective

Introduce 11 new ledger event types covering cascade authoring, reconciliation, and 2am-affordance events. Each event has a Pydantic schema, a JSON Schema, and an emit-helper function. Layer-2 truth: every cascade operation produces a ledger event.

## Lane

**Heavy** — extends the ledger event surface, which is Layer-2 source-of-truth. Event types are permanent additions (one-way door per ADR reversibility).

## Allowed Paths

- `src/gzkit/ledger/events.py` — EXTEND with 11 new event-type classes
- `src/gzkit/ledger/schemas/bounded_context_created.json` — NEW
- `src/gzkit/ledger/schemas/bounded_context_renamed.json` — NEW
- `src/gzkit/ledger/schemas/bounded_context_retired.json` — NEW
- `src/gzkit/ledger/schemas/glossary_term_added.json` — NEW
- `src/gzkit/ledger/schemas/glossary_term_revised.json` — NEW
- `src/gzkit/ledger/schemas/context_map_updated.json` — NEW
- `src/gzkit/ledger/schemas/domain_model_created.json` — NEW
- `src/gzkit/ledger/schemas/domain_model_revised.json` — NEW
- `src/gzkit/ledger/schemas/legacy_mapping_ratified.json` — NEW
- `src/gzkit/ledger/schemas/cascade_reconciled.json` — NEW
- `src/gzkit/ledger/schemas/cascade_debt_acknowledged.json` — NEW
- `src/gzkit/ledger/schemas/cascade_import_bypass.json` — NEW
- `src/gzkit/ledger/schemas/bounded_context_pending_ratification.json` — NEW
- `src/gzkit/ledger/emitters/cascade.py` — NEW
- `tests/ledger/test_cascade_events.py` — NEW
- `tests/ledger/test_cascade_event_schemas.py` — NEW

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / OBPI-02 (consume only)
- Non-ledger schemas — other OBPI scopes
- `src/gzkit/cli/**` — emit invocations live elsewhere (CLI/validator/skill code calls these emitters)
- `src/gzkit/governance/trust_audits/**` — OBPI-06
- `src/gzkit/governance/cascade_import_check.py` — OBPI-11 (will call emit-helpers)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10 (will call emit-helpers)
- `.gzkit/ledger.jsonl` — never modified directly
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`bounded_context_created`).** Schema: `{slug, parent_prd, owner_persona, introduced_in, ratified_by}`. Emitted by `gz domain init`, OBPI-13 amendment, fresh PRD authoring.
2. **REQUIREMENT (`bounded_context_renamed`).** Schema: `{old_slug, new_slug, ratified_by, reason}`. Schema lands; ceremony reserved for future ADR.
3. **REQUIREMENT (`bounded_context_retired`).** Schema: `{slug, successor_slug, ratified_by, reason}`. `successor_slug` may be `null`.
4. **REQUIREMENT (`glossary_term_added`).** Schema: `{term, scope, definition, provenance, ratified_by}`. Emitted on PRD § 2.1 additions.
5. **REQUIREMENT (`glossary_term_revised`).** Schema: `{term, old_definition, new_definition, ratified_by, reason}`.
6. **REQUIREMENT (`context_map_updated`).** Schema: `{from, to, type, description, action: "added"|"revised"|"removed", ratified_by}`.
7. **REQUIREMENT (`domain_model_created`).** Schema: `{bc_slug, dm_path, ratified_by}`. Emitted by `gz domain init`.
8. **REQUIREMENT (`domain_model_revised`).** Schema: `{bc_slug, dm_path, sections_touched: list[str], ratified_by}`. Emitted by OBPI-09 skill extensions during DM authoring.
9. **REQUIREMENT (`legacy_mapping_ratified`).** Schema: `{count, ratified_by}`. Single event at end of OBPI-07 ratification.
10. **REQUIREMENT (`cascade_reconciled`).** Schema: `{closing_artifact, changes: list[CascadeChange], ratified_by}`. Emitted at ADR/GHI closeout when reconciliation surfaces real diffs.
11. **REQUIREMENT (`cascade_debt_acknowledged`).** Schema: `{term, reason, accepted_by, accepting_artifact}`. Emitted by `gz validate --domain-cascade --accept-undefined-term`.
12. **REQUIREMENT (`cascade_import_bypass`).** Schema: `{source_file, source_line, imported_module, reason, accepted_by}`. Emitted by OBPI-11's AST enforcer when `# cascade-allowed:` inline marker is honored.
13. **REQUIREMENT (`bounded_context_pending_ratification`).** Schema: `{slug, reason, introducing_artifact, accepted_by}`. Emitted by `gz obpi complete --bc-introduced`.
14. **REQUIREMENT (emit-helper API).** `cascade.py` exports one function per event type. Each validates payload against JSON Schema before appending. Validation failure = `ValidationError` raised; never silently emit malformed event.
15. **REQUIREMENT (Layer-2 invariant).** All schemas inherit base ledger event shape (`event_id`, `event_type`, `timestamp`, `actor`, `payload`). Direct file writes to `.gzkit/ledger.jsonl` outside emit-helper API are forbidden.

> STOP-on-BLOCKERS: if existing ledger event-type registry uses non-snake_case naming, STOP and surface — consistency invariant.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #5 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Never §2 (no direct ledger edits)
- [ ] `docs/governance/state-doctrine.md` — Layer-2 truth
- [ ] `docs/governance/ledger-schema.md` (if present)

**Context:**

- [ ] Existing event types in `src/gzkit/ledger/events.py`
- [ ] Existing emit API
- [ ] Existing `.gzkit/ledger.jsonl` for event-shape inspection

**Prerequisites:**

- [ ] OBPI-01 (strategic models) landed — schemas may import `BoundedContextDeclaration` etc.

**Existing Code:**

- [ ] Existing event-type registration pattern
- [ ] Existing emit-helper conventions

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #5 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] Each of 11 event types has schema-validation test (valid + invalid payload)
- [ ] Each of 11 emit-helpers has happy-path test
- [ ] Emit-helper rejects invalid payload (fail-closed; no append)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] `docs/governance/ledger-schema.md` updated (or defer to OBPI-12)

### Gate 4: BDD (Heavy only)

- [ ] No new scenarios required (events are infrastructure)

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

uv run python -c "
from gzkit.ledger.emitters.cascade import (
    emit_bounded_context_created,
    emit_glossary_term_added,
    emit_cascade_reconciled,
    emit_cascade_debt_acknowledged,
)
print('cascade emitters importable')
"

# expect 6 cascade event schemas: bounded_context_*, glossary_term_*, context_map_*, domain_model_*, legacy_mapping_*, cascade_*
ls src/gzkit/ledger/schemas/
```

## Demo

```bash
uv run python -c "
import os, tempfile
os.environ['GZKIT_LEDGER_PATH'] = tempfile.mkstemp(suffix='.jsonl')[1]
from gzkit.ledger.emitters.cascade import emit_bounded_context_created
emit_bounded_context_created(slug='demo', parent_prd='PRD-DEMO', owner_persona='main-session', introduced_in='ADR-0.99.0', ratified_by='demo-user')
print(open(os.environ['GZKIT_LEDGER_PATH']).read())
"
```

## Acceptance Criteria

- [ ] REQ-0.0.43-05-01: Given cascade emit-helper module, when imported, then all 11 functions exported
- [ ] REQ-0.0.43-05-02: Given valid `bounded_context_created` payload, when emit called, then single line appended with `event_type: "bounded_context_created"`
- [ ] REQ-0.0.43-05-03: Given invalid `bounded_context_created` payload, when emit called, then `ValidationError` raised; no append
- [ ] REQ-0.0.43-05-04: Given each of 11 schemas, when valid instance validated, then passes; when missing-field instance validated, then fails
- [ ] REQ-0.0.43-05-05: Given `cascade_reconciled`, when emitted with `changes=[]`, then schema permits empty list (operator-attested "nothing introduced")
- [ ] REQ-0.0.43-05-06: Given `cascade_import_bypass`, when emitted, then payload includes `source_file`, `source_line`, `imported_module`, `reason`, `accepted_by`
- [ ] REQ-0.0.43-05-07: Given `bounded_context_pending_ratification`, when emitted, then operator can later query the ledger for unratified BCs
- [ ] REQ-0.0.43-05-08: Given ledger after multiple cascade emits, when inspected, then each line is valid JSON with canonical base event shape

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs clean
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# N/A
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
