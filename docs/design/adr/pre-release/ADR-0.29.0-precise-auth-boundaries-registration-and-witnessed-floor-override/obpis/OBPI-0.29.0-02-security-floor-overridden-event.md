---
id: OBPI-0.29.0-02-security-floor-overridden-event
parent: ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override
item: 2
lane: heavy
sensitivity: security
status: Draft
---

# OBPI-0.29.0-02-security-floor-overridden-event: Add the `security_floor_overridden` ledger event across all five surfaces, emit it when `--accept-security-floor` fires (replacing the console-only print), and make it queryable.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`
- **Checklist Item:** #2 — "OBPI-0.29.0-02: Add the security_floor_overridden ledger event across all surfaces (schemas, Pydantic model, factory, no-graph-impact waiver), emit it on --accept-security-floor override (replacing the console-only print), and make it queryable."

**Status:** Draft

## Objective

Make every `--accept-security-floor` override WITNESSED. Add a `security_floor_overridden` ledger event (fields: `brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, `detected_categories`) mirroring the existing `brief_reconcile_drift_overridden` pattern across all five surfaces: schema entries in BOTH `.gzkit/schemas/ledger_events.json` AND `src/gzkit/schemas/ledger.json`; a Pydantic model plus discriminated-union registration in `src/gzkit/events.py`; a factory in `src/gzkit/ledger_events.py`; and a `_NO_GRAPH_IMPACT` waiver in `src/gzkit/governance/trust_audits/events.py`. Emit the event at the override site in `obpi_security_gate.py`, replacing the console-only print, and make it queryable by `brief_id` / `parent_adr`.

## Lane

**Heavy** — This OBPI registers a new ledger event type (a runtime/schema contract) and edits security-floor surfaces; it carries `sensitivity: security` because its Allowed Paths overlap the registered `auth_boundaries` surface (`obpi_security_gate.py`, the emit site).

> Heavy is reserved for schema/runtime-contract changes. A new ledger event type is a schema contract change.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/obpis/OBPI-0.29.0-02-security-floor-overridden-event.md` — this brief (evidence + ceremony updates)
- `.gzkit/schemas/ledger_events.json` — register the `security_floor_overridden` event id/name
- `src/gzkit/schemas/ledger.json` — register the `security_floor_overridden` event shape
- `src/gzkit/events.py` — `SecurityFloorOverriddenEvent` Pydantic model + discriminated-union registration
- `src/gzkit/ledger_events.py` — `security_floor_overridden_event` factory
- `src/gzkit/governance/trust_audits/events.py` — `_NO_GRAPH_IMPACT` waiver entry
- `src/gzkit/commands/obpi_security_gate.py` — emit site (replaces the console-only print); **CREATE** marker: this module is created by the prerequisite OBPI-0.29.0-01, so it exists in contract before this brief's authoring-time on-disk check
- `tests/` — REQ-derived unittest cases (event round-trip, emission on override, queryability, no-graph-impact coverage)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/commands/adr_audit.py` — untouched
- `data/security_surfaces.json` — re-pointing is OBPI-0.29.0-01's scope
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A `SecurityFloorOverriddenEvent` Pydantic model MUST exist in `src/gzkit/events.py` (per `.gzkit/rules/models.md`) with `event: Literal["security_floor_overridden"]` and fields `brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, `detected_categories`, and MUST be a member of the `TypedLedgerEvent` discriminated union.
2. REQUIREMENT: A `security_floor_overridden_event(...)` factory MUST exist in `src/gzkit/ledger_events.py` returning that event type.
3. REQUIREMENT: The `security_floor_overridden` event MUST be registered in BOTH `.gzkit/schemas/ledger_events.json` AND `src/gzkit/schemas/ledger.json`, and `src/gzkit/governance/trust_audits/events.py` MUST carry a `_NO_GRAPH_IMPACT` waiver entry for it with rationale.
4. REQUIREMENT: When `--accept-security-floor` fires in `obpi_security_gate.py`, the code MUST append a `security_floor_overridden` ledger event (replacing the prior console-only print) populated with `brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, and `detected_categories`.
5. REQUIREMENT: An emitted `security_floor_overridden` event MUST be queryable by `brief_id` and `parent_adr` (round-trips through `gzkit.events` deserialization and is retrievable from the ledger).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

> SCOPE BOUNDARY: The extraction of `obpi_security_gate.py` and the `auth_boundaries` re-point are OBPI-0.29.0-01's scope; the `--auth-surface-coherence` validator and docs are OBPI-0.29.0-03's scope. This OBPI assumes `obpi_security_gate.py` already exists (OBPI-01 landed).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/models.md` — Pydantic model policy for the new event
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] `src/gzkit/events.py:477-487` — `BriefReconcileDriftOverriddenEvent` (the model to mirror)
- [ ] `src/gzkit/ledger_events.py:292` — `brief_reconcile_drift_overridden_event` (the factory to mirror)
- [ ] `src/gzkit/governance/trust_audits/events.py:21-31` — `_NO_GRAPH_IMPACT` (the waiver dict to extend)
- [ ] `.gzkit/schemas/ledger_events.json:120` and `src/gzkit/schemas/ledger.json:1148` — the schema entries to mirror

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/commands/obpi_security_gate.py` (created by OBPI-0.29.0-01)
- [ ] Required path exists: `src/gzkit/events.py`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] The `brief_reconcile_drift_overridden` five-surface pattern reviewed before mirroring
- [ ] The override site in `obpi_security_gate.py` reviewed for the emit insertion

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Event documented where the ledger event catalogue is consumed (override-event narrative lands in OBPI-0.29.0-03 docs)

### Gate 4: BDD (Heavy only)

- [ ] External surface (new event type + emission) covered by direct unit tests; no new `.feature` required

### Gate 5: Human (security sensitivity)

- [ ] Human attestation recorded with the extended security walkthrough

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_events -v
uv run gz validate --ledger
```

