---
id: OBPI-0.0.37-03-composition-drift-validator
parent: ADR-0.0.37-constitutional-invariant-composition
item: 3
lane: Heavy
status: Draft
---

<!-- gz-validate-skip: brief-demo-section -->

# OBPI-0.0.37-03-composition-drift-validator: Composition Drift Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #3 — "OBPI-0.0.37-03 — Composition drift validator (`gz validate --invariant-coherence`; fail-closed on drift; `composition_drift_detected` ledger event)"

**Status:** Draft

## Objective

Wire OBPI-02's renderer into the `gz validate` scope catalog as `--invariant-coherence`, fail-closed on byte-drift between rendered registry and committed AGENTS.md, and register the `composition_rendered` / `composition_drift_detected` ledger event types so every render and every drift is a replayable Layer-2 receipt.

## Lane

**Heavy** — Introduces a new validator scope (`--invariant-coherence`), registers new ledger event types, extends the `gz check` default pipeline. Validator-scope and ledger-schema surfaces trigger Heavy.

## Allowed Paths

- `src/gzkit/governance/trust_audits/invariant_coherence.py` (new) — validator scope implementation
- `src/gzkit/governance/trust_audits/__init__.py` (modify) — register the validator in the package registry
- `src/gzkit/governance/events.py` (modify) — register `composition_rendered` and `composition_drift_detected` event types
- `.gzkit/schemas/ledger_events.json` (modify) — extend with the two new event type definitions
- `src/gzkit/commands/validate_cmd.py` (modify) OR wherever `gz validate` flag-dispatch lives — wire `--invariant-coherence` flag
- `tests/governance/test_invariant_coherence.py` (new) — REQ-derived validator assertions
- `tests/fixtures/invariant_coherence/` (new) — fixture registries + AGENTS.md pairs (matching, drifted)
- `features/constitutional_invariants.feature` (modify) — add drift-validator scenarios tagged `@REQ-0.0.37-03-*`; file created by OBPI-02
- `docs/governance/advisory-rules-audit.md` (modify) — add scorecard entry for the new validator scope
- `docs/user/manpages/gz-validate.md` (modify, if exists) — add `--invariant-coherence` flag documentation
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

**Context (exemplars):**

- [ ] `src/gzkit/governance/trust_audits/advisor_proof_binding.py` — example of a validator-scope module shape
- [ ] `src/gzkit/governance/trust_audits/distribution.py` — another validator-scope example
- [ ] `src/gzkit/governance/events.py` — event-registration pattern

**Prerequisites:**

- [ ] OBPI-01 landed (registry primitive)
- [ ] OBPI-02 landed (deterministic renderer with `--stdout`)
- [ ] `src/gzkit/governance/events.py` exists and exposes event-registration API

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
- [ ] REQ-0.0.37-03-03: Each invocation emits a `composition_rendered` ledger event with (invariant_count, target, byte_count, render_ts); drift case additionally emits `composition_drift_detected`
- [ ] REQ-0.0.37-03-04: `.gzkit/schemas/ledger_events.json` includes both event type definitions; existing events-schema validator (`gz validate --events` or equivalent) passes
- [ ] REQ-0.0.37-03-05: `gz check` runs `--invariant-coherence` as part of the default scope list
- [ ] REQ-0.0.37-03-06: `docs/governance/advisory-rules-audit.md` lists `--invariant-coherence` with classification Mechanical / fail-closed

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-03-composition-drift-validator` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: hand-edits to AGENTS.md could not be mechanically distinguished from intentional edits. After: any AGENTS.md content not flowing through the registry fails `gz check`. -->

### Key Proof

<!-- A drift case: edit AGENTS.md, run `gz validate --invariant-coherence`, observe exit 3 + diff. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>`
- Attestation: per ADR-0.0.36 universal Gate 5
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
