---
id: OBPI-0.0.37-03-composition-drift-validator
parent: ADR-0.0.37-constitutional-invariant-composition
item: 3
lane: Heavy
status: Abandoned
---

<!-- gz-validate-skip: brief-demo-section -->

# OBPI-0.0.37-03-composition-drift-validator: Composition Drift Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #3 — "OBPI-0.0.37-03 — Composition drift validator (`gz validate --invariant-coherence`; fail-closed on drift; `composition_drift_detected` ledger event)"

**Status:** Completed

## Objective

Wire OBPI-02's renderer into the `gz validate` scope catalog as `--invariant-coherence`, fail-closed on byte-drift between rendered registry and committed AGENTS.md, and register the `composition_rendered` / `composition_drift_detected` ledger event types so every render and every drift is a replayable Layer-2 receipt.

## Lane

**Heavy** — Introduces a new validator scope (`--invariant-coherence`), registers new ledger event types, extends the `gz check` default pipeline. Validator-scope and ledger-schema surfaces trigger Heavy.

## Allowed Paths

- `src/gzkit/governance/trust_audits/invariant_coherence.py` (new) — validator scope implementation
- `src/gzkit/governance/trust_audits/__init__.py` (modify) — register the validator in the package registry
- `src/gzkit/governance/events.py` (new) — `emit_composition_rendered` / `emit_composition_drift_detected` governance-layer emission helpers
- `src/gzkit/ledger_events.py` (modify; coupled-surface coherence per AGENTS.md §1a) — `composition_rendered_event` / `composition_drift_detected_event` factories so `audit_event_schemas` resolves
- `src/gzkit/events.py` (modify; coupled-surface coherence) — `CompositionRenderedEvent` / `CompositionDriftDetectedEvent` typed models
- `src/gzkit/schemas/ledger.json` (modify; coupled-surface coherence) — schema entries for both event types so `gz validate --ledger` does not fail-close
- `src/gzkit/governance/trust_audits/events.py` (modify; coupled-surface coherence) — `_NO_GRAPH_IMPACT` waivers for the two new events
- `.gzkit/schemas/ledger_events.json` (new) — per-event-type registry schema definitions (REQ-05)
- `src/gzkit/commands/validate_cmd.py` (modify) — wire `--invariant-coherence` into `default_scopes`, runner, and `_POLICY_BREACH_ERROR_TYPES`
- `src/gzkit/cli/parser_maintenance.py` (modify) — `--invariant-coherence` argparse flag (the `gz validate` flag-dispatch surface)
- `tests/governance/test_invariant_coherence.py` (new) — REQ-derived validator assertions (tempdir-based; no static fixtures dir)
- `tests/test_schemas.py` (modify; coupled-surface coherence) — register the two new event models in `_EVENT_MODELS`
- `features/constitutional_invariants.feature` (modify) — add drift-validator scenarios tagged `@REQ-0.0.37-03-*`; file created by OBPI-02
- `features/steps/constitutional_invariants_steps.py` (modify) — step definitions for the new scenarios
- `docs/governance/advisory-rules-audit.md` (modify) — add scorecard entry for the new validator scope
- `docs/user/manpages/validate.md` (modify) — add `--invariant-coherence` flag documentation
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-03-composition-drift-validator.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md` (read-only here; written only by OBPI-09 migration via OBPI-02 renderer)
- `src/gzkit/governance/compose.py` (OBPI-02 — consume, do not modify)
- `src/gzkit/governance/invariants.py` (OBPI-01 — consume)
- Brief reconciliation surfaces — OBPI-05/06
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `trust_audits/invariant_coherence.py` defines `validate_invariant_coherence(root: Path) -> AuditResult`. The function loads the registry (OBPI-01), re-renders to bytes (OBPI-02 `--stdout` path), reads committed `AGENTS.md`, and byte-compares. Mismatch returns AuditResult with severity=ERROR and the first 50 lines of unified diff in `detail`.
2. REQUIREMENT: The validator is registered in the trust-audits package registry so `gz validate --invariant-coherence` dispatches to it.
3. REQUIREMENT: `gz validate --invariant-coherence` exits 0 on match; exit code 3 on drift (consistent with other `gz validate --*` scopes per `.gzkit/rules/governance-core.md`).
4. REQUIREMENT: Every invocation of the validator emits a `composition_rendered` ledger event regardless of drift outcome. On drift, an additional `composition_drift_detected` event is emitted with the diff payload.
5. REQUIREMENT: `.gzkit/schemas/ledger_events.json` is extended with the two new event type definitions, conforming to the existing event-type schema (id, name, schema, required-fields). The two events are: `composition_rendered` (fields: invariant_count, target, byte_count, render_ts) and `composition_drift_detected` (fields: target, diff_first_50_lines, render_ts).
6. REQUIREMENT: `gz check` (the default pipeline) includes `--invariant-coherence`. The validator scope is added to the canonical scope list so operators get drift detection by default.
7. REQUIREMENT: This OBPI does NOT modify the renderer (OBPI-02) and does NOT introduce brief-reconciliation surfaces (OBPI-05).

> STOP-on-BLOCKERS: if OBPI-02 has not landed (`gz governance render --stdout` missing or non-deterministic), halt — drift detection requires a deterministic producer.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #3 (drift validator) verbatim
- [ ] ADR § Decision Rationale point 1 (foundation requires structural witness) — the "why" the validator exists

**Governance:**

- [ ] `docs/governance/advisory-rules-audit.md` — scorecard conventions (Mechanical / Promotable / Judgment classifications)
- [ ] `.gzkit/rules/governance-core.md` § Proof commands — `gz validate` exit-code convention
- [ ] `src/gzkit/governance/trust_audits/__init__.py` — how scopes are registered

**Prerequisites:**

- [ ] OBPI-01 landed (registry primitive: `load_invariants`, `ConstitutionalInvariant`)
- [ ] OBPI-02 landed (deterministic renderer `render_agents_md`)

**Existing Code:**

- [ ] `src/gzkit/governance/trust_audits/advisor_proof_binding.py` — canonical validator-scope module shape (public `validate_*` fn + private `_` helpers, top-level imports)
- [ ] `src/gzkit/governance/trust_audits/__init__.py` — validator-scope registry (import + `__all__` registration pattern)
- [ ] `src/gzkit/governance/compose.py` — OBPI-02 `render_agents_md(invariants, template_root) -> bytes` consumed by the validator
- [ ] `src/gzkit/governance/invariants.py` — OBPI-01 `load_invariants(root) -> dict[str, ConstitutionalInvariant]`
- [ ] `src/gzkit/ledger_events.py` — event factory pattern (`<name>_event() -> LedgerEvent` with `event=` literal)
- [ ] `src/gzkit/commands/validate_cmd.py` — `default_scopes` dict, `_default_scope_runners`, `_POLICY_BREACH_ERROR_TYPES` (exit-3 routing)
- [ ] `src/gzkit/cli/parser_maintenance.py` — `gz validate` argparse flag registration (`--advisor-proof-binding` precedent)
- [ ] `src/gzkit/governance/trust_audits/events.py` — `audit_event_schemas` (the coupled-surface validator the new events must satisfy)

## Quality Gates

### Gate 1: ADR

- [ ] Drift-validator paragraph quoted

### Gate 2: TDD

- [ ] `test_invariant_coherence.py` covers: match-no-drift, mismatch-drift, registry-load-error, event-emission for both event types
- [ ] Tests pass

### Code Quality

- [ ] Lint, typecheck clean

### Gate 3: Docs (Heavy)

- [ ] `docs/governance/advisory-rules-audit.md` includes a scorecard row for `--invariant-coherence` (classification: Mechanical, fail-closed)
- [ ] If `docs/user/manpages/gz-validate.md` exists, it documents `--invariant-coherence`
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/constitutional_invariants.feature` includes drift-validator scenarios tagged `@REQ-0.0.37-03-*`
- [ ] `behave` passes