## Demo

```bash
# Round-trip the new event through gzkit.events deserialization
uv run python -c "from gzkit.ledger_events import security_floor_overridden_event; e=security_floor_overridden_event(brief_id='OBPI-X', parent_adr='ADR-Y', attestor='g0', reason='additive structural edit', detected_categories=['auth_boundaries']); print(e['event'], e['brief_id'])"

# The no-graph-impact waiver names the event
uv run python -c "from gzkit.governance.trust_audits.events import _NO_GRAPH_IMPACT; print('security_floor_overridden' in _NO_GRAPH_IMPACT)"
```

## Acceptance Criteria

- [ ] REQ-0.29.0-02-01 [BEHAVIOR]: Given `gzkit.events`, when `SecurityFloorOverriddenEvent` is constructed with `event="security_floor_overridden"` and fields `brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, `detected_categories`, then it validates and is a member of the `TypedLedgerEvent` discriminated union (deserializing a `{"event": "security_floor_overridden", ...}` payload yields a `SecurityFloorOverriddenEvent`).
- [ ] REQ-0.29.0-02-02 [BEHAVIOR]: Given `gzkit.ledger_events.security_floor_overridden_event(...)`, when called with the six fields, then it returns a dict whose `event` is `"security_floor_overridden"` and which round-trips through `TypedLedgerEvent` validation.
- [ ] REQ-0.29.0-02-03 [SUPPORT]: The `security_floor_overridden` event is registered in `.gzkit/schemas/ledger_events.json` and `src/gzkit/schemas/ledger.json`, and `_NO_GRAPH_IMPACT` in `governance/trust_audits/events.py` carries an entry for it — proven by `uv run gz validate --ledger` passing AND an `artifact_edited` ledger event citing the two schema files emitted at OBPI completion.
- [ ] REQ-0.29.0-02-04 [BEHAVIOR]: Given a `--accept-security-floor` override in `obpi_security_gate.py`, when the override path runs, then a `security_floor_overridden` ledger event is appended (no longer only a console print) populated with `brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, and `detected_categories`.
- [ ] REQ-0.29.0-02-05 [BEHAVIOR]: Given an appended `security_floor_overridden` event, when the ledger is queried by `brief_id` (and by `parent_adr`), then the override record is retrievable with its `attestor` and `reason` intact.

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
# Direct unit tests cover the external surface; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here (security-sensitivity walkthrough)
```

### Value Narrative

Before this OBPI, a `--accept-security-floor` override emitted only an ephemeral console line at `obpi_complete.py:201-205` — no auditable record survived the run. An operator (or auditor) at 2am could not answer "who overrode the floor on which brief, and why?"

After this OBPI, every override appends a `security_floor_overridden` ledger event (`brief_id`, `parent_adr`, `override_ts`, `attestor`, `reason`, `detected_categories`), queryable by `brief_id` / `parent_adr`. The override is witnessed and permanent, mirroring the `brief_reconcile_drift_overridden` escape-hatch-receipt pattern that already governs reconcile overrides.

### Key Proof

Smoke run: `security_floor_overridden_event(brief_id='OBPI-X', parent_adr='ADR-Y', attestor='g0', reason='...', detected_categories=['auth_boundaries'])` returns an event whose `event == "security_floor_overridden"` and which round-trips through `TypedLedgerEvent`.

### Implementation Summary

- Files created/modified: `src/gzkit/events.py` (`SecurityFloorOverriddenEvent` + union member); `src/gzkit/ledger_events.py` (factory); `.gzkit/schemas/ledger_events.json` + `src/gzkit/schemas/ledger.json` (schema entries); `src/gzkit/governance/trust_audits/events.py` (`_NO_GRAPH_IMPACT` waiver); `src/gzkit/commands/obpi_security_gate.py` (emit site); `tests/` (REQ-derived cases).
- Tests added: REQ-0.29.0-02-01,02,04,05 BEHAVIOR cases; REQ-0.29.0-02-03 SUPPORT (schema + ledger proof).
- Date completed: pending.
- Attestation status: pending (security-sensitivity Gate 5).
- Defects noted: pending.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: pending
- Attestation: pending
- Date: pending

---

**Date Completed:** pending

**Evidence Hash:** -
