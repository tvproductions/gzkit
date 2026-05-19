---
id: OBPI-0.0.37-08-obpi-complete-gate
parent: ADR-0.0.37-constitutional-invariant-composition
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.37-08-obpi-complete-gate: OBPI Complete Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #8 — "OBPI-0.0.37-08 — `gz obpi complete` fail-close gate (refuses Stage 5 completion without fresh reconciliation receipt; `--accept-stale-reconciliation --reason` escape hatch records override)"

**Status:** Draft

## Objective

Extend `gz obpi complete` (Stage 5) to refuse completion when the active OBPI lacks a fresh `brief_reconciled` receipt. Provide a fail-loud-not-bypass escape hatch `--accept-stale-reconciliation --reason "<text>"` modeled on `--accept-uncovered` (ADR-0.0.25) that records the override as a `brief_reconcile_drift_overridden` ledger event for later operator review. This is the in-flight-drift-catching half of CIC-2.

## Lane

**Heavy** — Modifies completion-time behavior (a runtime contract surface), introduces a new escape-hatch flag, registers a new ledger event type. CLI/runtime/schema surfaces.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py` (modify) — Stage 5 reconciliation gate + escape hatch
- `src/gzkit/governance/events.py` (modify) — register `brief_reconcile_drift_overridden` event type
- `.gzkit/schemas/ledger_events.json` (modify) — schema definition for the new event type
- `tests/commands/test_obpi_complete.py` (modify or new test file `test_obpi_complete_reconcile_gate.py`) — Stage 5 gate tests + escape-hatch tests
- `docs/user/manpages/gz-obpi.md` (modify, if exists) — document `--accept-stale-reconciliation` flag
- `features/brief_reconcile.feature` (modify) — add Stage 5 + escape-hatch scenarios tagged `@REQ-0.0.37-08-*`; file created by OBPI-05
- `docs/user/runbook.md` (modify) — operator runbook entry: "2am Stage 5 escape: `--accept-stale-reconciliation --reason \"<text>\"` records override to ledger; never silent"
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-08-obpi-complete-gate.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- Stage 1 (`pipeline_runtime.py` — OBPI-07)
- Reconcile engine / CLI (OBPI-04/05/06 — consume)
- `src/gzkit/governance/reconcile_freshness.py` (OBPI-07's helper — consume)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz obpi complete <OBPI-ID>` queries the ledger for the most recent `brief_reconciled` receipt for the active OBPI. If absent, completion fail-closes (exit 3) with message: "Completion blocked: no `brief_reconciled` receipt for <OBPI-ID>. Run `gz brief reconcile <OBPI-ID>` then retry."
2. REQUIREMENT: If receipt exists, use OBPI-07's `is_receipt_fresh` to check freshness against the brief's Allowed Paths. If stale, completion fail-closes (exit 3) with message naming the drifted path.
3. REQUIREMENT: If receipt is fresh but `has_drift` payload is True, completion fail-closes (exit 3) with message naming the drifted dimensions.
4. REQUIREMENT: Escape hatch `--accept-stale-reconciliation --reason "<text>"` accepts the stale-or-drifted receipt. Without `--reason`, the flag fails with argparse error "--accept-stale-reconciliation requires --reason '<text>'". `--reason` text MUST be non-empty (at least 10 characters); a shorter reason rejected at argparse.
5. REQUIREMENT: When the escape hatch is invoked, a `brief_reconcile_drift_overridden` ledger event is emitted BEFORE the completion event. Payload: (brief_id, override_ts, attestor, reason, original_receipt_id, original_drift_dimensions). Existing completion event then emits as normal.
6. REQUIREMENT: The escape hatch is universal (works on every lane — lite, heavy; every kind — foundation, feature, pool). Lane-based access control is the wrong axis per ADR § Alternatives Considered #8. The audit-trail (ledger event) is the structural defense, not lane gating.
7. REQUIREMENT: New event type `brief_reconcile_drift_overridden` registered in `.gzkit/schemas/ledger_events.json` per existing events-schema conventions.
8. REQUIREMENT: This OBPI does NOT modify Stage 1 (OBPI-07's surface); does NOT register `brief_reconciled` / `brief_reconcile_drift_detected` (OBPI-06's surface).

> STOP-on-BLOCKERS: OBPI-06/07 must be landed.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #8 (Stage 5 gate + escape hatch) verbatim
- [ ] ADR § Consequences Negative #9 — the 2am operator scenario justifying the escape hatch
- [ ] ADR § Alternatives Considered #8 — why the escape hatch is lane-independent

**Governance:**

- [ ] ADR-0.0.25 — `--accept-uncovered` is the parallel pattern; reuse the shape (`--accept-X --reason "<text>"`)
- [ ] `.gzkit/rules/governance-core.md` § Non-negotiable rules — "Do not edit the ledger manually"; the escape hatch writes through the proper event-emission API

**Context (exemplars):**

- [ ] `src/gzkit/commands/obpi_complete.py` — current Stage 5 implementation
- [ ] `src/gzkit/commands/obpi_complete.py` `--accept-uncovered --accept-uncovered-reason` flag (ADR-0.0.25 implementation) — the exact pattern to mirror

**Prerequisites:**

- [ ] OBPI-06 (event types registered) + OBPI-07 (freshness helper) landed
- [ ] `src/gzkit/commands/obpi_complete.py` exposes its argparse subparser for flag addition

## Quality Gates

- [ ] Gate 1: Stage-5-gate paragraph quoted
- [ ] Gate 2: Tests for: missing receipt fail-close, stale receipt fail-close, fresh-drifted fail-close, fresh-clean pass, escape-hatch without --reason error, escape-hatch with --reason emits override event then completes (6 cases); RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: Manpage update; runbook entry on 2am escape; mkdocs strict
- [ ] Gate 4: `features/brief_reconcile.feature` includes Stage 5 + escape-hatch scenarios tagged `@REQ-0.0.37-08-*`; behave passes
- [ ] Gate 5: Foundation-kind attestation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_obpi_complete -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-08

# REQ-04: --accept-stale-reconciliation requires --reason
uv run gz obpi complete OBPI-0.0.37-08-obpi-complete-gate --accept-stale-reconciliation 2>&1 | rg -q "requires --reason" && echo "REQ-04 OK"

# REQ-07: event type registered
uv run python -c "
events_txt = open('.gzkit/schemas/ledger_events.json').read()
assert 'brief_reconcile_drift_overridden' in events_txt
print('REQ-07 OK')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-08-01: `gz obpi complete <OBPI-ID>` fail-closes (exit 3) when no `brief_reconciled` receipt exists for the active OBPI; error message names the missing-receipt remedy
- [ ] REQ-0.0.37-08-02: Stage 5 fail-closes (exit 3) when the most recent `brief_reconciled` receipt is stale per OBPI-07's `is_receipt_fresh`
- [ ] REQ-0.0.37-08-03: Stage 5 fail-closes (exit 3) when a fresh receipt's `has_drift` payload is True
- [ ] REQ-0.0.37-08-04: `--accept-stale-reconciliation` without `--reason "<text>"` exits with argparse error containing `--accept-stale-reconciliation requires --reason`
- [ ] REQ-0.0.37-08-05: `--accept-stale-reconciliation --reason "<text>"` (with text length >= 10) emits a `brief_reconcile_drift_overridden` ledger event (attestor, reason, original_receipt_id, original_drift_dimensions) BEFORE the completion event, then completes normally
- [ ] REQ-0.0.37-08-06: The escape hatch works regardless of lane/kind/sensitivity — no lane-based access control
- [ ] REQ-0.0.37-08-07: `brief_reconcile_drift_overridden` event type schema registered in `.gzkit/schemas/ledger_events.json`

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-08-obpi-complete-gate` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: an OBPI could complete with a stale brief whose Allowed Paths had drifted since reconciliation. After: Stage 5 fail-closes; escape hatch is loud, attested, and ledger-witnessed. -->

### Key Proof

<!-- Demonstrate: stale-receipt fail-close + escape-hatch override emitting `brief_reconcile_drift_overridden` event with non-empty reason. -->

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
- Attestation: substantive text grounded in escape-hatch event-emission demonstration
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