### Gate 5: Human

- [ ] Attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_invariant_coherence -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-03

# REQ-03: exit codes
uv run gz validate --invariant-coherence && echo "REQ-03 OK on match"
# (drift case in test)

# REQ-04/05: ledger events registered and emitted
uv run python -c "
import json
events = json.load(open('.gzkit/schemas/ledger_events.json'))
types = {e.get('name') or e.get('id') for e in (events.get('events') or events.get('types') or events.values() if isinstance(events, dict) else events)}
assert 'composition_rendered' in str(events) and 'composition_drift_detected' in str(events), 'event types not registered'
print('REQ-05 OK: event types registered in schema')
"

# REQ-06: scope is part of gz check
uv run gz check --list-scopes 2>&1 | rg -q 'invariant-coherence' && echo "REQ-06 OK: scope included in gz check"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-03-01: `gz validate --invariant-coherence` exits 0 when rendered registry bytes match committed AGENTS.md
- [ ] REQ-0.0.37-03-02: `gz validate --invariant-coherence` exits 3 when bytes differ; output includes a unified diff of the first 50 differing lines
- [ ] REQ-0.0.37-03-03: A clean (matching) run is read-only — no ledger event; a drift run emits a single `composition_drift_detected` ledger event. (Amended 2026-06-23: the original per-invocation `composition_rendered` emission was removed — it had no consumer and, by writing the ledger on every run, broke the `gz check` / pre-push gate this validator now serves. The `composition_rendered` event type stays defined for historical-ledger compatibility but is no longer emitted. ADR-0.0.37 is Draft; OBPI-0.0.37-03 was repudiated — this is in-flight correction, not a closed-contract change.)
- [ ] REQ-0.0.37-03-04: `.gzkit/schemas/ledger_events.json` includes both event type definitions; existing events-schema validator (`gz validate --events` or equivalent) passes
- [ ] REQ-0.0.37-03-05: `gz check` runs `--invariant-coherence` as part of the default scope list
- [ ] REQ-0.0.37-03-06: `docs/governance/advisory-rules-audit.md` lists `--invariant-coherence` with classification Mechanical / fail-closed

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz obpi reconcile OBPI-0.0.37-03-composition-drift-validator` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: hand-edits to AGENTS.md could not be mechanically distinguished from intentional edits. After: any AGENTS.md content not flowing through the registry fails `gz check`. -->

### Key Proof


Drift case — committed AGENTS.md differs from rendered registry: `uv run gz validate --invariant-coherence` exits 3 and prints a unified diff (first 50 lines) of committed vs. rendered AGENTS.md.

ARB receipts (all exit_status=0): arb-ruff-954f16380568456d9fe6d2feca02cf38 (lint clean), arb-step-typecheck-c66836b1981d4557a5fbd46a00cdc294 (typecheck clean), arb-step-unittest-a96b904094ac47b99629e0b6ed8a6007 (5358 tests pass), arb-step-mkdocs-3e633550eb0f473aa5286c6d0e610f37 (docs strict), arb-step-behave-3a8990d943474609924a9a23d1cc80ce (3/3 BDD scenarios). gz covers: 6/6 REQ coverage.

### Implementation Summary


- Files created: src/gzkit/governance/trust_audits/invariant_coherence.py (validator scope), src/gzkit/governance/events.py (ledger emission helpers), .gzkit/schemas/ledger_events.json (per-event-type registry schema), tests/governance/test_invariant_coherence.py (21 tests, 6 classes)
- Files modified: trust_audits/__init__.py, ledger_events.py, events.py, schemas/ledger.json, trust_audits/events.py, validate_cmd.py, parser_maintenance.py, tests/test_schemas.py, features/constitutional_invariants.feature + steps, advisory-rules-audit.md, validate.md, behave_coverage_waivers.json
- Tests added: 21 unit tests + 3 BDD scenarios (@REQ-0.0.37-03-01/02/03)
- Date completed: 2026-05-19
- Attestation status: operator-attested ("attest completed")
- Defects noted: GHI #500 (gz validate --documents 3589 historical-brief schema errors), GHI #501 (events.py module split + frozen=True parity), GHI #502 (agent-insights.jsonl:75 invalid type=discovery); comment added to GHI #486 (utf8_prefix in ADR-pool.artifact-staleness-propagation briefs). _EventBase frozen=True direct-fixed in-flight.

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — composition drift validator gz validate --invariant-coherence wired into gz check default scope, fail-closed exit 3 on AGENTS.md byte-drift from the rendered constitutional invariant registry; composition_rendered/composition_drift_detected ledger events registered. 6/6 REQs covered (21 unit tests + 3 BDD scenarios); full unittest sweep green (5358 tests). ARB receipts: arb-ruff-954f16380568456d9fe6d2feca02cf38, arb-step-typecheck-c66836b1981d4557a5fbd46a00cdc294, arb-step-unittest-a96b904094ac47b99629e0b6ed8a6007, arb-step-mkdocs-3e633550eb0f473aa5286c6d0e610f37, arb-step-behave-3a8990d943474609924a9a23d1cc80ce. Pre-existing failures cleared in-flight (utf8_prefix in ADR-pool.artifact-staleness-propagation briefs; discovery InsightType variant); defects routed to GHI #500/#501/#502/#486.
- Date: 2026-05-20

---

**Brief Status:** Draft

**Date Completed:** 2026-05-20

**Evidence Hash:** -
